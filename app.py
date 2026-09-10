"""
PC-DMIS Macro Library — desktop application
=============================================
A local, offline reference tool for browsing the macro/script library,
reading each file's description, function explanation, confidence rating
and deployment guide, and exporting the actual file to a folder of your
choice (e.g. C:\\PCDMIS_Scripts\\) or copying it to the clipboard.

Requires only the Python standard library (Tkinter ships with the
standard Windows/Mac installer from python.org). No internet connection
or extra packages needed.

Run with:
    python app.py
"""

import json
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

if getattr(sys, "frozen", False):
    # Running as a PyInstaller-built executable: bundled data files
    # (manifest.json, library/) are extracted into sys._MEIPASS at
    # startup, not next to the .exe itself.
    ROOT = Path(sys._MEIPASS)  # type: ignore[attr-defined]
else:
    ROOT = Path(__file__).resolve().parent
LIBRARY_DIR = ROOT / "library"
MANIFEST_PATH = ROOT / "manifest.json"

# ---------------------------------------------------------------------------
# Color palette (matches the browser catalog version for consistency)
# ---------------------------------------------------------------------------
BG = "#15181c"
PANEL = "#1b1f25"
PANEL_ALT = "#20252c"
BORDER = "#2c323a"
TEXT = "#e7e4de"
TEXT_DIM = "#8b93a1"
TEXT_FAINT = "#5c6570"
ACCENT = "#e2a33c"
OK = "#6fbf8b"
MOD = "#e2a33c"
CAVEAT_BG = "#332a1a"
CAVEAT_FG = "#e8cf9f"
CODE_BG = "#101317"
CODE_FG = "#c9d1d9"

MONO_FONT = ("Consolas", 10) if sys.platform.startswith("win") else ("Menlo", 11)
SANS_FONT = ("Segoe UI", 10) if sys.platform.startswith("win") else ("Helvetica", 12)
SANS_BOLD = (SANS_FONT[0], SANS_FONT[1], "bold")

DISCLAIMER = (
    "Confidence ratings reflect cross-referencing against Hexagon "
    "documentation and community-shared working code \u2014 not a real "
    "PC-DMIS test run by this project's owner. Verify each file against "
    "your own PC-DMIS session before relying on it in production."
)


def load_manifest():
    if not MANIFEST_PATH.exists():
        messagebox.showerror("Missing manifest.json",
                              f"Could not find manifest.json next to app.py.\nExpected at: {MANIFEST_PATH}")
        sys.exit(1)
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def find_lib_file(filename):
    """Locate a library file by name anywhere under LIBRARY_DIR."""
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
        return f"[File not found in library folder: {filename}]"
    return path.read_text(encoding="utf-8")


class MacroLibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PC-DMIS Macro Library")
        self.geometry("1180x760")
        self.minsize(900, 560)
        self.configure(bg=BG)

        self.entries = load_manifest()
        self.categories = ["All"] + sorted(set(e["category"] for e in self.entries))
        self.active_filter = "All"
        self.selected_id = self.entries[0]["id"] if self.entries else None
        self.active_file_tab = "script"  # or "companion"

        self._setup_style()
        self._build_layout()
        self._refresh_list()
        self._refresh_detail()

    # -------------------------------------------------------------------
    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                         foreground=TEXT, borderwidth=0, rowheight=26, font=SANS_FONT)
        style.map("Treeview", background=[("selected", PANEL_ALT)],
                   foreground=[("selected", ACCENT)])
        style.configure("Treeview.Heading", background=PANEL, foreground=TEXT_DIM,
                         borderwidth=0, font=SANS_FONT)
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL, foreground=TEXT_DIM,
                         padding=(14, 6), font=SANS_FONT)
        style.map("TNotebook.Tab", background=[("selected", PANEL_ALT)],
                  foreground=[("selected", TEXT)])
        style.configure("Filter.TButton", background=PANEL, foreground=TEXT_DIM,
                         borderwidth=1, relief="solid", font=SANS_FONT, padding=(10, 4))
        style.map("Filter.TButton", background=[("active", PANEL_ALT)])
        style.configure("FilterActive.TButton", background="#3a3120", foreground=ACCENT,
                         borderwidth=1, relief="solid", font=SANS_FONT, padding=(10, 4))
        style.configure("Action.TButton", background=PANEL, foreground=TEXT,
                         borderwidth=1, relief="solid", font=SANS_FONT, padding=(10, 6))
        style.configure("Primary.TButton", background=ACCENT, foreground="#1b1204",
                         borderwidth=0, font=SANS_BOLD, padding=(10, 6))

    # -------------------------------------------------------------------
    def _build_layout(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(18, 4))
        tk.Label(header, text="PC-DMIS Macro Library", bg=BG, fg=TEXT,
                  font=(SANS_FONT[0], 16, "bold")).pack(anchor="w")
        tk.Label(header, text="Scripts and command blocks, cross-referenced against "
                              "Hexagon documentation and real working code",
                  bg=BG, fg=TEXT_DIM, font=SANS_FONT).pack(anchor="w")

        banner = tk.Frame(self, bg=CAVEAT_BG, highlightbackground=BORDER, highlightthickness=1)
        banner.pack(fill="x", padx=24, pady=(10, 8))
        tk.Label(banner, text=DISCLAIMER, bg=CAVEAT_BG, fg=CAVEAT_FG, font=SANS_FONT,
                 justify="left", wraplength=1100, anchor="w", padx=12, pady=8).pack(fill="x")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        # --- Sidebar -----------------------------------------------------
        sidebar = tk.Frame(body, bg=PANEL, width=300)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        filter_frame = tk.Frame(sidebar, bg=PANEL)
        filter_frame.pack(fill="x", padx=10, pady=10)
        self.filter_buttons = {}
        for cat in self.categories:
            b = ttk.Button(filter_frame, text=cat, style="Filter.TButton",
                            command=lambda c=cat: self._set_filter(c))
            b.pack(side="left", padx=(0, 6), pady=2)
            self.filter_buttons[cat] = b

        tree_frame = tk.Frame(sidebar, bg=PANEL)
        tree_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        self.tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.tag_configure("high", foreground=OK)
        self.tree.tag_configure("moderate", foreground=MOD)
        self.tree.tag_configure("category", foreground=TEXT_FAINT)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # --- Detail panel --------------------------------------------------
        self.detail = tk.Frame(body, bg=BG)
        self.detail.pack(side="left", fill="both", expand=True, padx=(20, 0))

    # -------------------------------------------------------------------
    def _set_filter(self, cat):
        self.active_filter = cat
        for c, b in self.filter_buttons.items():
            b.configure(style="FilterActive.TButton" if c == cat else "Filter.TButton")
        self._refresh_list()

    def _refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        filtered = [e for e in self.entries
                    if self.active_filter == "All" or e["category"] == self.active_filter]
        last_cat = None
        first_id = None
        for e in filtered:
            if e["category"] != last_cat:
                self.tree.insert("", "end", iid=f"cat::{e['category']}",
                                  text=e["category"], tags=("category",), open=True)
                last_cat = e["category"]
            self.tree.insert(f"cat::{e['category']}", "end", iid=e["id"],
                              text="  " + e["title"], tags=(e["confidence"],))
            if first_id is None:
                first_id = e["id"]
        if self.selected_id not in [e["id"] for e in filtered] and first_id:
            self.selected_id = first_id
        if self.selected_id:
            try:
                self.tree.selection_set(self.selected_id)
                self.tree.see(self.selected_id)
            except tk.TclError:
                pass

    def _on_select(self, _event):
        sel = self.tree.selection()
        if not sel or sel[0].startswith("cat::"):
            return
        self.selected_id = sel[0]
        self.active_file_tab = "script"
        self._refresh_detail()

    # -------------------------------------------------------------------
    def _refresh_detail(self):
        for w in self.detail.winfo_children():
            w.destroy()

        e = next((x for x in self.entries if x["id"] == self.selected_id), None)
        if not e:
            return

        d = self.detail

        tk.Label(d, text=e["category"], bg=BG, fg=TEXT_FAINT, font=MONO_FONT).pack(anchor="w")
        tk.Label(d, text=e["title"], bg=BG, fg=TEXT, font=(SANS_FONT[0], 19, "bold")
                  ).pack(anchor="w", pady=(2, 10))

        badges = tk.Frame(d, bg=BG)
        badges.pack(anchor="w", pady=(0, 14))
        self._badge(badges, e["type"], TEXT_DIM, PANEL)
        conf_color = OK if e["confidence"] == "high" else MOD
        conf_label = "High confidence" if e["confidence"] == "high" else "Moderate confidence"
        self._badge(badges, conf_label, conf_color, "#20302a" if e["confidence"] == "high" else "#332a1a")

        body_wrap = tk.Frame(d, bg=BG)
        body_wrap.pack(fill="both", expand=True)

        canvas = tk.Canvas(body_wrap, bg=BG, highlightthickness=0)
        vscroll = ttk.Scrollbar(body_wrap, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        inner.bind("<Configure>", lambda ev: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", width=760)
        canvas.configure(yscrollcommand=vscroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        vscroll.pack(side="right", fill="y")

        def _wheel(ev):
            canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _wheel)

        self._wrap_label(inner, e["description"], TEXT, (SANS_FONT[0], 12))
        self._wrap_label(inner, e["explanation"], TEXT_DIM, SANS_FONT, pady=(6, 16))

        self._section_title(inner, "Why this confidence rating")
        self._wrap_label(inner, e["confidenceNote"], TEXT_DIM, SANS_FONT, pady=(0, 16))

        self._section_title(inner, "Deployment guide")
        for i, step in enumerate(e["guide"], 1):
            self._wrap_label(inner, f"{i}.  {step}", TEXT, SANS_FONT, pady=(0, 6))

        self._section_title(inner, "Before you rely on this")
        caveat_box = tk.Frame(inner, bg=CAVEAT_BG, highlightbackground=BORDER,
                               highlightthickness=1)
        caveat_box.pack(fill="x", pady=(0, 16))
        self._wrap_label(caveat_box, e["caveats"], CAVEAT_FG, SANS_FONT, padx=14, pady=12)

        self._section_title(inner, "File")

        tabs = tk.Frame(inner, bg=BG)
        tabs.pack(fill="x", pady=(0, 0))
        self._file_tab(tabs, e["filename"], "script")
        if e.get("companion"):
            self._file_tab(tabs, e["companion"], "companion")

        current_filename = e["companion"] if (self.active_file_tab == "companion" and e.get("companion")) else e["filename"]
        content = read_lib_file(current_filename)

        code = tk.Text(inner, height=16, bg=CODE_BG, fg=CODE_FG, font=MONO_FONT,
                        wrap="word", relief="flat", highlightbackground=BORDER,
                        highlightthickness=1, padx=12, pady=12)
        code.insert("1.0", content)
        code.configure(state="disabled")
        code.pack(fill="both", expand=False, pady=(0, 12))

        actions = tk.Frame(inner, bg=BG)
        actions.pack(fill="x", pady=(0, 30))
        ttk.Button(actions, text=f"Export {current_filename}...", style="Primary.TButton",
                   command=lambda: self._export(current_filename, content)).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Copy to clipboard", style="Action.TButton",
                   command=lambda: self._copy(content)).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Open library folder", style="Action.TButton",
                   command=self._open_folder).pack(side="left")

    # -------------------------------------------------------------------
    def _file_tab(self, parent, filename, tab_key):
        active = self.active_file_tab == tab_key
        b = tk.Label(parent, text=filename, bg=PANEL_ALT if active else PANEL,
                     fg=TEXT if active else TEXT_DIM, font=MONO_FONT,
                     padx=12, pady=6, cursor="hand2")
        b.pack(side="left")
        b.bind("<Button-1>", lambda ev, k=tab_key: self._set_file_tab(k))

    def _set_file_tab(self, key):
        self.active_file_tab = key
        self._refresh_detail()

    def _badge(self, parent, text, fg, bg):
        tk.Label(parent, text=text, fg=fg, bg=bg, font=MONO_FONT,
                 padx=10, pady=3).pack(side="left", padx=(0, 8))

    def _section_title(self, parent, text):
        wrap = tk.Frame(parent, bg=BG)
        wrap.pack(fill="x", pady=(18, 8))
        tk.Label(wrap, text=text, bg=BG, fg=TEXT_FAINT, font=MONO_FONT).pack(anchor="w")
        tk.Frame(wrap, bg=BORDER, height=1).pack(fill="x", pady=(6, 0))

    def _wrap_label(self, parent, text, fg, font, padx=0, pady=0):
        lbl = tk.Label(parent, text=text, bg=parent["bg"] if "bg" in parent.keys() else BG,
                        fg=fg, font=font, justify="left", wraplength=740, anchor="w")
        lbl.pack(fill="x", anchor="w", padx=padx, pady=pady)
        return lbl

    # -------------------------------------------------------------------
    def _export(self, filename, content):
        target_dir = filedialog.askdirectory(title="Choose a folder to export to")
        if not target_dir:
            return
        dest = Path(target_dir) / filename
        try:
            dest.write_text(content, encoding="utf-8")
            messagebox.showinfo("Exported", f"Saved to:\n{dest}")
        except OSError as ex:
            messagebox.showerror("Export failed", str(ex))

    def _copy(self, content):
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("Copied", "File content copied to clipboard.")

    def _open_folder(self):
        try:
            if sys.platform.startswith("win"):
                os.startfile(LIBRARY_DIR)  # noqa
            elif sys.platform == "darwin":
                os.system(f'open "{LIBRARY_DIR}"')
            else:
                os.system(f'xdg-open "{LIBRARY_DIR}"')
        except Exception as ex:
            messagebox.showerror("Could not open folder", str(ex))


if __name__ == "__main__":
    app = MacroLibraryApp()
    app.mainloop()
