"""Generate the API reference for gecko-docs at build time.

Run by the ``mkdocs-gen-files`` plugin. Walks the two submodules and emits a
cobrapy-style ``autoapi`` reference as **two parallel trees** plus a name map:

* **MATLAB API (GECKO)** -- one page per ``src/geckomat`` subfolder
  (``change_model``, ``gather_kcats`` ...), each with a *Functions* summary
  table followed by the full help for every function (rendered by the
  ``matlab`` mkdocstrings handler via tree-sitter -- no MATLAB runtime needed).
* **Python API (geckopy)** -- one page per package, same shape, rendered by the
  ``python`` handler (griffe collects from source statically).
* **MATLAB <-> Python** -- a single translation table pairing the two naming
  conventions (``camelCase`` <-> ``snake_case``) by normalised name, for every
  function that exists in both.

Each function gets its own ``## name`` heading (so the summary table can link
to it) followed by a ``:::`` autodoc block. A literate-nav ``SUMMARY.md`` ties
the trees together.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import mkdocs_gen_files

ROOT = Path(__file__).resolve().parent.parent
GECKO_MAT = ROOT / "GECKO" / "src" / "geckomat"
PYPKG = ROOT / "geckopy" / "src" / "geckopy"

# GECKO geckomat subfolders to document, in nav order: (folder, page title).
# Pruned to existing folders at build time by scripts/build_hooks.py / the
# matlab handler.
MATLAB_CATEGORIES = [
    ("change_model", "Build & edit ecModel"),
    ("gather_kcats", "Gather kcats"),
    ("get_enzyme_data", "Enzyme & EC data"),
    ("kcat_sensitivity_analysis", "kcat sensitivity tuning"),
    ("limit_proteins", "Limit proteins"),
    ("model_adapter", "Model adapter"),
    ("utilities", "Utilities"),
]

# Friendly titles for geckopy packages. The ec_model package is geckopy's
# counterpart to geckomat/change_model; adapter to model_adapter.
PY_PACKAGE_TITLES = {
    "ec_model": "Build & edit ecModel",
    "gather_kcats": "Gather kcats",
    "get_enzyme_data": "Enzyme & EC data",
    "kcat_sensitivity_analysis": "kcat sensitivity tuning",
    "limit_proteins": "Limit proteins",
    "adapter": "Model adapter",
    "utilities": "Utilities",
    "databases": "Databases",
    "_toplevel": "Top-level",
}


def norm(name: str) -> str:
    """Normalise a function name for cross-language matching."""
    return re.sub(r"[_\s]", "", name).lower()


def slug(name: str) -> str:
    """Reproduce Python-Markdown's default heading slug for in-page anchors."""
    value = re.sub(r"[^\w\s-]", "", name).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def cell(text: str) -> str:
    """Make a string safe for a single Markdown table cell."""
    return " ".join(text.split()).replace("|", "\\|")


