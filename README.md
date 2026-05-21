# Deadline Custom Event Plugins

Custom event plugins for Thinkbox Deadline render farm.

---

## Plugins

### MayaOCIOFix

แก้ไข `OCIOConfigFile` ใน job plugin info ตอน submit โดยแทนที่ token `<MAYA_RESOURCES>` ด้วย path จริงของ Maya resources และสามารถ override Arnold `abortOnError` ได้

**ปัญหาที่แก้:** Maya 2025+ ส่ง `OCIOConfigFile` มาในรูป `<MAYA_RESOURCES>/OCIO-configs/...` แต่ Deadline worker ไม่รู้จัก token นี้ → render fail

**Triggers:** `OnJobSubmitted` — เฉพาะ plugin `MayaBatch` และ `MayaCmd`

> **หมายเหตุ:** OCIO patch และ AbortOnError ทำงานอิสระต่อกัน — `AbortOnError` จะถูก apply เสมอสำหรับทุก job ที่ Maya version ตรงกับ config ไม่ว่าจะมี `<MAYA_RESOURCES>` ใน OCIOConfigFile หรือไม่ก็ตาม

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

### PPIstartup

Inject `userSetup.mel` ของ PPI studio เข้า Maya job อัตโนมัติตอน submit และกำหนด output path แบบ auto-increment rev

**Triggers:** `OnJobSubmitted` — เฉพาะ plugin `MayaBatch` และ `MayaCmd` ที่ชื่อ job ขึ้นต้นด้วย prefix ที่กำหนด (รองรับสูงสุด 3 entries)

#### Logic

1. Loop entries 1–3: หา prefix แรกที่ match ชื่อ job (first match wins) — ถ้าไม่ match เลย → skip
2. เพิ่ม directory ของ `userSetup.mel` (จาก MEL Path ที่ match) เข้า `MAYA_SCRIPT_PATH` — Maya จะ auto-source `userSetup.mel` จาก directory นั้นตอน startup
3. กำหนด `OutputFilePath` เป็น `{ProjectPath}/render/{SceneName}/rev####/` โดย scan folder จริงแล้ว auto-increment rev

> **หมายเหตุ:** `OutputDirectory0` (แสดงใน Deadline Monitor) ไม่สามารถเปลี่ยนได้จาก event plugin — เป็น limitation ของ Deadline API แต่ `OutputFilePath` ที่ใช้เป็น `-rd` flag จริงใน MayaCmd ถูกต้อง

#### Configuration

| Field | Default | Description |
|---|---|---|
| Event State | Global Enabled | เปิด/ปิด plugin |
| Prefix 1 | `JJK` | Job name prefix #1 (case-sensitive) — เว้นว่างเพื่อ disable |
| UserSetup MEL Path 1 | `M:/_tech/mayaScript/ppi/jjk/startup/userSetup.mel` | Path ไปยัง `userSetup.mel` สำหรับ Prefix 1 |
| Prefix 2 | _(ว่าง)_ | Job name prefix #2 — เว้นว่างเพื่อ disable |
| UserSetup MEL Path 2 | _(ว่าง)_ | Path ไปยัง `userSetup.mel` สำหรับ Prefix 2 |
| Prefix 3 | _(ว่าง)_ | Job name prefix #3 — เว้นว่างเพื่อ disable |
| UserSetup MEL Path 3 | _(ว่าง)_ | Path ไปยัง `userSetup.mel` สำหรับ Prefix 3 |

#### ตัวอย่าง Output Path

Job มี `ProjectPath = M:/JJK`, `SceneFile = shot010.ma`:
- Submit ครั้งแรก (ยังไม่มี rev) → `OutputFilePath = M:/JJK/render/shot010/rev0001`
- Submit อีกครั้ง (มี rev0001 อยู่แล้ว) → `OutputFilePath = M:/JJK/render/shot010/rev0002`

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
   <DeadlineRepository>/custom/events/PPIstartup/
   ```

2. เปิด Deadline Monitor → **Tools → Configure Event Plugins**

3. ตั้งค่า plugin แต่ละตัว แล้ว Save

4. ดู log ได้ใน Deadline Monitor → **View → Logs → Event Logs**

---

## Notes

- ทุก section ใน `.param` file ต้องมี `Type=` — ถ้าขาดจะเกิด warning ตอน Deadline โหลด plugin
- `[About]` ใช้ `Type=Label` + `Default=` สำหรับ read-only display text (`Value=` ไม่ถูก recognize)

## Requirements

- Thinkbox Deadline 10+
- Maya (MayaBatch / MayaCmd) plugin — สำหรับ MayaOCIOFix, SetJobTimeout
- Arnold renderer — สำหรับ AbortOnError feature ใน MayaOCIOFix
