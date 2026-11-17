# DC Circuit Calculator — BJT Bias Web App

เว็บ Flask สำหรับคำนวณ DC Operating Point ของวงจรไบอัส BJT แบบ NPN Common Emitter
เลือกได้สามวงจร: **Voltage Divider Bias**, **Fixed Bias** และ **Emitter Bias**
(งาน Lab 03 รายวิชา ENG29 2121)

## ไฟล์ในโปรเจกต์

| ไฟล์ | หน้าที่ |
| --- | --- |
| `app.py` | เส้นทาง Flask, ตรวจอินพุต, แปลงหน่วย kΩ → Ω, เลือกฟังก์ชันตามโหมด |
| `dc_bias.py` | สมการของทั้งสามวงจร คืนผลเป็น dict ที่ใช้คีย์และหน่วยร่วมกัน |
| `templates/index.html` | ฟอร์มเลือกโหมด กรอกค่า และแสดงผล |
| `requirements.txt` | Flask |

## วิธีรัน

```powershell
# ติดตั้ง dependencies (ครั้งแรกครั้งเดียว)
"C:\Program Files\Python314\python.exe" -m pip install -r requirements.txt

# รันเซิร์ฟเวอร์ที่พอร์ต 5000
"C:\Program Files\Python314\python.exe" -m flask --app app run --port 5000
```

เปิด <http://127.0.0.1:5000/>

## หน่วยที่ใช้

- ฟอร์มรับตัวต้านทานเป็น **kΩ** ทั้งหมด (1 MΩ = 1,000 kΩ) และแปลงเป็น Ω ครั้งเดียวใน `app.py`
- β ไม่มีหน่วย, VCC / VBE เป็นโวลต์
- ผลลัพธ์: VB, VE, VC, VCE เป็น V · IB เป็น µA · IC / IE เป็น mA

## สมการ

| โหมด | IB |
| --- | --- |
| Fixed | `(VCC − VBE) / RB` |
| Emitter | `(VCC − VBE) / [RB + (β+1)RE]` |
| Voltage Divider | `(VTH − VBE) / [RTH + (β+1)RE]` โดย `VTH = VCC·R2/(R1+R2)` และ `RTH = R1·R2/(R1+R2)` |

จาก IB: `IC = β·IB`, `IE = (β+1)·IB`, `VE = IE·RE` (Fixed ใช้ `VE = 0`),
`VB = VE + VBE`, `VC = VCC − IC·RC`, `VCE = VC − VE`

## การตรวจอินพุต

- ช่องที่โหมดนั้นไม่ใช้จะไม่ถูกตรวจและไม่ถูกอ่าน
- ค่าว่าง, ไม่ใช่ตัวเลข, ไม่เป็นจำนวนจำกัด หรือ ≤ 0 → แสดงข้อผิดพลาด ไม่คำนวณ
- โหมดที่ไม่รู้จัก → ข้อผิดพลาด (ไม่เดาเป็น Voltage Divider)
- อินพุตถูกต้องแต่ `IB ≤ 0` หรือ `VCE ≤ 0.2 V` → แสดงคำเตือนว่าแบบจำลอง Forward Active อาจใช้ไม่ได้

## ค่าตรวจรับ (VCC = 12 V, RC = 2.2 kΩ, β = 100, VBE = 0.70 V)

| กรณี | อินพุต | IC (mA) | VCE (V) |
| --- | --- | --- | --- |
| A1 Divider | R1 = 100 kΩ, R2 = 22 kΩ, RE = 1 kΩ | 1.230 | 8.052 |
| A2 Fixed | RB = 1 MΩ (1000 kΩ) | 1.130 | 9.514 |
| A3 Emitter | RB = 1 MΩ, RE = 1 kΩ | 1.026 | 8.706 |
| A4 Emitter | RB = 1 MΩ, RE = 2 kΩ | 0.940 | 8.033 |
| A5 Fixed | RB = 0 | ข้อผิดพลาดที่ช่อง RB | — |

A4 ได้ IC น้อยกว่า A3 เพราะ RE มากขึ้นทำให้กระแสฐานและกระแสคอลเลกเตอร์ลดลง
