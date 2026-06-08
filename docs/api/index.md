# API reference

GECKO ships in two implementations that build the **same**
enzyme-constrained models with the same algorithms and the same on-disk
format:

- **GECKO** — the original **MATLAB** toolbox (`src/geckomat`), built on
  RAVEN and the COBRA Toolbox.
- **geckopy** — the **Python** port, built on cobrapy.

This reference documents both side by side. The function docstrings are
extracted directly from the source of each toolbox, so what you read here
is always in sync with the code on each project's `main` branch.

## How the two line up

The two toolboxes are deliberately kept aligned. The main differences are
mechanical:

| | GECKO (MATLAB) | geckopy (Python) |
|---|---|---|
| Naming | `camelCase` (`makeEcModel`) | `snake_case` (`make_ec_model`) |
| Returns | multiple outputs `[a,b] = f(...)` | one return; model mutated in place |
| Indexing | 1-based | 0-based |
| Missing data | often a silent default | usually raises |

Every ported Python function names its MATLAB origin in its docstring
(`Ported from GECKO MATLAB: <path>`), and intentional behavioural
differences are flagged with `MATLAB-COMPAT:` notes. See
[Migrating from GECKO (MATLAB) to geckopy](../introduction.md) for the
narrative version.

## How to read these pages

Each function is shown with both implementations in tabs — click between
them:

=== "Python · geckopy"

    ```python
    from geckopy import make_ec_model
    ```

=== "MATLAB · GECKO"

    ```matlab
    model = makeEcModel(model);
    ```

!!! note "A note on the MATLAB docstrings"

    The Python docstrings are NumPy-style, so they render as structured
    parameter/return tables. GECKO's MATLAB help blocks use the toolbox's
    own `Input:` / `Output:` convention, so they render as faithful help
    text rather than typed tables. The content is the same; only the
    formatting differs.

## Reference by pipeline stage

The reference is organised by the stages of a typical workflow, mirroring
the subpackage layout shared by both toolboxes:

| Stage | MATLAB (`src/geckomat`) | Python (`geckopy`) |
|---|---|---|
| [Build an ecModel](build.md) | `change_model/` | `ec_model`, pipeline edits |
| [Gather kcats](gather-kcats.md) | `gather_kcats/` | `gather_kcats` |
| [Enzyme & EC data](enzyme-data.md) | `get_enzyme_data/` | `get_enzyme_data`, `databases` |
| [kcat sensitivity tuning](kcat-sensitivity.md) | `kcat_sensitivity_analysis/` | `kcat_sensitivity_analysis` |
| [Limit proteins](limit-proteins.md) | `limit_proteins/` | `limit_proteins` |
| [Simulation & utilities](simulation-utilities.md) | `utilities/` | `utilities` |
| [Model adapter](adapter.md) | `model_adapter/` | `adapter` |
