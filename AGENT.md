# Agent Notes

This repo contains custom Thinkbox Deadline event plugins and one local Maya submitter copy used for the PPI startup/output-path workflow.

## Ground Rules

- Do not edit `_backup/` unless explicitly asked.
- Preserve Deadline/IronPython compatibility in event plugins:
  - Keep `from Deadline.Events import *`
  - Keep `from Deadline.Scripting import *`
  - Persist plugin-info changes with `RepositoryUtils.SaveJob(job)`
- `JobOutputDirectories` / `OutputDirectory0` is read-only from `OnJobSubmitted`; do not try to set it in `PPIstartup.py`.
- For Maya output display in Deadline Monitor, set output path in `SubmitMayaToDeadline.mel` before submission.
- `.claude/settings.json` may be dirty from local tooling; do not touch it unless asked.

## PPI Startup Flow

Files:

- `PPIstartup/SubmitMayaToDeadline.mel`
- `PPIstartup/ppi_projects.txt`
- `PPIstartup/PPIstartup.py`
- `PPIstartup/PPIstartup.param`

Submitter behavior:

- Reads `ppi_projects.txt` from the same Deadline repository folder as the Maya submitter.
- Detects PPI projects from Maya `ProjectPath` path segments, for example `P:/JJK/...` matches `JJK`.
- Always writes `PPISubmitterVersion=2026-06-13-v3` for Maya render jobs as a deploy/reload marker.
- Writes `Pipeline=ppi` and `PPIProject=<code>` only when project detection matches.
- Overrides output path for PPI jobs before submit so `OutputDirectory0` and `OutputFilePath` can match.
- Leaves non-PPI projects on the default `//berry/output/RENDERS/{username}` path.

Event plugin behavior:

- Runs only for `MayaBatch` and `MayaCmd`.
- Prefers Deadline Extra Info: `Pipeline=ppi`, `PPIProject=<code>`.
- Falls back to configured project code / job name / `ProjectPath` while rollout is in progress.
- Adds the matching `userSetup.mel` directory to `MAYA_SCRIPT_PATH`.
- Sets `OutputFilePath` as a fallback, but does not and cannot set `OutputDirectory0`.

## Deploy

Event plugin:

```text
<DeadlineRepository>/custom/events/PPIstartup/
```

Maya submitter files:

```text
<DeadlineRepository>/submission/Maya/Main/SubmitMayaToDeadline.mel
<DeadlineRepository>/submission/Maya/Main/ppi_projects.txt
```

After updating the Maya submitter, reload it in Maya or restart Maya:

```mel
source "M:/_tech/DeadlineRepository10/submission/Maya/Main/SubmitMayaToDeadline.mel";
```

## Verification

For a PPI job, Job Extra Info key/value pairs should include:

```text
PPIDetectProjectPath=P:/JJK/...
PPISubmitterVersion=2026-06-13-v3
Pipeline=ppi
PPIProject=JJK
```

Interpretation:

- Missing `PPISubmitterVersion`: Maya is using an old submitter or it was not re-sourced.
- Has `PPISubmitterVersion` but no `Pipeline=ppi`: project detection failed; inspect `PPIDetectProjectPath` and `ppi_projects.txt`.
- Has `Pipeline=ppi` but `OutputDirectory0` is still berry: output override is not applied in the active submitter path.
- Event log says fallback detection: job was not tagged by submitter, but event plugin still matched from config/name/path.
