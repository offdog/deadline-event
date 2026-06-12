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

**Triggers:** `OnJobSubmitted` — เฉพาะ plugin `MayaBatch` และ `MayaCmd` ที่มี job extra info `Pipeline=ppi`

#### Logic

1. `SubmitMayaToDeadline.mel` อ่าน `ppi_projects.txt` จาก folder เดียวกัน แล้ว detect project code จาก `ProjectPath`
2. Submitter เขียน debug marker `ExtraInfoKeyValue6=PPISubmitterVersion=2026-06-13-v3`
3. ถ้า match จะเขียน `ExtraInfoKeyValue7=Pipeline=ppi` และ `ExtraInfoKeyValue8=PPIProject=<code>` พร้อม override output path ก่อน submit
4. `PPIstartup.py` อ่าน extra info ใน `OnJobSubmitted`; ถ้า extra info ยังว่างจะ fallback จาก project code config / job name / `ProjectPath`
5. ใช้ `PPIProject` ไป match config entries 1–3 แล้วเพิ่ม directory ของ `userSetup.mel` เข้า `MAYA_SCRIPT_PATH`
6. กำหนด `OutputFilePath` fallback เป็น `{ProjectPath}/render/{SceneName}/rev####/` โดย scan folder จริงแล้ว auto-increment rev

> **หมายเหตุ:** `OutputDirectory0` (แสดงใน Deadline Monitor) ต้องถูกตั้งจาก Maya submitter ก่อน submit job เพราะ `JobOutputDirectories` เป็น read-only ใน event plugin; local copy `PPIstartup/SubmitMayaToDeadline.mel` จะ override output path เฉพาะ project code ที่อยู่ใน `ppi_projects.txt` ส่วนโปรเจคอื่นยังใช้ `//berry/output/RENDERS/{username}`

#### PPI Submitter Verification

หลัง submit งาน PPI ให้ดู **Job Extra Info → Extra Info Key/Value Pairs**:

| Key | Expected Value | Meaning |
|---|---|---|
| `PPIDetectProjectPath` | Maya project path เช่น `P:/JJK/...` | ค่า `ProjectPath` ที่ submitter ใช้ detect |
| `PPISubmitterVersion` | `2026-06-13-v3` | ยืนยันว่า Maya ใช้ submitter ตัวใหม่ |
| `Pipeline` | `ppi` | งานนี้ถูก tag เป็น PPI |
| `PPIProject` | `JJK` หรือ project code อื่น | project code ที่ match จาก `ppi_projects.txt` |

ถ้าเห็น `PPISubmitterVersion` แต่ไม่มี `Pipeline=ppi` ให้ตรวจ `PPIDetectProjectPath` และ `ppi_projects.txt`; ถ้าไม่เห็น `PPISubmitterVersion` แปลว่ายังไม่ได้ reload/deploy submitter ล่าสุดใน Maya

#### Configuration

| Field | Default | Description |
|---|---|---|
| Event State | Global Enabled | เปิด/ปิด plugin |
| PPI Project Code 1 | `JJK` | Project code จาก extra info `PPIProject` |
| UserSetup MEL Path 1 | `M:/_tech/mayaScript/ppi/jjk/startup/userSetup.mel` | Path ไปยัง `userSetup.mel` สำหรับ Project Code 1 |
| PPI Project Code 2 | _(ว่าง)_ | Project code เพิ่มเติม |
| UserSetup MEL Path 2 | _(ว่าง)_ | Path ไปยัง `userSetup.mel` สำหรับ Project Code 2 |
| PPI Project Code 3 | _(ว่าง)_ | Project code เพิ่มเติม |
| UserSetup MEL Path 3 | _(ว่าง)_ | Path ไปยัง `userSetup.mel` สำหรับ Project Code 3 |

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

2. สำหรับ Maya PPI submitter ให้ copy ไฟล์ไปวางคู่กัน:
   ```
   <DeadlineRepository>/submission/Maya/Main/SubmitMayaToDeadline.mel
   <DeadlineRepository>/submission/Maya/Main/ppi_projects.txt
   ```

3. เปิด Deadline Monitor → **Tools → Configure Event Plugins**

4. ตั้งค่า plugin แต่ละตัว แล้ว Save

5. ดู log ได้ใน Deadline Monitor → **View → Logs → Event Logs**

---

## Notes

- ทุก section ใน `.param` file ต้องมี `Type=` — ถ้าขาดจะเกิด warning ตอน Deadline โหลด plugin
- `[About]` ใช้ `Type=Label` + `Default=` สำหรับ read-only display text (`Value=` ไม่ถูก recognize)

## Requirements

- Thinkbox Deadline 10+
- Maya (MayaBatch / MayaCmd) plugin — สำหรับ MayaOCIOFix, SetJobTimeout
- Arnold renderer — สำหรับ AbortOnError feature ใน MayaOCIOFix
