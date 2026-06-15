# Changelog

## 2026-06-15

### Added

- Added configurable PPI event settings for forced Deadline group and Maya-version pools:
  - `PPIGroup=ppi`
  - `Maya2023Pool=maya2023-arnold522`
  - `Maya2024Pool=maya2024-arnold5341`
  - `Maya2025Pool=maya2025-arnold545`
- Added event logs that report the forced PPI group and selected Maya-version pool.

### Changed

- PPI Maya render submissions now force `ChunkSize=10` at submit time while non-PPI jobs keep the UI/persistent task-size behavior.
- `PPIstartup.py` now forces matched PPI jobs to `Group=ppi` and selects `Pool` from the submitted Maya version.

## 2026-06-13

### Added

- Added local Maya submitter copy at `PPIstartup/SubmitMayaToDeadline.mel` for the PPI output-path workflow.
- Added `PPIstartup/ppi_projects.txt` with initial project code `JJK`.
- Added submitter debug Extra Info:
  - `PPIDetectProjectPath=<ProjectPath seen by submitter>`
  - `PPISubmitterVersion=2026-06-13-v3`
- Added `AGENT.md` with repo-specific maintenance and deploy notes.

### Changed

- `PPIstartup.py` now prefers Deadline Extra Info (`Pipeline=ppi`, `PPIProject=<code>`) instead of relying only on job-name prefixes.
- `PPIstartup.py` keeps fallback detection by configured project code, job name, and `ProjectPath` for rollout safety.
- `PPIstartup.param` labels/descriptions now describe `Prefix1/2/3` as PPI project codes.
- `SubmitMayaToDeadline.mel` detects PPI projects from `ProjectPath` segments matched against `ppi_projects.txt`.
- PPI jobs now write:
  - `ExtraInfoKeyValue7=Pipeline=ppi`
  - `ExtraInfoKeyValue8=PPIProject=<code>`
- PPI jobs override submitter output path before submission so Deadline can create the correct `OutputDirectory0`.
- README now documents the PPI submitter flow, verification keys, and deploy locations.

### Fixed

- Removed attempts to set `JobOutputDirectories` from the event plugin because Deadline exposes it as read-only in `OnJobSubmitted`.
- Kept non-PPI Maya jobs on the existing default output path: `//berry/output/RENDERS/{username}`.
