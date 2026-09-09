# Guide

Short, task-focused pages: one job per page, in **MATLAB and Python side by
side**. Start at [Introduction](introduction.md) if the ecModel concept is
new, or [Getting started](getting-started.md) to jump straight into loading
a model, and read on from there, or go directly to whichever task is at
hand.

:::{admonition} GECKO 4.0.0b1
:class: important
This Guide documents GECKO 4, a pre-release still under development. Pages
call out functions that are new in GECKO 4 and were not part of the
published GECKO 3.0 Nature Protocols pipeline; see [GECKO 3 →
GECKO 4](../gecko3-to-gecko4.md) for the full list of changes, and for how
to stay on GECKO 3 if a workflow depends on its behavior.
:::

:::{admonition} MATLAB and Python
:class: info
Every task page shows both languages side by side: GECKO (MATLAB), built on
RAVEN, and geckopy (Python), built on cobrapy. Function names differ only
mechanically between the two (`camelCase` vs. `snake_case`); see
[MATLAB ↔ Python](../matlab-vs-python.md) for the full name mapping, and
[API reference](../api/index.md) for every function's signature.
:::

## Pages

**Foundations**

1. [Introduction](introduction.md), what an ecModel is and how enzyme
   constraints are added to a conventional GEM.
2. [Getting started](getting-started.md), install GECKO or geckopy and load
   a first model.
3. [Building an ecModel](building-ec-model.md), expand a conventional GEM
   into ecModel structure.

**Building the ecModel**

4. [GECKO light vs. full ecModels](gecko-light.md), the two ecModel layouts,
   what light gives up, and when to choose each.
5. [Gathering kcat values](gathering-kcats.md), collect turnover numbers from
   BRENDA and DLKcat.
6. [Applying kcat values](applying-kcats.md), write collected kcat values
   into the ecModel's enzyme constraints.

**Tuning**

7. [Growth-rate tuning](growth-rate-tuning.md), close the gap between a
   freshly built ecModel's growth rate and the organism's actual one.
8. [Tuning against experimental data](tuning-against-experimental-data.md),
   curate the kcat values tuning identified as limiting.

**Proteomics**

9. [Proteomics integration](proteomics-integration.md), constrain individual
   enzyme concentrations from measured proteomics data.
10. [Relaxing overconstrained proteomics](relaxing-constraints.md), two ways
    to loosen proteomics constraints that leave the ecModel unable to reach
    its intended growth rate.

**Simulation and analysis**

11. [Simulation and analysis](simulation-and-analysis.md), objective choice,
    flux variability, mapping ecModel fluxes back to a conventional GEM, and
    context-specific ecModels.
12. [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md), which
    enzymes a solution uses, and which ones are actually limiting the
    objective.

**Reference**

13. [ecModel YAML format](yaml-format.md), the file format both toolboxes
    read and write, field by field.

## Approximate timing

Rough wall-clock time for a first pass through each stage of work, on a
genome-scale model such as yeast-GEM. Actual timing depends heavily on model
size, internet connection, and which solver is configured.

| Pages | Approx. timing | Notes |
|---|---|---|
| Getting started, Building an ecModel | 15 min | |
| GECKO light vs. full, Gathering kcats, Applying kcats | 1 h | DLKcat prediction accounts for most of it |
| Growth-rate tuning, Tuning against experimental data | 15 min | |
| Proteomics integration | 15 min | |
| Relaxing overconstrained proteomics | 15 min | can take longer with lower-quality proteomics data, more enzymes need flexibilizing |
| Simulation and analysis | 3 h | ecFVA at genome scale accounts for most of it, and is far shorter with a commercial solver configured |
| Enzyme usage and bottlenecks | 15 min | |

## See also

- [GECKO 3 → GECKO 4](../gecko3-to-gecko4.md), the full list of GECKO 4
  changes against the published protocol.
- [API reference](../api/index.md), generated function documentation for
  both toolboxes.
- [MATLAB ↔ Python](../matlab-vs-python.md), the function name mapping
  between GECKO and geckopy.

```{toctree}
:hidden:
:caption: Installation

../installation/index
```

```{toctree}
:hidden:
:caption: Guide

introduction
getting-started
building-ec-model
gecko-light
gathering-kcats
applying-kcats
growth-rate-tuning
tuning-against-experimental-data
proteomics-integration
relaxing-constraints
simulation-and-analysis
enzyme-usage-and-bottlenecks
yaml-format
```
