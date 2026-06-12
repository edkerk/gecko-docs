# API reference

GECKO ships in two implementations that build the **same** enzyme-constrained
metabolic models with the same algorithms:

- **GECKO** — the original **MATLAB** toolbox (`src/geckomat`), built on RAVEN
  and the COBRA Toolbox. Functions use `camelCase` names.
- **geckopy** — the **Python** port, built on cobrapy. Functions use
  `snake_case` names.

The function help on these pages is extracted directly from the source of each
toolbox on the branch tracked by this site, so it stays in sync with the code.

## How these pages are organised

The reference is split into **two parallel trees**, one per language, each
organised by the toolbox's own module layout and each function shown with its
signature, parameters and returns:

- **MATLAB API (GECKO)** — one page per `src/geckomat` category
  (`Build & edit ecModel`, `Gather kcats`, `Limit proteins`, …).
- **Python API (geckopy)** — one page per package, mirroring the same
  categories.

Every page opens with a *Functions* table you can scan, followed by the full
help for each function.

To move between the two implementations, use the **[MATLAB ↔ Python](translation.md)**
table, which maps every paired function `camelCase` ↔ `snake_case` and links to
both references.

## How the two line up

The two toolboxes are deliberately kept aligned. The main differences are
mechanical:

| | GECKO (MATLAB) | geckopy (Python) |
|---|---|---|
| Naming | `camelCase` (`makeEcModel`) | `snake_case` (`make_ec_model`) |
| Returns | multiple outputs `[a,b] = f(...)` | one return; model mutated in place |
| Indexing | 1-based | 0-based |
| Missing data | often a silent default | usually raises |

!!! note "A note on the MATLAB docstrings"
    The Python docstrings are NumPy-style, so they render as structured
    parameter/return tables. GECKO's MATLAB help blocks use the toolbox's own
    `Input:` / `Output:` convention, so they render as faithful help text rather
    than typed tables. The content is the same; only the formatting differs.

Use the navigation to browse either tree, or start from the
[MATLAB ↔ Python](translation.md) table.
