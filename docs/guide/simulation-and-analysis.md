# Simulation and analysis

Both light and full ecModels share a conventional GEM's underlying
structure, an S-matrix with vectors of lower and upper bounds (in Python, an
ordinary `cobra.Model`), so any method that works on a conventional GEM also
works on an ecModel, in both languages, regardless of whether it is a light
or full one. This page covers the simulation and analysis tasks specific to
ecModels; ordinary FBA, media, and solver setup are covered in
[Getting started](getting-started.md) and apply unchanged. An ecModel is
also usable in other constraint-based toolboxes; SBML is the most portable
exchange format for that, and [ecModel YAML format](yaml-format.md) covers
the format this documentation otherwise uses.

## Functions on this page

| MATLAB | Python | |
|---|---|---|
| `setProtPoolSize` | `set_prot_pool_size` | change the protein pool constraint, including turning it off with `Inf` |
| `setParam(..., 'obj', ...)` | `model.objective = ...` | choose the objective: maximize growth, or minimize protein pool usage |
| `mapRxnsToConv` | `map_rxns_to_conv` | map an ecModel flux distribution back onto its starting conventional GEM |
| `getAllowedBounds` / `ecFVA` | `flux_variability_analysis` / `ec_fva` | flux variability, with `ecFVA` mapping the ranges back to the conventional GEM |
| `getSubsetEcModel` | `get_subset_ec_model` | trim a generic ecModel down to a context-specific gene/reaction set |

## The protein pool constraint at different growth rates

An ecModel without proteomics integration is a convenient way to study how
the total protein pool constraint affects metabolism as growth rate changes.
At low growth rates, metabolic activity is low and enzymes are usually
available in excess; at high growth rates, activity is high, and fluxes can
become limited by how much enzyme is available at all.

Comparing a normal ecModel against a copy whose protein pool is unconstrained
(`Inf`) isolates that effect, since the unconstrained copy behaves like a
conventional GEM with respect to protein availability:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel_infProt = setProtPoolSize(ecModel, Inf);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
import math

from geckopy import set_prot_pool_size

set_prot_pool_size(ec_model_inf, p_tot=math.inf)
```
:::
::::

Simulating exchange fluxes across a range of growth rates on both models
shows the difference directly: the unconstrained copy cannot predict the
shift from respiration to fermentation at high growth rate (the Crabtree
effect in yeast), because nothing in it ever runs short of enzyme. Plotting
that comparison needs project-specific code (`plotCrabtree` /
`plot_crabtree` in the `full_ecModel` tutorial bundled with each toolbox,
not part of the general API), since it depends on which exchange reactions
and which reference dataset a given model uses.

:::{admonition} Example output
:class: note
Tuning $k_{cat}$ values (see [Growth-rate tuning](growth-rate-tuning.md))
matters for this comparison too: an ecModel with untuned kcats can fail to
reach realistic growth rates even with the protein pool constraint in place.
In one such comparison, only 13 kcat values needed tuning before the model
exhibited the Crabtree effect: yeast switched from respiration to
fermentation once the protein pool became fully used. The simulated switch
came slightly later than the experimental one (around 0.2 /h simulated vs.
around 0.28 /h observed), suggesting a single enzyme was dominating the
constraint too early; inspecting the top enzyme usages (see [Enzyme usage
and bottlenecks](enzyme-usage-and-bottlenecks.md)) is the way to check that.
:::

## Choosing the objective function

Maximizing growth is the usual objective for FBA on a conventional GEM,
particularly for microbes, and it remains relevant for an ecModel. A second
objective becomes useful once growth is known: minimizing total protein pool
usage, on the assumption that a cell is more likely to use its enzyme
resources efficiently than not.

Maximize growth first:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'obj', params.bioRxn, 1);
sol = solveLP(ecModel);
fprintf('Growth rate that is reached: %.4f /hour\n', abs(sol.f))
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
ec_model.objective = params.bio_rxn
sol = ec_model.optimize()
print(f"Growth rate that is reached: {sol.fluxes[params.bio_rxn]:.4f} /hour")
```
:::
::::

