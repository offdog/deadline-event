# Thinkbox Deadline Custom Event Plugins

## Project Structure

```
deadline-event/
├── MayaOCIOFix/
│   ├── MayaOCIOFix.py
│   └── MayaOCIOFix.param
├── UsersSuspendJob/
│   ├── UsersSuspendJob.py
│   └── UsersSuspendJob.param
├── SetJobTimeout/
│   ├── SetJobTimeout.py
│   └── SetJobTimeout.param
├── SetMachineLimit/
│   ├── SetMachineLimit.py
│   └── SetMachineLimit.param
├── UnmapAllDrive/
│   ├── UnmapAllDrive.py
│   └── UnmapAllDrive.param
└── _backup/                # Old versions — do not touch
```

## Deploy Path

Copy each plugin folder to:
```
<DeadlineRepository>/custom/events/<PluginName>/
```

## Deadline Event Plugin Conventions

- Entry points: `GetDeadlineEventListener()` and `CleanupDeadlineEventListener()`
- Always use wildcard imports — IronPython runtime requires them:
  ```python
  from Deadline.Events import *
  from Deadline.Scripting import *
  ```
- Read plugin config with `self.GetConfigEntryWithDefault("Key", "default")` (string) or `self.GetIntegerConfigEntryWithDefault("Key", default)` (int)
- Read/write job plugin info with `job.GetJobPluginInfoKeyValue()` / `job.SetJobPluginInfoKeyValue()`
- Persist job changes with `RepositoryUtils.SaveJob(job)`
- Hook callbacks via `+=` on the callback attribute; delete with `del` in `CleanUp`
- Worker/Slave callbacks receive `(slave, slaveInfo)` args; job callbacks receive `(job)`

## MayaOCIOFix

Fires on `OnJobSubmitted` for `MayaBatch` and `MayaCmd` jobs.

**Logic flow:**
1. Skip if plugin is not `MayaBatch` / `MayaCmd`
2. Read job's `Version` plugin info key; skip if not in `MayaVersion` config list
3. Read `OCIOConfigFile`; skip if empty or `<MAYA_RESOURCES>` not present
4. Replace `<MAYA_RESOURCES>` with `{MayaInstallBasePath}/Maya{jobVersion}/resources`
5. Save job
6. If `AbortOnError != Unchanged`, inject MEL into `PreRenderMel` (appends, does not overwrite)

**Key plugin info keys read/written:** `OCIOConfigFile`, `PreRenderMel`, `Version`

## UsersSuspendJob

Fires on `OnJobSubmitted`. Suspends the job immediately if the submitting user is in the `SuspendUsers` config list (comma-separated, case-insensitive).

## SetJobTimeout

Fires on `OnJobSubmitted`. Sets `JobTaskTimeoutSeconds`, `JobMinRenderTimeSeconds`, and `JobOnTaskTimeout` only for jobs whose plugin name is in the `AllowedSoftware` config list.

**Config:** Max/Min timeout broken into Hours/Minutes/Seconds fields; `DoTask` enum (Error/Notify/Requeue/Fail/Complete).

## SetMachineLimit

Fires on `OnJobSubmitted`, `OnJobStarted`, `OnJobResumed`, `OnJobRequeued`.

Dynamically sets `MachineLimitMaximum` based on current active job count vs threshold:
- active jobs > `ActiveJobThreshold` AND priority > `JobPriorityThreshold` → set limit to `MachineLimitMaximumHigh`
- otherwise → set limit to `0` (unlimited)

Uses `RepositoryUtils.GetJobsInState("Active")` to count live jobs at event time.

## UnmapAllDrive

Fires on Worker events: `OnSlaveIdle`, `OnSlaveStopped`, `OnSlaveStalled`, `OnMachineRestart`.

Runs `net use /del /y *` on the worker machine to unmap all network drives. Skips if `UserFilter` is empty; runs for all users if `*`; otherwise filters by comma-separated username list (matched against `os.getlogin()`).

Note: uses specific imports (`from Deadline.Events import DeadlineEventListener`) not wildcard — do not change, it works.

## .param File Format

```ini
[FieldName]
Type=Enum|String|Integer|Boolean
Values=A;B;C          # Enum only (some plugins use Items= instead)
Label=Display Name
Category=Group Name
CategoryIndex=0
Default=value
Description=Shown in Deadline Monitor UI
```
