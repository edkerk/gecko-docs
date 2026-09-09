# GECKO vs. geckopy

:::{note} Looking for a specific function?
The [MATLAB vs Python](matlab-vs-python.md) table pairs every function that
exists in both, and links straight to the reference entry for each. This
page is the narrative comparison; that page is the lookup.
:::

GECKO exists as two independent implementations:

- **GECKO**: the original MATLAB toolbox, built on the RAVEN toolbox and the
  COBRA Toolbox.
- **geckopy**: the Python port, built on
  [cobrapy](https://cobrapy.readthedocs.io/en/latest/), so a model is a `cobra.Model`
  and the wider Python ecosystem works on it directly.

Both build the same enzyme-constrained models from the same algorithms and
write the same on-disk YAML format. Across the 138 functions tracked between
the two toolboxes, 47 are implemented at parity on both sides. Only one
MATLAB function has no Python counterpart yet: `bayesianSensitivityTuning`,
GECKO's ABC-SMC kcat-tuning sampler, which is paused rather than abandoned
(geckopy uses CMA-ES for the same job in the meantime). In the other
direction, five geckopy functions have no MATLAB counterpart yet, including
two OpenKineticsPredictor REST helpers already written on an unmerged MATLAB
branch. In that narrow sense, geckopy is ahead in places, not behind: both
are current, converged implementations of the same algorithms, not an
established original and a catching-up port.

## Which one should you use?

Neither is a reduced version of the other, so the right choice usually
depends on the rest of your code, not on the toolbox itself.

**Use geckopy** if the surrounding code is Python, if you want the model to
be a `cobra.Model` that every cobrapy tool accepts without conversion, or if
you need reproducible environments and CI.

**Use GECKO** if the surrounding code is MATLAB, or if your workflow already
depends on RAVEN or the COBRA Toolbox.

**Either** covers the full core pipeline: structure expansion, kcat
integration, model tuning, proteomics integration, simulation and analysis.
Where both have a function, the [mapping table](matlab-vs-python.md) names
the pair; where only one does, the sections below say which and why.

## At a glance

| | GECKO (MATLAB) | geckopy (Python) |
|---|---|---|
| Model toolbox | RAVEN + COBRA Toolbox | cobrapy + raven-toolbox |
| Model object | RAVEN struct with an `ec` field | `EcModel(cobra.Model)` with an `.ec` dataclass |
| Per-entity classes | none, parallel cell arrays | `cobra.{Metabolite,Reaction,Gene}` instances |
| Per-enzyme accessor | indexing into `model.ec.enzymes{i}` | `Enzyme` proxy: `model.enzymes.get_by_id("P00350")` |
| Adapter | `ModelAdapter` classdef + `ModelAdapterManager` | `ModelAdapter` + `model_adapter.toml` (pydantic-validated) |
| Default adapter | global `ModelAdapterManager.getDefault()` | none; pass `adapter=` or set `model.adapter` |
| Return style | `[a,b,c] = f(...)` | single return; model mutated in place |
| Naming | `camelCase` | `snake_case` |
| Indexing | 1-based | 0-based |
| Missing data | often a silent default | usually a raised exception |
| Tabular output | cell arrays / structs | `pandas.DataFrame` |
| HTTP (BRENDA/KEGG/UniProt/OKP) | `webread`/`webwrite` | `requests` |
| On-disk format | RAVEN/cobrapy YAML (+ SBML) | RAVEN/cobrapy YAML (SBML ecModel I/O dropped in `0.1.0a2`) |

A model saved by either side loads in the other: the two toolboxes read and
write the same YAML schema.

## Changing the case does not give the matching name

MATLAB uses `camelCase` and Python uses `snake_case`, but changing only the
case usually produces a name that does not exist. Some renames go beyond
case, either for clarity or because the function's role changed:

| MATLAB | geckopy |
|---|---|
| `selectKcatValue` | `apply_kcat_list` |
| `getKcatAcrossIsozymes` | `fill_kcats_from_isozymes` |
| `mergeDLKcatAndFuzzyKcats` | `merge_kcats` (generalized to any number of sources) |
| `writeOpenKineticsPredictorInput` / `readOpenKineticsPredictorOutput` | `submit_open_kinetics_predictor` / `fetch_open_kinetics_predictor` (REST client, replaces the file round-trip) |

Check the [mapping table](matlab-vs-python.md) rather than guessing; it also
records the deprecated aliases geckopy kept for one minor cycle after a
rename.

## What only one side has

### Deliberately MATLAB-only

Five functions stay MATLAB-only by design:

| MATLAB | Reason |
|---|---|
| `ModelAdapterManager` | geckopy has no global default adapter; pass `adapter=` explicitly or set `model.adapter`, so there is no manager to port. |
| `plotEcFVA` | Plot directly from the `ec_fva` DataFrame with matplotlib or seaborn instead. |
| `updateProtPool` | Obsolete since GECKO 3.2.0; `set_prot_pool_size` supersedes it on both sides. |
| `writeOpenKineticsPredictorInput` | Replaced by the REST client (`submit_open_kinetics_predictor`); the request payload is built internally. |
| `readOpenKineticsPredictorOutput` | Replaced by the REST client (`fetch_open_kinetics_predictor`); the response is parsed internally. |

### Deliberately Python-only

56 functions exist only in geckopy, but most are not new capability: they
are return types and loaded-data wrappers that Python's language design
calls for and MATLAB's does not. MATLAB GECKO returns several positional
outputs (`[model, a, b] = f(...)`) and passes parallel cell arrays and
structs between functions; geckopy returns one dataclass per call and wraps
loaded data (`BrendaData`, `PhylDist`, `FluxData`, and others) in dataclasses
instead. A representative sample:

| Python | Kind |
|---|---|
| `geckopy.TunedKcatsResult`, `geckopy.AddNewRxnsResult`, `geckopy.EnzymeUsageResult` | Return-type dataclasses, one per multi-output MATLAB call. |
| `geckopy.BrendaData`, `geckopy.PhylDist`, `geckopy.FluxData` | Loaded-data dataclasses, replacing MATLAB's structs and cell arrays. |
| `geckopy.adapter.ComplexParams`, `geckopy.adapter.KeggParams` | Adapter parameter groups; MATLAB reads the same data off `ModelAdapter` classdef properties. |
| `geckopy.ec_model.pipeline.add_protein_usage_reactions` and other pipeline steps | Build-pipeline steps exported so callers can reuse or reorder them; MATLAB keeps the equivalent logic inline in `makeEcModel.m`. |
| `geckopy.load_phyl_dist`, `geckopy.load_uniprot_tsv` | Explicit data loaders; MATLAB reads the same files inline inside the function that consumes them. |
| `geckopy.Enzyme` | The per-enzyme proxy object. MATLAB indexes into parallel cell arrays instead, so there is nothing to port. |

None of these 56 functions represent capability MATLAB lacks; each has a
MATLAB-side equivalent expressed a different way (a struct field, an inline
block, a positional output). The functions that are genuinely new algorithms
rather than idiom differences are the three queued for MATLAB below.

## Where MATLAB and geckopy have diverged, and might converge

Beyond the deliberate, permanent differences above, the parity ledger tracks
functions that exist on only one side today but are candidates to close the
gap:

- **Queued for Python** (1 function): `bayesianSensitivityTuning`. The
  design for a ported version exists; the work is paused, not abandoned.
- **Queued for MATLAB** (5 functions): `fetch_open_kinetics_predictor` and
  `submit_open_kinetics_predictor` already exist as MATLAB code on an
  unmerged branch and close this row once merged;
  `get_enzyme_bottlenecks`, `pfba_enzymes`, and `relax_proteomics_greedy`
  are new algorithms developed in Python that have not been ported back to
  MATLAB.

See the [MATLAB vs Python](matlab-vs-python.md) table for the full
function-by-function list, including every parity, deprecated-alias, and
`[3→4]`-marked entry.
