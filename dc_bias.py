"""โมดูลคำนวณ DC Operating Point ของวงจรไบอัส BJT (NPN Common Emitter)

ทุกฟังก์ชันรับค่าความต้านทานเป็นโอห์ม กระแสเป็นแอมแปร์ และแรงดันเป็นโวลต์
แล้วคืนผลลัพธ์เป็น dict ที่ใช้ชื่อคีย์และหน่วยร่วมกันทั้งสามวงจร

แบบจำลอง: beta และ VBE คงที่ในย่าน Forward Active (DC โดยประมาณ)
"""

from __future__ import annotations

VCE_MIN_FORWARD_ACTIVE = 0.2  # V


def _model_warning(ib_a: float, vce_v: float) -> str | None:
    """เตือนเมื่อค่าที่คำนวณได้อยู่นอกย่าน Forward Active (ไม่ใช่ข้อผิดพลาดอินพุต)"""
    problems: list[str] = []
    if ib_a <= 0:
        problems.append("IB ที่คำนวณได้ ≤ 0 A วงจรอาจอยู่ในย่าน Cutoff")
    if vce_v <= VCE_MIN_FORWARD_ACTIVE:
        problems.append(
            f"VCE ที่คำนวณได้ ≤ {VCE_MIN_FORWARD_ACTIVE} V วงจรอาจอยู่ในย่าน Saturation"
        )
    if not problems:
        return None
    return " ; ".join(problems) + " — แบบจำลอง Forward Active อาจใช้ไม่ได้"


def _operating_point(
    ib_a: float,
    beta: float,
    rc_ohm: float,
    re_ohm: float,
    vcc_v: float,
    vbe_v: float,
) -> dict[str, float | str | None]:
    """คำนวณค่ากระแสและแรงดันที่เหลือจาก IB (สมการชุดเดียวใช้ร่วมกันทั้งสามโหมด)"""
    ic_a = beta * ib_a
    ie_a = (beta + 1.0) * ib_a

    ve_v = ie_a * re_ohm
    vb_v = ve_v + vbe_v
    vc_v = vcc_v - ic_a * rc_ohm
    vce_v = vc_v - ve_v

    return {
        "ib_ua": ib_a * 1e6,
        "ic_ma": ic_a * 1e3,
        "ie_ma": ie_a * 1e3,
        "vb_v": vb_v,
        "ve_v": ve_v,
        "vc_v": vc_v,
        "vce_v": vce_v,
        "warning": _model_warning(ib_a, vce_v),
    }


def fixed_bias(
    vcc_v: float, rb_ohm: float, rc_ohm: float, beta: float, vbe_v: float
) -> dict[str, float | str | None]:
    """Fixed Bias: RB จาก VCC ไป Base, Emitter ต่อลงกราวด์โดยตรง (VE = 0 V)"""
    ib_a = (vcc_v - vbe_v) / rb_ohm
    return _operating_point(ib_a, beta, rc_ohm, 0.0, vcc_v, vbe_v)


def emitter_bias(
    vcc_v: float,
    rb_ohm: float,
    rc_ohm: float,
    re_ohm: float,
    beta: float,
    vbe_v: float,
) -> dict[str, float | str | None]:
    """Emitter Bias: RB จาก VCC ไป Base และ RE จาก Emitter ลงกราวด์"""
    ib_a = (vcc_v - vbe_v) / (rb_ohm + (beta + 1.0) * re_ohm)
    return _operating_point(ib_a, beta, rc_ohm, re_ohm, vcc_v, vbe_v)


def voltage_divider_bias(
    vcc_v: float,
    r1_ohm: float,
    r2_ohm: float,
    rc_ohm: float,
    re_ohm: float,
    beta: float,
    vbe_v: float,
) -> dict[str, float | str | None]:
    """Voltage Divider Bias: R1 จาก VCC ไป Base, R2 จาก Base ลงกราวด์, RE จาก Emitter ลงกราวด์"""
    vth_v = vcc_v * r2_ohm / (r1_ohm + r2_ohm)
    rth_ohm = r1_ohm * r2_ohm / (r1_ohm + r2_ohm)

    ib_a = (vth_v - vbe_v) / (rth_ohm + (beta + 1.0) * re_ohm)
    result = _operating_point(ib_a, beta, rc_ohm, re_ohm, vcc_v, vbe_v)
    result["vth_v"] = vth_v
    result["rth_ohm"] = rth_ohm
    return result
