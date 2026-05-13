# Thinkbox Deadline Custom Event Plugins

## Project Structure

```
deadline-event/
├── MayaOCIOFix/
│   ├── MayaOCIOFix.py      # Event plugin logic
│   └── MayaOCIOFix.param   # Config UI definition for Deadline Monitor
├── UsersSuspendJob/
│   ├── UsersSuspendJob.py
│   └── UsersSuspendJob.param
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
- Read plugin config with `self.GetConfigEntryWithDefault("Key", "default")`
- Read/write job plugin info with `job.GetJobPluginInfoKeyValue()` / `job.SetJobPluginInfoKeyValue()`
- Persist job changes with `RepositoryUtils.SaveJob(job)`
- Hook callbacks via `+=` on the callback attribute; delete with `del` in `CleanUp`

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

## .param File Format

```ini
[FieldName]
Type=Enum|String|Integer|Boolean
Values=A;B;C          # Enum only
Label=Display Name
Category=Group Name
CategoryIndex=0
Default=value
Description=Shown in Deadline Monitor UI
```
