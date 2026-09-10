# PC-DMIS Macro/Script Library

A library of PC-DMIS automation for a CMM programmer's own inspection
workflows: Basic (`.bas`) scripts and native command-language blocks
(paste-ready for Command Mode), browsable through either a desktop app
or a static HTML catalog, with every entry tracked for how confident we
actually are in it.

## What's here

- **`library/`** — the actual `.bas` and `.txt` files.
  - `library/basic-scripts/` — PC-DMIS Basic automation (loops, dialogs,
    file I/O, COM automation, reporting).
  - `library/dmis-programs/` — native command-language blocks (alignment
    templates, operator-input gates, the `SCRIPT/FILENAME=...` snippets
    that call into a `.bas` file).
  - `library/reference/` — vendor (Hexagon) sample code, kept verbatim as
    a citation for what's actually confirmed vs. guessed elsewhere.
  - `library/README.md` — the file-by-file status table (draft /
    documented / verified) and the backlog. **Read this before trusting
    any individual script.**
- **`manifest.json`** — metadata for the desktop app and HTML catalog:
  title, category, confidence rating, description, deployment guide, and
  caveats for each entry. Holds no script content itself — content is
  always read live from `library/` so the two can't drift apart.
- **`app.py`** — a local, offline desktop app (Tkinter, Python standard
  library only) for browsing the catalog, reading each entry's
  deployment guide and caveats, and exporting a file straight to a
  folder of your choice (e.g. `C:\PCDMIS_Scripts\`).
- **`PCDMIS_Macro_Library.html`** — a static, no-install browser version
  of the same catalog. **Generated, not hand-edited** — see below.
- **`tools/generate_html.py`** — regenerates `PCDMIS_Macro_Library.html`
  from `manifest.json` + `library/`. Run this after editing either.

## Running the desktop app

Requires Python 3.8+ with Tkinter (bundled by default in the official
python.org Windows/Mac installers — on Linux, `sudo apt install
python3-tk` if you hit `No module named tkinter`). No other
dependencies, no internet connection needed.

```
python app.py
```

## Regenerating the HTML catalog

After changing `manifest.json` or any file under `library/`:

```
python tools/generate_html.py
```

This reads the current file contents live and rewrites
`PCDMIS_Macro_Library.html` so the browser catalog always matches what's
on disk — don't hand-edit the generated file.

## Getting a standalone `.exe`

PyInstaller can't cross-compile — a Windows `.exe` has to be built by
PyInstaller running on Windows. This repo has a GitHub Actions workflow
(`.github/workflows/build-windows-exe.yml`) that does exactly that on a
`windows-latest` runner:

- **Automatically** on every push to the default branch that touches
  `app.py`, `manifest.json`, or `library/**`.
- **On demand** via the "Run workflow" button on the Actions tab.
- **As a GitHub Release** with the `.exe` attached, whenever a tag
  matching `v*` is pushed.

Either way, the build downloads as `PCDMIS_Macro_Library.exe` (single
file, windowed — no console) from the workflow run's Artifacts, or from
the release page for a tag build.

## Confidence ratings — read before deploying anything

The scripts under `library/basic-scripts/` and `library/dmis-programs/`
were cross-referenced against Hexagon's own documentation
(docs.hexagonmi.com) and real working code shared by users on
nexus.hexagon.com and pcdmisforum.com, but **most have not been run
against a real PC-DMIS session by this project's owner yet**. The
confidence badges in the app/HTML catalog (high/moderate) and the status
column in `library/README.md` (draft/documented/verified) both reflect
that gap — see `library/README.md` for the full legend and the
per-file notes on exactly what's confirmed vs. still guessed.

One thing worth carrying forward: an earlier source document for this
project claimed to be a "Technical Language Spec" for LLM consumption
and turned out to contain fabricated PC-DMIS syntax when checked against
real documentation. Treat any single unverified source the same way —
cross-reference before trusting new syntax, regardless of how
authoritative it looks.

### Known gap: Geometric Tolerance / FCF dimension data

`OOT_CSV_Export.bas` and `Excel_Export_Results.bas` only read legacy DIM
dimensions correctly. Geometric Tolerance / Feature Control Frame (FCF)
commands — the default since PC-DMIS 2020 R2 — don't expose clean axis
data through the same `Command.DimensionCommand` object model; this is a
confirmed, still-open Hexagon limitation, not a bug in these scripts.
See the backlog in `library/README.md` for the native-command-based
workaround Hexagon has confirmed (`SEGMENT[]/FEATURE[]/axis.MEAS`
expression syntax) that hasn't been implemented here yet.
