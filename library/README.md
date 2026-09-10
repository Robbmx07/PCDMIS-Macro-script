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
| `basic-scripts/OOT_CSV_Export.bas` + `dmis-programs/OOT_CSV_Export_Insert.txt` | Basic script + native insert | documented | Scans dimensions after a run and CSV-logs anything out of tolerance. Object model (`IsDimension`/`DimensionCommand`) cross-referenced against Hexagon docs and community examples, not run against a live session here. **Confirmed gap**: only reads legacy DIM dimensions — Geometric Tolerance/FCF dimensions (default since PC-DMIS 2020 R2) report all-zero values, a known open Hexagon limitation, not a bug in this script. |
| `basic-scripts/PartCounter_Increment.bas` + `dmis-programs/PartCounter_Insert.txt` | Basic script + native insert | documented | Increments a `V_PART_COUNT` variable per loop pass. Directly grounded in Hexagon's own official sample (see `reference/hexagon-sample-01-increment-variable/`). `SetVariableValue` only persists for the current execution run; use `PutText` for a permanent change (not implemented here). |
| `basic-scripts/Validate_SerialNumber.bas` + `dmis-programs/Validate_SerialNumber_Insert.txt` | Basic script + native insert | documented | Validates an operator-entered serial number against an `SN-####` pattern and re-prompts via `LABEL/GOTO/IF...END_IF` on failure. That control-flow pattern is confirmed against real user-posted PC-DMIS code. The exact format check is a placeholder — edit the `Len`/`Left`/`Right` logic to match your own part numbering convention. |
| `basic-scripts/Excel_Export_Results.bas` + `dmis-programs/Excel_Export_Insert.txt` | Basic script + native insert | draft (partially documented) | Exports legacy DIM dimensions to a new Excel workbook via COM automation. PC-DMIS object access is the same confirmed pattern as the CSV export; the combined script (PC-DMIS object model + Excel COM calls in one run) has not itself been tested end to end. Same GeoTol/FCF gap as the CSV export. |
| `basic-scripts/Runtime_Logger.bas` + `dmis-programs/Runtime_Logger_Insert.txt` | Basic script + native insert | draft (partially documented) | Two-`Sub` timer (`StartTimer`/`StopTimer`) requiring two separate insertion points in the routine. Variable read/write and file logging are individually confirmed patterns; this exact two-`Sub`, two-insertion-point combination hasn't been tested end to end — easy to leave `Function` set to the wrong `Sub` on one of the two inserts. |
| `basic-scripts/Operator_ShiftLog.bas` + `dmis-programs/Operator_ShiftLog_Insert.txt` | Basic script + native insert | documented | Logs employee ID + timestamp + routine name to a shift log CSV. Reuses the same confirmed variable-read and file-logging pattern as the OOT export and serial number validator. No format validation on the employee ID in this version. |
| `dmis-programs/PDF_AutoReport_Export.txt` | Native command block | documented | Pure command-language block, no Basic script involved. Builds a date/time-stamped filename and calls `PRINT/REPORT` with `TO_FILE=ON`. `PRINT/REPORT` syntax and the `SYSTEMDATE`/`SYSTEMTIME` stamping pattern are confirmed from real working routines shared in Hexagon's community. |
| `dmis-programs/Alignment_321_Template.txt` | Native command block | draft (partially documented) | Standard Level/Rotate/Translate 3-2-1 alignment skeleton. The general shape is standard PC-DMIS practice but has not been cross-checked parameter-by-parameter against a live export — treat as a starting skeleton and verify against one of your own known-good alignment exports. |
| `dmis-programs/FixtureCheck_Confirmation.txt` | Native command block | documented | Yes/no fixture-setup confirmation gate using the confirmed `LABEL/GOTO/IF...END_IF` re-prompt pattern. Touches no automation objects, files, or external applications — the lowest-risk file in the library to test first. |

These nine entries (plus their metadata, deployment guides, and caveats) were imported from a separate catalog the owner had generated in another session, along with a desktop app (`app.py`, stdlib-only Tkinter) and a browser catalog (`PCDMIS_Macro_Library.html`, generated from `manifest.json` + this folder by `tools/generate_html.py` — see the root [README.md](../README.md)). Their "documented"/"draft" status above is this repo's own read on the confidence notes that shipped with them, mapped onto the scale defined below; none of them have been run against a real PC-DMIS session by this project's owner yet. Treat the "high"/"moderate" confidence badges shown in the app and HTML catalog as a secondary signal from that other session's research, not a substitute for the status column here.

## Adding a new entry

Per the project workflow: before any new entry is written, we need 1-2 real,
working reference files of that type so syntax isn't guessed. Each new entry
should note in this table what's fixed boilerplate vs. variable input, get
confirmed, then move from draft to verified only after a real PC-DMIS test.

## Candidate types not yet started

Rough backlog, not commitments — pick and prioritize:

- **GeoTol/FCF axis-data export** — `OOT_CSV_Export.bas` and `Excel_Export_Results.bas`
  only read legacy DIM dimensions; Feature Control Frame dimensions (default since
  PC-DMIS 2020 R2) return all-zero values through `DimensionCommand`, a confirmed
  open Hexagon limitation, not a bug here. Hexagon has confirmed the
  `SEGMENT[]/FEATURE[]/axis.MEAS` expression syntax still works when typed directly
  into the edit window (not exposed in the expression builder UI) — this needs a
  native-command-based variant, not a Basic script fix, since the gap is in the
  object model itself. Needs its own reference sample before writing new code, per
  the "Adding a new entry" rule above.
- Feature measurement block (circle, plane, point, etc. with tolerances)
- Probe/tip qualification sequence
- GR&R / repeatability report automation (beyond single-alignment check)
- CAD/part-number driven setup