Then fix growth at (99% of, to avoid rounding issues) that value and switch
the objective to minimizing protein pool usage:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'lb', params.bioRxn, 0.99*abs(sol.f));
ecModel = setParam(ecModel, 'obj', 'prot_pool_exchange', 1);
sol = solveLP(ecModel);
fprintf('Minimum protein pool usage: %.2f mg/gDCW\n', abs(sol.f))
```
:::
:::{tab-item} 🐍 Python
:sync: python

cobrapy's dict-form objective takes a coefficient per reaction, so
minimizing `prot_pool_exchange` is a negative weight in an otherwise
ordinary (maximizing) objective:

```python
max_growth = sol.fluxes[params.bio_rxn]
ec_model.reactions.get_by_id(params.bio_rxn).lower_bound = 0.99 * max_growth
ec_model.objective = {
    ec_model.reactions.get_by_id("prot_pool_exchange"): -1.0,
}
sol = ec_model.optimize()
print(f"Minimum protein pool usage: {abs(sol.fluxes['prot_pool_exchange']):.2f} mg/gDCW")
```
:::
::::

This gives a flux distribution with growth at least 99% of the maximum for
that condition, using enzyme resources as efficiently as the model allows.

:::{admonition} Example output
:class: note
```
Growth rate that is reached: 0.4121 /hour
Minimum protein pool usage: 123.75 mg/gDCW
```
:::

## Comparing flux distributions of different models

An ecModel's flux distribution cannot be compared directly against its
starting conventional GEM: building the ecModel changes the network
structure substantially (isozyme splitting, enzyme usage reactions), so the
two need to be mapped onto a common footing first.

Map an ecModel-derived flux distribution back onto its starting conventional
GEM, combining flux from isozymatic reactions and inverted reversible
reactions back into the single reaction they came from:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
sol = solveLP(ecModel);
[mappedFlux, enzUsageFlux, usageEnz] = mapRxnsToConv(ecModel, model, sol.x);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import map_rxns_to_conv

sol = ec_model.optimize()
mapped = map_rxns_to_conv(ec_model, model, sol.fluxes)
mapped_flux, enz_usage_flux, usage_enz = (
    mapped.mapped_flux, mapped.enz_usage_flux, mapped.usage_enz,
)
```

`map_rxns_to_conv` returns a `MapRxnsResult` bundling the same three arrays
under snake_case names.
:::
::::

The resulting `mappedFlux` / `mapped_flux` vector has the same length and
order as a flux vector from the conventional GEM directly, and can be
treated as any other conventional flux vector from that point on.

:::{warning}
The ecModel passed in must actually derive from the conventional GEM passed
alongside it: reactions are matched by identifier, with no check that the
underlying chemical reaction is still the same. Any stoichiometric change
made beyond the enzyme and proteomics constraints themselves, such as
flipping a reaction's directionality or adding a brand-new reaction, breaks
that correspondence without raising an error.
:::

## Evaluating the solution space

A major benefit of an ecModel over a conventional GEM is a smaller solution
space, which flux variability analysis (FVA) makes visible directly. FVA
works the same way on an ecModel as on any other constraint-based model; in
MATLAB, `getAllowedBounds` runs plain FVA on the ecModel's own reaction set,
but for comparing against a conventional GEM's own FVA result, mapping
straight to the conventional model's reaction ids with `ecFVA` is more
convenient.

Apply the same exchange flux constraints to three models with a shared basis
for comparison: an ecModel with proteomics integrated (see [Proteomics
integration](proteomics-integration.md)), the same ecModel without
proteomics, and the underlying conventional GEM:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModelProt = constrainFluxData(ecModelProt, fluxData, 1, 'max', 'loose');
ecModel     = constrainFluxData(ecModel, fluxData, 1, 'max', 'loose');
model       = constrainFluxData(model, fluxData, 1, 'max', 'loose');

