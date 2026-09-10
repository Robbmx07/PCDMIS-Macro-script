#!/usr/bin/env python3
"""
Regenerates PCDMIS_Macro_Library.html from manifest.json + library/.

manifest.json holds only metadata (title, description, confidence, guide,
caveats, filename, companion). This script reads the actual file contents
live from library/ and embeds them into the HTML, so the browser catalog
and the on-disk scripts can never drift out of sync with each other.

Run after editing manifest.json or any file under library/:
    python tools/generate_html.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "manifest.json"
LIBRARY_DIR = ROOT / "library"
OUTPUT_PATH = ROOT / "PCDMIS_Macro_Library.html"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PC-DMIS Macro Library</title>
<style>
  :root{{
    --bg:#15181c;
    --panel:#1b1f25;
    --panel-alt:#20252c;
    --border:#2c323a;
    --text:#e7e4de;
    --text-dim:#8b93a1;
    --text-faint:#5c6570;
    --accent:#e2a33c;
    --accent-soft:#3a3120;
    --ok:#6fbf8b;
    --ok-soft:#20302a;
    --mod:#e2a33c;
    --mod-soft:#332a1a;
    --mono: ui-monospace, "SF Mono", "Cascadia Code", Consolas, "Roboto Mono", monospace;
    --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  }}
  *{{box-sizing:border-box;}}
  html,body{{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:var(--sans);height:100%;}}
  body{{display:flex;flex-direction:column;min-height:100vh;}}

  header{{
    border-bottom:1px solid var(--border);
    padding:22px 28px 18px;
    display:flex;
    align-items:baseline;
    justify-content:space-between;
    flex-wrap:wrap;
    gap:8px;
  }}
  header h1{{
    font-size:19px;
    font-weight:600;
    letter-spacing:0.2px;
    margin:0;
  }}
  header .sub{{
    color:var(--text-dim);
    font-size:13px;
  }}
  header .count{{
    font-family:var(--mono);
    color:var(--text-faint);
    font-size:12px;
  }}

  .disclaimer{{
    margin:14px 28px 0;
    border:1px solid var(--mod-soft);
    background:var(--mod-soft);
    border-radius:4px;
    padding:12px 16px;
    font-size:13px;
    line-height:1.5;
    color:#e8cf9f;
  }}

  .layout{{
    display:flex;
    flex:1;
    min-height:0;
  }}

  .sidebar{{
    width:320px;
    min-width:320px;
    border-right:1px solid var(--border);
    display:flex;
    flex-direction:column;
    overflow-y:auto;
  }}

  .filters{{
    display:flex;
    flex-wrap:wrap;
    gap:6px;
    padding:14px 16px;
    border-bottom:1px solid var(--border);
  }}
  .chip{{
    font-family:var(--mono);
    font-size:11px;
    color:var(--text-dim);
    border:1px solid var(--border);
    padding:4px 9px;
    border-radius:3px;
    cursor:pointer;
    background:transparent;
    white-space:nowrap;
  }}
  .chip:hover{{border-color:var(--text-faint);color:var(--text);}}
  .chip.active{{border-color:var(--accent);color:var(--accent);background:var(--accent-soft);}}

  .group-label{{
    font-size:11px;
    color:var(--text-faint);
    padding:14px 16px 4px;
  }}

  .item{{
    padding:11px 16px;
    border-bottom:1px solid var(--border);
    cursor:pointer;
  }}
  .item:hover{{background:var(--panel-alt);}}
  .item.selected{{background:var(--panel-alt);border-left:2px solid var(--accent);padding-left:14px;}}
  .item .title{{font-size:13.5px;font-weight:500;margin-bottom:4px;}}
  .item .meta{{display:flex;gap:8px;align-items:center;font-size:11px;color:var(--text-dim);}}
  .dot{{width:6px;height:6px;border-radius:50%;display:inline-block;}}
  .dot.high{{background:var(--ok);}}
  .dot.moderate{{background:var(--mod);}}
  .dot.low{{background:#c15a45;}}

  .detail{{
    flex:1;
    overflow-y:auto;
    padding:32px 40px 60px;
    max-width:820px;
  }}

  .detail .kicker{{
    font-family:var(--mono);
    font-size:11px;
    color:var(--text-faint);
    margin-bottom:8px;
  }}
  .detail h2{{
    font-size:24px;
    margin:0 0 14px;
    font-weight:600;
  }}
  .badges{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:22px;}}
  .badge{{
    font-family:var(--mono);
    font-size:11px;
    padding:4px 10px;
    border-radius:3px;
    border:1px solid var(--border);
    color:var(--text-dim);
  }}
  .badge.conf-high{{color:var(--ok);border-color:var(--ok-soft);background:var(--ok-soft);}}
  .badge.conf-moderate{{color:var(--mod);border-color:var(--mod-soft);background:var(--mod-soft);}}

  .detail p{{line-height:1.55;font-size:14.5px;color:var(--text);}}
  .detail .lead{{color:var(--text);font-size:15.5px;line-height:1.6;margin-bottom:20px;}}

  .section-title{{
    font-size:12px;
    color:var(--text-faint);
    margin:28px 0 10px;
    padding-bottom:6px;
    border-bottom:1px solid var(--border);
  }}

  ol.guide{{margin:0;padding-left:22px;}}
  ol.guide li{{margin-bottom:10px;line-height:1.55;font-size:14px;}}

  .caveat{{
    border:1px solid var(--mod-soft);
    background:var(--mod-soft);
    border-radius:4px;
    padding:14px 16px;
    font-size:13.5px;
    line-height:1.55;
    color:#e8cf9f;
  }}

  .files{{display:flex;gap:8px;margin-top:6px;flex-wrap:wrap;}}
  .filetab{{
    font-family:var(--mono);
    font-size:12px;
    padding:6px 12px;
    border:1px solid var(--border);
    border-bottom:none;
    border-radius:4px 4px 0 0;
    color:var(--text-dim);
    cursor:pointer;
  }}
  .filetab.active{{color:var(--text);background:var(--panel-alt);border-color:var(--border);}}

  .codebox{{
    border:1px solid var(--border);
    background:#101317;
    border-radius:0 4px 4px 4px;
    padding:16px;
    font-family:var(--mono);
    font-size:12.5px;
    line-height:1.6;
    color:#c9d1d9;
    white-space:pre-wrap;
    word-break:break-word;
    max-height:420px;
    overflow-y:auto;
  }}

  .actions{{display:flex;gap:10px;margin-top:12px;}}
  button.act{{
    font-family:var(--sans);
    font-size:13px;
    padding:8px 14px;
    border-radius:4px;
    border:1px solid var(--border);
    background:transparent;
    color:var(--text);
    cursor:pointer;
  }}
  button.act:hover{{border-color:var(--accent);color:var(--accent);}}
  button.act.primary{{background:var(--accent);border-color:var(--accent);color:#1b1204;font-weight:600;}}
  button.act.primary:hover{{opacity:0.9;color:#1b1204;}}

  ::-webkit-scrollbar{{width:10px;height:10px;}}
  ::-webkit-scrollbar-thumb{{background:var(--border);border-radius:5px;}}
  ::-webkit-scrollbar-track{{background:transparent;}}

  @media (max-width:760px){{
    .layout{{flex-direction:column;}}
    .sidebar{{width:100%;min-width:0;max-height:280px;}}
    .detail{{padding:24px 20px 60px;}}
  }}
</style>
</head>
<body>

<header>
  <div>
    <h1>PC-DMIS Macro Library</h1>
    <div class="sub">Scripts and command blocks, cross-referenced against Hexagon documentation and real working code</div>
  </div>
  <div class="count" id="countLabel"></div>
</header>

<div class="disclaimer">
  Confidence ratings reflect cross-referencing against Hexagon documentation and community-shared working code &mdash;
  not a real PC-DMIS test run by this project's owner. Verify each file against your own PC-DMIS session before
  relying on it in production. See <code>library/README.md</code> for this repo's own draft/documented/verified
  tracking on hand-authored scripts.
</div>

<div class="layout">
  <div class="sidebar">
    <div class="filters" id="filters"></div>
    <div id="itemList"></div>
  </div>
  <div class="detail" id="detail"></div>
</div>

<script>
const LIBRARY = {library_json};

let activeFilter = "All";
let selectedId = LIBRARY[0].id;
let activeFileTab = "script";

const categories = ["All", ...Array.from(new Set(LIBRARY.map(e => e.category)))];

function renderFilters(){{
  const el = document.getElementById("filters");
  el.innerHTML = "";
  categories.forEach(cat => {{
    const chip = document.createElement("div");
    chip.className = "chip" + (cat === activeFilter ? " active" : "");
    chip.textContent = cat;
    chip.onclick = () => {{ activeFilter = cat; renderAll(); }};
    el.appendChild(chip);
  }});
}}

function renderList(){{
  const el = document.getElementById("itemList");
  el.innerHTML = "";
  const filtered = LIBRARY.filter(e => activeFilter === "All" || e.category === activeFilter);
  document.getElementById("countLabel").textContent = filtered.length + " / " + LIBRARY.length + " files";

  let lastCat = null;
  filtered.forEach(e => {{
    if(e.category !== lastCat){{
      const label = document.createElement("div");
      label.className = "group-label";
      label.textContent = e.category;
      el.appendChild(label);
      lastCat = e.category;
    }}
    const item = document.createElement("div");
    item.className = "item" + (e.id === selectedId ? " selected" : "");
    item.innerHTML = `
      <div class="title">${{e.title}}</div>
      <div class="meta">
        <span class="dot ${{e.confidence}}"></span>
        <span>${{e.type}}</span>
      </div>
    `;
    item.onclick = () => {{ selectedId = e.id; activeFileTab = "script"; renderAll(); }};
    el.appendChild(item);
  }});
}}

function download(filename, content){{
  const blob = new Blob([content], {{type:"text/plain"}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}}

function copyText(text, btn){{
  navigator.clipboard.writeText(text).then(() => {{
    const original = btn.textContent;
    btn.textContent = "Copied";
    setTimeout(() => {{ btn.textContent = original; }}, 1200);
  }});
}}

function renderDetail(){{
  const e = LIBRARY.find(x => x.id === selectedId);
  const el = document.getElementById("detail");
  if(!e){{ el.innerHTML = ""; return; }}

  const confLabel = e.confidence === "high" ? "High confidence" : e.confidence === "moderate" ? "Moderate confidence" : "Low confidence";

  let filesTabHtml = `<div class="filetab ${{activeFileTab==='script'?'active':''}}" data-tab="script">${{e.filename}}</div>`;
  if(e.companion){{
    filesTabHtml += `<div class="filetab ${{activeFileTab==='companion'?'active':''}}" data-tab="companion">${{e.companion}}</div>`;
  }}

  const currentContent = activeFileTab === "companion" && e.companionContent ? e.companionContent : e.scriptContent;
  const currentFilename = activeFileTab === "companion" && e.companionContent ? e.companion : e.filename;

  el.innerHTML = `
    <div class="kicker">${{e.category}}</div>
    <h2>${{e.title}}</h2>
    <div class="badges">
      <div class="badge">${{e.type}}</div>
      <div class="badge conf-${{e.confidence}}">${{confLabel}}</div>
    </div>

    <p class="lead">${{e.description}}</p>
    <p>${{e.explanation}}</p>

    <div class="section-title">Why this confidence rating</div>
    <p>${{e.confidenceNote}}</p>

    <div class="section-title">Deployment guide</div>
    <ol class="guide">${{e.guide.map(g => `<li>${{g}}</li>`).join("")}}</ol>

    <div class="section-title">Before you rely on this</div>
    <div class="caveat">${{e.caveats}}</div>

    <div class="section-title">File${{e.companion ? "s" : ""}}</div>
    <div class="files">${{filesTabHtml}}</div>
    <div class="codebox" id="codebox">${{currentContent.replace(/&/g,"&amp;").replace(/</g,"&lt;")}}</div>
    <div class="actions">
      <button class="act primary" id="downloadBtn">Download ${{currentFilename}}</button>
      <button class="act" id="copyBtn">Copy to clipboard</button>
    </div>
  `;

  el.querySelectorAll(".filetab").forEach(tab => {{
    tab.onclick = () => {{ activeFileTab = tab.getAttribute("data-tab"); renderDetail(); }};
  }});
  document.getElementById("downloadBtn").onclick = () => download(currentFilename, currentContent);
  document.getElementById("copyBtn").onclick = (ev) => copyText(currentContent, ev.target);
}}

function renderAll(){{
  renderFilters();
  renderList();
  renderDetail();
}}

renderAll();
</script>
</body>
</html>
"""


def find_lib_file(filename):
    if not filename:
        return None
    direct = LIBRARY_DIR / filename
    if direct.exists():
        return direct
    matches = list(LIBRARY_DIR.rglob(filename))
    return matches[0] if matches else None


def read_lib_file(filename):
    path = find_lib_file(filename)
    if path is None:
        raise FileNotFoundError(
            f"manifest.json references '{filename}' but no such file exists under {LIBRARY_DIR}"
        )
    return path.read_text(encoding="utf-8")


def build():
    entries = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    enriched = []
    for e in entries:
        entry = dict(e)
        entry["scriptContent"] = read_lib_file(e["filename"])
        entry["companionContent"] = read_lib_file(e["companion"]) if e.get("companion") else None
        enriched.append(entry)

    library_json = json.dumps(enriched, indent=2)
    html = HTML_TEMPLATE.format(library_json=library_json)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({len(enriched)} entries)")


if __name__ == "__main__":
    build()
