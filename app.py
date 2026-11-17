"""Lab 03 · BJT DC Bias Web App

เว็บ Flask ที่เลือกวงจรไบอัสได้สามแบบ (Voltage Divider / Fixed / Emitter)
ทำหน้าที่ตรวจอินพุต แปลงหน่วย แล้วเรียกฟังก์ชันใน dc_bias.py
"""

from __future__ import annotations

import math

from flask import Flask, render_template, request

import dc_bias

app = Flask(__name__)

# ตัวต้านทานที่อยู่ในฟอร์มใช้หน่วย kΩ ทั้งหมด แปลงเป็น Ω ครั้งเดียวตอนรับข้อมูล
KILO = 1000.0

MODES: dict[str, dict] = {
    "divider": {
        "label": "Voltage Divider Bias",
        "summary": "R1 จาก VCC ไป Base · R2 จาก Base ลงกราวด์ · RE จาก Emitter ลงกราวด์",
        "resistors": [
            {"key": "r1", "label": "R1"},
            {"key": "r2", "label": "R2"},
            {"key": "re", "label": "RE"},
        ],
    },
    "fixed": {
        "label": "Fixed Bias",
        "summary": "RB จาก VCC ไป Base · Emitter ต่อลงกราวด์โดยตรง",
        "resistors": [
            {"key": "rb", "label": "RB"},
        ],
    },
    "emitter": {
        "label": "Emitter Bias",
        "summary": "RB จาก VCC ไป Base · RE จาก Emitter ลงกราวด์",
        "resistors": [
            {"key": "rb", "label": "RB"},
            {"key": "re", "label": "RE"},
        ],
    },
}

COMMON_FIELDS = [
    {"key": "vcc", "label": "VCC", "unit": "V", "value": "12"},
    {"key": "rc", "label": "RC", "unit": "kΩ", "value": "2.2"},
    {"key": "beta", "label": "β", "unit": "", "value": "100"},
    {"key": "vbe", "label": "VBE", "unit": "V", "value": "0.70"},
]


class InputError(Exception):
    """ข้อผิดพลาดจากข้อมูลที่ผู้ใช้กรอก (ไม่ใช่ข้อผิดพลาดของแบบจำลอง)"""


def _read_number(form, key: str, label: str, unit: str) -> float:
    raw = (form.get(key) or "").strip()
    where = f"{label} ({unit})" if unit else label

    if not raw:
        raise InputError(f"กรอก {where} ให้ครบ")
    try:
        value = float(raw)
    except ValueError:
        raise InputError(f"{where} ต้องเป็นตัวเลข")
    if not math.isfinite(value):
        raise InputError(f"{where} ต้องเป็นจำนวนจำกัด")
    if value <= 0:
        raise InputError(f"{where} ต้องมากกว่า 0")
    return value


def _collect_values(form, mode: str) -> dict[str, float]:
    """อ่านเฉพาะช่องที่โหมดนั้นต้องใช้ แล้วคืนค่าที่แปลงหน่วยเป็น Ω/V แล้ว"""
    values: dict[str, float] = {}
    values["vcc_v"] = _read_number(form, "vcc", "VCC", "V")
    values["rc_ohm"] = _read_number(form, "rc", "RC", "kΩ") * KILO
    values["beta"] = _read_number(form, "beta", "β", "")
    values["vbe_v"] = _read_number(form, "vbe", "VBE", "V")

    for field in MODES[mode]["resistors"]:
        key, label = field["key"], field["label"]
        values[f"{key}_ohm"] = _read_number(form, key, label, "kΩ") * KILO

    return values


def _calculate(mode: str, v: dict[str, float]) -> dict:
    if mode == "fixed":
        return dc_bias.fixed_bias(
            vcc_v=v["vcc_v"],
            rb_ohm=v["rb_ohm"],
            rc_ohm=v["rc_ohm"],
            beta=v["beta"],
            vbe_v=v["vbe_v"],
        )
    if mode == "emitter":
        return dc_bias.emitter_bias(
            vcc_v=v["vcc_v"],
            rb_ohm=v["rb_ohm"],
            rc_ohm=v["rc_ohm"],
            re_ohm=v["re_ohm"],
            beta=v["beta"],
            vbe_v=v["vbe_v"],
        )
    if mode == "divider":
        return dc_bias.voltage_divider_bias(
            vcc_v=v["vcc_v"],
            r1_ohm=v["r1_ohm"],
            r2_ohm=v["r2_ohm"],
            rc_ohm=v["rc_ohm"],
            re_ohm=v["re_ohm"],
            beta=v["beta"],
            vbe_v=v["vbe_v"],
        )
    raise InputError(f"ไม่รู้จักโหมดวงจร “{mode}” — ต้องเป็น divider, fixed หรือ emitter")


def _raw_values(form) -> dict[str, str]:
    keys = [f["key"] for f in COMMON_FIELDS] + ["r1", "r2", "re", "rb"]
    return {key: form.get(key, "") for key in keys}


def _render(mode: str, values: dict[str, str], result=None, errors=None, status: int = 200):
    return (
        render_template(
            "index.html",
            modes=MODES,
            mode=mode,
            mode_info=MODES.get(mode),
            common_fields=COMMON_FIELDS,
            values=values,
            result=result,
            errors=errors or [],
        ),
        status,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        default_mode = request.args.get("mode", "divider")
        if default_mode not in MODES:
            default_mode = "divider"
        return _render(default_mode, {})

    form = request.form
    mode = form.get("mode", "")
    values = _raw_values(form)

    if mode not in MODES:
        return _render(
            "divider",
            values,
            errors=[f"ไม่รู้จักโหมดวงจร “{mode}” — ต้องเป็น divider, fixed หรือ emitter"],
            status=400,
        )

    try:
        parsed = _collect_values(form, mode)
        result = _calculate(mode, parsed)
    except InputError as exc:
        return _render(mode, values, errors=[str(exc)], status=400)

    return _render(mode, values, result=result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
