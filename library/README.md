# PC-DMIS Macro/Script Library

A growing library of PC-DMIS automation, organized by type:

- `dmis-programs/` — PC-DMIS command-language program files (the interactive
  editor syntax, e.g. alignment blocks, feature measurement blocks).
- `basic-scripts/` — PC-DMIS Basic (`.bas`) automation scripts (loops,
  dialogs, file I/O, reporting, things that wrap around a program).

## Status

Every entry is tracked here as one of:

- **draft** — written from general knowledge, not confirmed by any
  documentation or test. Treat as unverified.
- **documented** — matches vendor (Hexagon) documentation the user provided,
  but not yet confirmed by a real test run in PC-DMIS.
- **verified** — confirmed by running in real PC-DMIS and importing/executing
  cleanly with no manual fixes.

| File | Type | Status | Notes |
|---|---|---|---|
| `basic-scripts/AlignmentRepeatability.bas` | Basic script | draft (partially documented) | Loops an alignment N times, checks origin/orientation spread against tolerance. `CreateObject("PCDLRN.Application")` and `App.ActivePartProgram` are now documented (see reference below); reading back the alignment result and re-running a labeled block are still unconfirmed guesses marked `VERIFY:`. |
| `reference/hexagon-sample-01-increment-variable/` | Reference (vendor doc) | documented | Hexagon's own sample: DMIS program calls a `.bas` script to increment a variable. Confirms `CreateObject`, `ActivePartProgram`, `GetVariableValue`/`SetVariableValue`, and the `SCRIPT/FILENAME=` block for invoking a script from a program. |

## Adding a new entry

Per the project workflow: before any new entry is written, we need 1-2 real,
working reference files of that type so syntax isn't guessed. Each new entry
should note in this table what's fixed boilerplate vs. variable input, get
confirmed, then move from draft to verified only after a real PC-DMIS test.

## Candidate types not yet started

Rough backlog, not commitments — pick and prioritize:

- Alignment routine (standard, e.g. 3-2-1 plane/line/point)
- Feature measurement block (circle, plane, point, etc. with tolerances)
- Probe/tip qualification sequence
- GR&R / repeatability report automation (beyond single-alignment check)
- Batch/multi-part execution with operator prompts
- Custom result export (Excel/CSV/SPC formatting)
- Out-of-tolerance alerting
- CAD/part-number driven setup
