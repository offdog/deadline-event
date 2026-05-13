# Deadline Custom Event Plugins

Custom event plugins for Thinkbox Deadline render farm.

---

## Plugins

### MayaOCIOFix

แก้ไข `OCIOConfigFile` ใน job plugin info ตอน submit โดยแทนที่ token `<MAYA_RESOURCES>` ด้วย path จริงของ Maya resources และสามารถ override Arnold `abortOnError` ได้

**ปัญหาที่แก้:** Maya 2025+ ส่ง `OCIOConfigFile` มาในรูป `<MAYA_RESOURCES>/OCIO-configs/...` แต่ Deadline worker ไม่รู้จัก token นี้ → render fail

**Triggers:** `OnJobSubmitted` — เฉพาะ plugin `MayaBatch` และ `MayaCmd`

#### Configuration

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

### SetJobTimeout

ตั้งค่า timeout ของ task อัตโนมัติตอน submit เหมาะสำหรับป้องกัน task ค้างนานเกินไป

**Triggers:** `OnJobSubmitted` — เฉพาะ plugin ที่อยู่ใน `AllowedSoftware`

#### Configuration

| Field | Default | Description |
|---|---|---|
| Event State | Disabled | เปิด/ปิด plugin |
| Allowed Software | `MayaBatch,MayaCmd,CommandLine` | Plugin name ที่ต้องการจัดการ คั่นด้วย comma |
| Max Hours/Minutes/Seconds | `0` | Maximum render time per task (0 = ไม่จำกัด) |
| Min Hours/Minutes/Seconds | `0h 0m 5s` | Minimum render time ก่อนที่จะถือว่า timeout |
| On Task Timeout | `Requeue` | Action เมื่อ timeout: Error / Notify / Requeue / Fail / Complete |

---

### SetMachineLimit

ปรับ `MachineLimitMaximum` อัตโนมัติตาม load ของ farm — จำกัด worker ของ job priority ต่ำเมื่อ farm ยุ่ง

**Triggers:** `OnJobSubmitted`, `OnJobStarted`, `OnJobResumed`, `OnJobRequeued`

#### Logic

| เงื่อนไข | ผลลัพธ์ |
|---|---|
| active jobs > threshold **และ** priority > threshold | ตั้ง MachineLimitMaximum = High value |
| active jobs > threshold **และ** priority ≤ threshold | ตั้ง MachineLimitMaximum = 0 (unlimited) |
| active jobs ≤ threshold | ตั้ง MachineLimitMaximum = 0 (unlimited) |

#### Configuration

| Field | Default | Description |
|---|---|---|
| Event State | Disabled | เปิด/ปิด plugin |
| Active Job Threshold | `10` | จำนวน active job ที่ถือว่า farm ยุ่ง |
| Job Priority Threshold | `50` | Priority ที่แบ่ง high/low priority |
| Machine Limit Maximum (High Priority) | `35` | จำนวน worker สูงสุดสำหรับ high priority job |

---

### UnmapAllDrive

Unmap network drive ทั้งหมดบน worker อัตโนมัติ เพื่อป้องกัน drive letter ค้างหลัง render

**Triggers:** Worker events — `OnSlaveIdle`, `OnSlaveStopped`, `OnSlaveStalled`, `OnMachineRestart`

#### Configuration

| Field | Default | Description |
|---|---|---|
| Event State | Disabled | เปิด/ปิด plugin |
| User Filter | `myrender,renderman,mydeadline` | Username ที่ต้องการ unmap — ใช้ `*` สำหรับทุก user, เว้นว่าง = ไม่ทำงาน |

---

### NukeCleanup

ลบไฟล์ `.tmp` ใน output directory ของ Nuke job อัตโนมัติ ป้องกัน temp file สะสมบน storage

**Triggers:** `OnSlaveStartingJob` และ/หรือ `OnJobFinished` — เฉพาะ job ที่ PluginName มีคำว่า `Nuke`

#### Configuration

| Field | Default | Description |
|---|---|---|
| Event State | Disabled | เปิด/ปิด plugin |
| Perform Nuke .tmp File Cleanup | `On Job Finished` | เวลาที่ทำการลบ: ก่อน render / หลัง render / ทั้งสองอย่าง |

---

### SetJobsEnv

Inject environment variable เข้าไปใน job ตอน submit เหมาะสำหรับ set ค่า env เช่น `OCIO`, `PYTHONPATH` ให้ทุก job โดยไม่ต้องแก้ที่ submitter

**Triggers:** `OnJobSubmitted` — ทุก plugin

#### Configuration

| Field | Default | Description |
|---|---|---|
| Event State | Disabled | เปิด/ปิด plugin |
| Environment Keys | _(ว่าง)_ | `KEY=VALUE` คั่นด้วย `;` เช่น `OCIO=/path/config.ocio;MY_VAR=1` |

---

## Deploy

1. Copy plugin folder ไปที่ Deadline Repository:
   ```
   <DeadlineRepository>/custom/events/MayaOCIOFix/
   <DeadlineRepository>/custom/events/UsersSuspendJob/
   <DeadlineRepository>/custom/events/SetJobTimeout/
   <DeadlineRepository>/custom/events/SetMachineLimit/
   <DeadlineRepository>/custom/events/UnmapAllDrive/
   <DeadlineRepository>/custom/events/NukeCleanup/
   <DeadlineRepository>/custom/events/SetJobsEnv/
   ```

2. เปิด Deadline Monitor → **Tools → Configure Event Plugins**

3. ตั้งค่า plugin แต่ละตัว แล้ว Save

4. ดู log ได้ใน Deadline Monitor → **View → Logs → Event Logs**

---

## Requirements

- Thinkbox Deadline 10+
- Maya (MayaBatch / MayaCmd) plugin — สำหรับ MayaOCIOFix, SetJobTimeout
- Arnold renderer — สำหรับ AbortOnError feature ใน MayaOCIOFix
