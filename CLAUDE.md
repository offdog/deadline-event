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
├── NukeCleanup/
│   ├── NukeCleanup.py
│   └── NukeCleanup.param
├── SetJobsEnv/
│   ├── SetJobsEnv.py
│   └── SetJobsEnv.param
├── PPIstartup/
│   ├── PPIstartup.py
│   └── PPIstartup.param
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
3. OCIO patch (independent — runs regardless of AbortOnError):
   - Read `OCIOConfigFile`; skip patch if empty or `<MAYA_RESOURCES>` not present
   - Replace `<MAYA_RESOURCES>` with `{MayaInstallBasePath}/Maya{jobVersion}/resources` and save job
4. AbortOnError (always runs for all version-matched jobs, default `Disable` → set `abortOnError 0`):
   - If `AbortOnError != Unchanged`, inject MEL into `PreRenderMel` (appends, does not overwrite) and save job

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

## NukeCleanup

Fires on `OnSlaveStartingJob` and/or `OnJobFinished` for jobs whose `PluginName` contains `"Nuke"`.

Deletes all `.tmp` files in each of the job's output directories. Uses `OnSlaveStartingJob` instead of `OnJobStarted` as a workaround for `OnJobStarted` not firing reliably.

**Config:** `CleanTmpFilesEvent` enum — `On Job Started` / `On Job Finished` / `On Job Started and On Job Finished`

## SetJobsEnv

Fires on `OnJobSubmitted` for all jobs. Injects environment variables into the job's environment at submit time.

**Config:** `EnvKeys` — semicolon-separated `KEY=VALUE` pairs (e.g. `OCIO=/path/to/config.ocio;MY_VAR=1`). Uses `job.SetJobEnvironmentKeyValue()` + `RepositoryUtils.SaveJob()`.

## PPIstartup

Fires on `OnJobSubmitted` for `MayaBatch` and `MayaCmd` jobs. Supports up to 3 numbered prefix/MEL path pairs (`Prefix1`/`MelPath1` … `Prefix3`/`MelPath3`).

**Logic flow:**
1. Skip if plugin is not `MayaBatch` / `MayaCmd`
2. Loop entries 1–3: skip if `Prefix{i}` is empty; if `job.JobName.startswith(prefix)` → use `MelPath{i}` (first match wins)
3. If no prefix matched → skip (return)
4. Append script directory (extracted from matched `MelPath{i}`) to `MAYA_SCRIPT_PATH` job environment — Maya auto-sources `userSetup.mel` from all directories in this path at startup
5. Auto-set `OutputFilePath` (Plugin Info) to `{ProjectPath}/render/{SceneName}/rev####/` — scans existing `rev\d{4}` subdirs and increments; starts at `rev0001` if none exist
6. `RepositoryUtils.SaveJob(job)` once at end

**Key notes:**
- `SetJobEnvironmentKeyValue` auto-saves immediately (no SaveJob needed for env vars)
- `SetJobPluginInfoKeyValue` requires explicit `RepositoryUtils.SaveJob()` to persist
- `OutputDirectory0` (Job Info display field) **cannot** be changed from an event plugin — Deadline API limitation; `OutputFilePath` (the actual render path used by MayaCmd as `-rd`) is correctly set
- Uses `import re` for `re.match(r'^rev\d{4}$', d)` when scanning rev dirs

**Key plugin info keys read/written:** `ProjectPath`, `SceneFile`, `OutputFilePath`

## .param File Format

```ini
[FieldName]
Type=Enum|String|Integer|Boolean|Label
Values=A;B;C          # Enum only (some plugins use Items= instead)
Label=Display Name
Category=Group Name
CategoryIndex=0
Default=value
Description=Shown in Deadline Monitor UI
```

- Every section **must** declare `Type=` — Deadline will warn on load if missing
- Use `Type=Label` with `Default=` for read-only display fields (e.g. `[About]`)