# --------------------------------------------------------------------------- #
# Collect MATLAB functions                                                    #
# --------------------------------------------------------------------------- #
def is_matlab_documentable(path: Path) -> bool:
    """True if the .m file declares a function or a class (not a plain script)."""
    try:
        with path.open(encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                stripped = line.strip()
                if not stripped or stripped.startswith("%"):
                    continue
                return stripped.startswith("function") or stripped.startswith("classdef")
    except OSError:
        return False
    return False


def matlab_summary(path: Path, fname: str) -> str:
    """First descriptive line of a function's MATLAB help block."""
    try:
        with path.open(encoding="utf-8", errors="ignore") as fh:
            lines = fh.readlines()
    except OSError:
        return ""

    help_lines: list[str] = []
    started = False
    for line in lines:
        stripped = line.strip()
        if not started:
            if stripped.startswith("function") or stripped.startswith("classdef"):
                started = True
            continue
        if stripped.startswith("%"):
            help_lines.append(stripped.lstrip("%").strip())
        elif stripped == "" and not help_lines:
            continue
        else:
            break

    cleaned = [h for h in help_lines if h]
    if not cleaned:
        return ""
    # The first help line is often just the function name; strip it.
    first = cleaned[0]
    if first.lower().startswith(fname.lower()):
        rest = first[len(fname):].strip(" -:\t")
        if rest:
            return rest
        if len(cleaned) > 1:
            return cleaned[1]
        return ""
    return first


def collect_matlab() -> dict[str, list[dict]]:
    """category -> sorted list of {name, summary} for documented functions."""
    cats: dict[str, list[dict]] = {}
    for folder, _title in MATLAB_CATEGORIES:
        funcs: dict[str, str] = {}
        base = GECKO_MAT / folder
        for m in base.rglob("*.m"):
            if m.stem == "Contents":
                continue
            if not is_matlab_documentable(m):
                continue
            funcs.setdefault(m.stem, matlab_summary(m, m.stem))
        cats[folder] = [
            {"name": n, "summary": funcs[n]}
            for n in sorted(funcs, key=str.lower)
        ]
    return cats


# --------------------------------------------------------------------------- #
# Collect Python functions and classes                                        #
# --------------------------------------------------------------------------- #
def module_dotted(path: Path) -> str:
    """geckopy/src/geckopy/ec_model/build.py -> geckopy.ec_model.build"""
    rel = path.relative_to(PYPKG.parent)  # relative to src/
    parts = list(rel.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def py_summary(node: ast.AST) -> str:
    """First non-empty line of a node's docstring."""
    doc = ast.get_docstring(node) or ""
    for line in doc.strip().splitlines():
        if line.strip():
            return line.strip()
    return ""


def collect_python() -> list[dict]:
    """List of {name, ident, package, summary} for public top-level objects."""
    objects: list[dict] = []
    for py in PYPKG.rglob("*.py"):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, OSError):
            continue
        dotted = module_dotted(py)
        rel = py.relative_to(PYPKG)
        package = rel.parts[0] if len(rel.parts) > 1 else "_toplevel"
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name.startswith("_"):
                    continue
                ident = f"{dotted}.{node.name}" if dotted else node.name
                objects.append(
                    {
                        "name": node.name,
                        "ident": ident,
                        "package": package,
                        "summary": py_summary(node),
                    }
                )
    return objects


# --------------------------------------------------------------------------- #
# Page rendering                                                              #
# --------------------------------------------------------------------------- #
def render_page(title: str, intro: str, entries: list[dict], handler: str | None) -> str:
    """A cobrapy-style page: summary table, then one section per object."""
    out = [f"# {title}", "", intro, "", "## Functions", ""]
    out += ["| Function | Summary |", "|---|---|"]
    for e in entries:
        out.append(f"| [`{e['name']}`](#{slug(e['name'])}) | {cell(e['summary'])} |")
    out += ["", "## Reference", ""]
    for e in entries:
        out += [f"### {e['name']}", ""]
        if handler:
            out += [f"::: {e['ref']}", f"    handler: {handler}", ""]
        else:
            out += [f"::: {e['ref']}", ""]
    return "\n".join(out) + "\n"


matlab = collect_matlab()
python_objs = collect_python()

# normalised name -> python object ; first definition wins
py_by_norm: dict[str, dict] = {}
for obj in python_objs:
    py_by_norm.setdefault(norm(obj["name"]), obj)

summary: list[str] = ["* [Overview](index.md)"]

# --- MATLAB API tree ------------------------------------------------------- #
summary.append("* MATLAB API (GECKO)")
for folder, title in MATLAB_CATEGORIES:
    funcs = matlab[folder]
    if not funcs:
        continue
    entries = [{"name": f["name"], "summary": f["summary"], "ref": f["name"]} for f in funcs]
    intro = (
        f"MATLAB functions in `GECKO/src/geckomat/{folder}`. Help text is "
        "collected from the source of the tracked branch."
    )
    with mkdocs_gen_files.open(f"api/matlab/{folder}.md", "w") as fh:
        fh.write(render_page(title, intro, entries, handler="matlab"))
    summary.append(f"    * [{title}](matlab/{folder}.md)")

# --- Python API tree ------------------------------------------------------- #
by_package: dict[str, list[dict]] = {}
for obj in python_objs:
    by_package.setdefault(obj["package"], []).append(obj)

summary.append("* Python API (geckopy)")
for package in sorted(by_package, key=lambda p: (p == "_toplevel", PY_PACKAGE_TITLES.get(p, p).lower())):
    objs = sorted(by_package[package], key=lambda o: o["name"].lower())
    title = PY_PACKAGE_TITLES.get(package, package)
    dotted = "geckopy" if package == "_toplevel" else f"geckopy.{package}"
    entries = [{"name": o["name"], "summary": o["summary"], "ref": o["ident"]} for o in objs]
    intro = f"`geckopy` objects in `{dotted}`, collected from the source of the tracked branch."
    with mkdocs_gen_files.open(f"api/python/{package}.md", "w") as fh:
        fh.write(render_page(f"{title} (Python)", intro, entries, handler=None))
    summary.append(f"    * [{title}](python/{package}.md)")

# --- MATLAB <-> Python translation table ----------------------------------- #
pairs: list[tuple[str, str, str, str, str]] = []  # (matlab, folder, python, package, summary)
for folder, _title in MATLAB_CATEGORIES:
    for f in matlab[folder]:
        match = py_by_norm.get(norm(f["name"]))
        if match:
            text = f["summary"] or match["summary"]
            pairs.append((f["name"], folder, match["name"], match["package"], text))

lines = [
    "# MATLAB ↔ Python",
    "",
    "GECKO (MATLAB) and geckopy implement the same functionality. MATLAB uses "
    "`camelCase`, geckopy uses `snake_case`. The table below pairs the functions "
    "that exist in both; click a name to jump to its full reference. Functions "
    "that exist in only one implementation appear in that language's tree but "
    "not here.",
    "",
    f"**{len(pairs)}** paired functions.",
    "",
    "| GECKO (MATLAB) | geckopy (Python) | Summary |",
    "|---|---|---|",
]
for m_name, m_folder, p_name, p_pkg, text in sorted(pairs, key=lambda r: r[0].lower()):
    m_link = f"[`{m_name}`](matlab/{m_folder}.md#{slug(m_name)})"
    p_link = f"[`{p_name}`](python/{p_pkg}.md#{slug(p_name)})"
    lines.append(f"| {m_link} | {p_link} | {cell(text)} |")
with mkdocs_gen_files.open("api/translation.md", "w") as fh:
    fh.write("\n".join(lines) + "\n")
summary.append("* [MATLAB ↔ Python](translation.md)")

# --- literate-nav SUMMARY -------------------------------------------------- #
with mkdocs_gen_files.open("api/SUMMARY.md", "w") as fh:
    fh.write("\n".join(summary) + "\n")
