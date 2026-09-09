"""Shared index of the two toolboxes' public APIs, collected from submodule source.

Both the API-reference generator (``gen_api_pages_sphinx.py``) and any future
name checker need to know which functions actually exist in GECKO (MATLAB)
and geckopy (Python). Collecting that in one place means the prose can be
validated against exactly the same index the reference pages are built from,
so a function name that no longer resolves cannot slip through in one while
the other is regenerated.

Collection is static in both languages: ``.m`` files are read as text and
Python modules are parsed with ``ast``. Neither MATLAB nor an installed
geckopy is required.
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The submodules are the source of truth for a real build. For local work they
# can be pointed elsewhere -- e.g. at a working checkout of either toolbox --
# which is useful when a submodule cannot be moved to the tracked commit.
GECKO = Path(os.environ.get("GECKO_DOCS_GECKO_SRC", ROOT / "GECKO" / "src"))
PYPKG = Path(
    os.environ.get(
        "GECKO_DOCS_PYTHON_SRC", ROOT / "geckopy" / "src" / "geckopy"
    )
)

# GECKO src categories to document, in nav order: (folder, page title). GECKO
# dropped the src/geckomat nesting level and split what used to be a single
# "utilities" catch-all into several categories. Pruned to existing folders
# at build time; "deprecated" (backward-compat aliases, e.g. selectKcatValue
# for assignKcatValues) and "dlkcat-gecko" (the Python/Docker DLKcat runner,
# not MATLAB) are intentionally excluded.
MATLAB_CATEGORIES = [
    ("change_model", "Build & edit ecModel"),
    ("download_databases", "Download databases"),
    ("enzyme_usage", "Enzyme usage"),
    ("flux_analysis", "Flux analysis"),
    ("gather_kcats", "Gather kcats"),
    ("get_enzyme_data", "Enzyme & EC data"),
    ("io", "Input / output"),
    ("kcat_tuning", "kcat sensitivity tuning"),
    ("limit_proteins", "Limit proteins"),
    ("model_adapter", "Model adapter"),
    ("utilities", "Utilities"),
]

# Friendly titles for geckopy packages. ec_model is geckopy's counterpart to
# change_model; adapter to model_adapter.
PY_PACKAGE_TITLES = {
    "ec_model": "Build & edit ecModel",
    "gather_kcats": "Gather kcats",
    "get_enzyme_data": "Enzyme & EC data",
    "kcat_tuning": "kcat sensitivity tuning",
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
def is_matlab_function(path: Path) -> bool:
    """True if the .m file declares a function (i.e. not a plain script).

    Read as utf-8-sig: some of GECKO's .m files carry a UTF-8 byte-order mark,
    and a leading U+FEFF is not whitespace to ``str.strip()``, so the opening
    ``function`` line would not be recognised and the file would be indexed as
    a script -- dropping it from the API reference without any error.
    """
    try:
        with path.open(encoding="utf-8-sig", errors="ignore") as fh:
            for line in fh:
                stripped = line.strip()
                if not stripped or stripped.startswith("%"):
                    continue
                return stripped.startswith("function")
    except OSError:
        return False
    return False


def matlab_summary(path: Path, fname: str) -> str:
    """First descriptive line of a function's MATLAB help block."""
    try:
        with path.open(encoding="utf-8-sig", errors="ignore") as fh:
            lines = fh.readlines()
    except OSError:
        return ""

    help_lines: list[str] = []
    started = False
    for line in lines:
        stripped = line.strip()
        if not started:
            if stripped.startswith("function"):
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
        base = GECKO / folder
        for m in base.rglob("*.m"):
            if m.stem == "Contents":
                continue
            if not is_matlab_function(m):
                continue
            funcs.setdefault(m.stem, matlab_summary(m, m.stem))
        cats[folder] = [
            {"name": n, "summary": funcs[n]}
            for n in sorted(funcs, key=str.lower)
        ]
    return cats


def collect_matlab_all() -> dict[str, str]:
    """Every GECKO function name -> the category folder it lives in.

    Unlike :func:`collect_matlab` this also walks the folders that are not
    part of the documented category list, so a name checker recognises a
    function that exists in the toolbox but has no reference page.
    """
    found: dict[str, str] = {}
    for m in GECKO.rglob("*.m"):
        rel = m.relative_to(GECKO)
        if rel.parts[0] in {"dlkcat-gecko"}:
            continue
        if m.stem == "Contents" or not is_matlab_function(m):
            continue
        found.setdefault(m.stem, rel.parts[0])
    return found


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
                summary = py_summary(node)
                # geckopy keeps a backward-compat alias for the original
                # MATLAB name alongside its canonical replacement in the same
                # module (e.g. get_ec_from_database next to
                # fill_eccodes_from_database), each marked with a docstring
                # starting "Deprecated alias for ...". MATLAB's own
                # backward-compat aliases live in a separate excluded
                # deprecated/ folder; Python's have no such physical
                # separation, so they are excluded here by convention
                # instead. Skipping them also keeps norm()-based matching
                # from pairing a MATLAB name with the deprecated shim that
                # happens to share its transliterated spelling.
                if summary.startswith("Deprecated"):
                    continue
                ident = f"{dotted}.{node.name}" if dotted else node.name
                objects.append(
                    {
                        "name": node.name,
                        "ident": ident,
                        "package": package,
                        "summary": summary,
                    }
                )
    return objects