minFlux = zeros(numel(model.rxns), 3);
maxFlux = minFlux;
[minFlux(:,1), maxFlux(:,1)] = ecFVA(model, model);
[minFlux(:,2), maxFlux(:,2)] = ecFVA(ecModel, model);
[minFlux(:,3), maxFlux(:,3)] = ecFVA(ecModelProt, model);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_flux_data_constraints
from geckopy.utilities import ec_fva

for m in (model, ec_model, ec_model_prot):
    apply_flux_data_constraints(
        m, flux_data,
        condition=0, max_min_growth="max", loose_strict_flux="loose",
    )

fva_bare = ec_fva(model, model)
fva_full = ec_fva(ec_model, model)
fva_prot = ec_fva(ec_model_prot, model)
```

`ec_fva` returns a DataFrame indexed by the conventional model's reaction
ids, with `min_flux` / `max_flux` columns, so there is no need to
pre-allocate a matrix as in MATLAB.
:::
::::

:::{warning} Performance
With the default open-source solver (GLPK), `ec_fva` at yeast-GEM scale
(around 4,000 canonical reactions times 3 models times 2 LPs each) can take
well over an hour. Configure a faster solver first
(`ec_model.solver = "gurobi"`, license permitting) before running this at
genome scale, or expect a long run.
:::

### Example output

Visualizing the resulting ranges as a cumulative distribution
(`plotEcFVA` / a project-specific `plot_ec_fva` helper) makes the reduction
in solution space visible directly: the ecModel's median flux variability
runs more than fourfold lower than the conventional GEM's, and over 15% of
the conventional GEM's reactions carry very high flux variability (around
1,000 mmol/gDCWh) that is entirely absent from either ecModel:

| Model | Median flux variability |
|---|---|
| Conventional GEM | 3.104 |
| ecModel, no proteomics | 0.355 |
| ecModel, with proteomics | 0.00325 |

## Context-specific models

ecModels reconstructed for higher organisms, such as humans, should not
start from the generic model directly, but from a context-specific model
built with an omics-integration method such as tINIT. There are two ways to
combine contextualization with enzyme-constraining:

1. Contextualize the generic model first, then convert the result to an
   ecModel.
2. Reconstruct a generic ecModel first, then contextualize that.

The second path is faster, and any contextualized ecModel derived from the
same generic ecModel carries the same $k_{cat}$ data, which matters when
reconstructing hundreds of single-cell ecModels from one generic model.

Trim a generic ecModel down to the gene and reaction set of a smaller,
already-contextualized conventional model (both must derive from the same
starting GEM):

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecHT29 = getSubsetEcModel(ecModel, HT29);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import get_subset_ec_model

ec_ht29 = get_subset_ec_model(ec_model, ht29)
```

Matches by canonicalized reaction id and returns a fresh `EcModel` without
mutating `ec_model`.
:::
::::

### Example output

Contextualization and enzyme constraints each shrink the reachable growth
rate on their own, and combine when applied together, for example comparing
maximum growth rates between an unconstrained context-specific GEM, a
generic ecModel, and a context-specific ecModel derived from it:

```
Growth rate in HT29-GEM:      149.97  /hour
Growth rate in ecHuman-GEM:     0.122 /hour
Growth rate in ecHT29-GEM:      0.086 /hour
```

The unconstrained context-specific model's growth rate (149.97 /h) is not
biologically meaningful on its own, since carbon uptake is unconstrained
there; it establishes only that the network stoichiometry allows fast
growth, so the much lower ecModel numbers come from the enzyme constraints
and the contextualization, not from a stoichiometric bottleneck.

## See also

- [GECKO light vs. full ecModels](gecko-light.md), for the runtime and
  accuracy trade-off between the two ecModel layouts.
- [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md), what a
  full ecModel's enzyme usage reactions add on top of the analyses here.
- [Proteomics integration](proteomics-integration.md), constructing the
  proteomics-constrained ecModel used in the solution-space comparison above.
- [API reference](../api/index.md) and [MATLAB ↔ Python](../matlab-vs-python.md)
  for the full signature of every function on this page.
