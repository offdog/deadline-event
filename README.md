# Deadline Custom Event Plugins

Custom event plugins for Thinkbox Deadline render farm.

---

## Plugins

### MayaOCIOFix

แก้ไข `OCIOConfigFile` ใน job plugin info ตอน submit โดยแทนที่ token `<MAYA_RESOURCES>` ด้วย path จริงของ Maya resources และสามารถ override Arnold `abortOnError` ได้

**ปัญหาที่แก้:** Maya 2025+ ส่ง `OCIOConfigFile` มาในรูป `<MAYA_RESOURCES>/OCIO-configs/...` แต่ Deadline worker ไม่รู้จัก token นี้ → render fail

**Triggers:** `OnJobSubmitted` — เฉพาะ plugin `MayaBatch` และ `MayaCmd`

#### Configuration (Deadline Monitor → Tools → Configure Event Plugins → MayaOCIOFix)

| Field | Default | Description |
|---|---|---|
| Event State | Global Enabled | เปิด/ปิด plugin |
| Maya Version | `2025` | Version ที่ต้องการจัดการ คั่นด้วย comma (เช่น `2025,2026`) |
| Maya Install Base Path | `C:/Program Files/Autodesk` | Base path ของ Autodesk — ต่อท้ายด้วย `/Maya{version}/resources` อัตโนมัติ |
| Abort On Error | `Disable` | Override Arnold abortOnError ตอน submit (`Unchanged` = ไม่แตะ) |

#### ตัวอย่าง

OCIOConfigFile ก่อนแก้:
```
<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio
```

OCIOConfigFile หลังแก้ (Maya Version = `2025`, Base Path = `C:/Program Files/Autodesk`):
```
C:/Program Files/Autodesk/Maya2025/resources/OCIO-configs/Maya2022-default/config.ocio
```

---

### UsersSuspendJob

Suspend job อัตโนมัติทันทีที่ submit สำหรับ user ที่กำหนด เหมาะสำหรับ user ที่ต้องรอ approval ก่อน render

**Triggers:** `OnJobSubmitted` — ทุก plugin

#### Configuration

| Field | Default | Description |
|---|---|---|
| Event State | Global Enabled | เปิด/ปิด plugin |
| Suspend Users | `dvisual` | Username คั่นด้วย comma (case-insensitive) |

---

## Deploy

1. Copy plugin folder ไปที่ Deadline Repository:
   ```
   <DeadlineRepository>/custom/events/MayaOCIOFix/
   <DeadlineRepository>/custom/events/UsersSuspendJob/
   ```

2. เปิด Deadline Monitor → **Tools → Configure Event Plugins**

3. ตั้งค่า plugin แต่ละตัว แล้ว Save

4. ดู log ได้ใน Deadline Monitor → **View → Logs → Event Logs**

---

## Requirements

- Thinkbox Deadline 10+
- Maya (MayaBatch / MayaCmd) plugin
- Arnold renderer (สำหรับ AbortOnError feature)
