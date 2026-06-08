# Stage 5: Simulation and analysis

!!! info "Timing"
    Approximately 3 hours (Steps 66-79). Step 74 accounts for most of the time.

!!! note "ecModels behave like conventional GEMs"
    Both light and full ecModels produced by GECKO share the same underlying
    structure of an S-matrix combined with vectors of lower and upper bounds, so
    they can be simulated and analyzed in the same way. The
    [RAVEN toolbox functions](stage3-model-tuning.md#box-2-selection-of-raven-toolbox-functions)
    apply to both conventional GEMs and ecModels. ecModels are also suitable for
    simulations in other constraint-based toolboxes, where SBML files are the
    best way to exchange them
    ([Stage 1, Step 14](stage1-structure-expansion.md#save-the-ecmodel)).

## Simulate exchange fluxes at various growth rates

The ecModel without proteomics integration can be used to investigate the effect
of the total protein pool constraint on metabolism at different growth rates. At
low growth rates, cellular metabolic activity is low and enzymes are probably
present in copious amounts. At high growth rates, metabolic activity is high, so
the high fluxes may become constrained by the amount of available enzyme.

**Step 66.** Load an ecModel without proteomics integration:

```matlab
ecModel = loadEcModel('ecYeastGEM.yml');
```

**Step 67.** The `full_ecModel` tutorial provides a custom `plotCrabtree`
function that predicts fluxes at a range of growth rates and plots selected
exchange reactions, together with experimentally measured fluxes. Navigate to
the `full_ecModel/code` folder and run it; the plot is saved in the output
subfolder:

```matlab
cd(fullfile(params.path, 'code'))
[fluxes, gRate] = plotCrabtree(ecModel);
saveas(gcf, fullfile(params.path, 'output', 'crabtree.tiff'))
```

!!! warning "Critical step"
    To run this function you must first navigate to the `full_ecModel/code`
    folder, because it is a custom function distributed specifically for this
    ecModel and is not part of the general GECKO code.

**Step 68.** To demonstrate that conventional GEMs cannot capture this effect,
perform the simulations with an ecModel whose protein pool exchange reaction is
not constrained, mimicked by defining an infinite cellular protein:

```matlab
ecModel_infProt = setProtPoolSize(ecModel, Inf);
[fluxes, gRate] = plotCrabtree(ecModel_infProt);
saveas(gcf, fullfile(params.path, 'output', 'crabtree_infProt.tiff'))
```

## Choose the objective function

A common consideration is the choice of objective function. In FBA of
conventional GEMs, particularly when simulating microbes, maximization of growth
is often used. This remains relevant for ecModels but is joined by another
critical objective: once the reachable growth rate is observed, the ecModel
should be minimized for the total protein pool reaction, based on the assumption
that the cell is more likely to present flux distributions that make efficient
use of protein resources.

**Step 69.** Set maximization of biomass production as the objective before
running FBA:

```matlab
ecModel = setParam(ecModel, 'obj', params.bioRxn, 1);
sol = solveLP(ecModel);
fprintf('Growth rate that is reached: %.4f /hour\n', abs(sol.f))
```

**Step 70.** Set the reached growth rate as the lower bound for the biomass
reaction, change the objective to minimizing the protein pool exchange reaction
([Stage 3, Step 41](stage3-model-tuning.md#too-tight-protein-pool-constraint)),
and run FBA again. To avoid numeric issues from rounding, use 99% of the growth
rate as the lower bound:

```matlab
ecModel = setParam(ecModel, 'lb', params.bioRxn, 0.99*abs(sol.f));
ecModel = setParam(ecModel, 'obj', 'prot_pool_exchange', 1);
sol = solveLP(ecModel);
fprintf('Minimum protein pool usage: %.2f mg/gDCW\n', abs(sol.f))
```

This yields the flux distribution with a growth rate at least 99% of the maximum
in that condition, with the most efficient enzyme resource allocation.

## Enzyme usage

A unique output from full ecModel simulations is enzyme usage, either as:

- **Absolute usage**, corresponding to the flux through the respective
  `usage_prot` reactions; or
- **Capacity usage**, where the absolute usage is divided by the available
  protein, as indicated by the constraints of the `usage_prot` reactions (not
  necessarily the values in `ecModel.ec.concs`; see
  [Stage 4, Step 64](stage4-proteomics.md#flexibilize-measured-protein-concentrations)).

Enzyme usages are particularly insightful when the total protein constraint is
limiting, as they detail the resource balance allocation across all enzymes. As
an example, the enzyme usage during the Crabtree simulation (Step 67) can be
evaluated to see which enzyme contributes most to the total protein constraint.

**Step 71.** Perform a simulation at a growth rate of 0.25 h^-1 while minimizing
glucose uptake, then report the top ten highly used enzymes:

```matlab
ecModel = setParam(ecModel, 'obj', 'r_1714', 1);
ecModel = setParam(ecModel, 'lb', params.bioRxn, 0.25);
sol = solveLP(ecModel, 1);
usageData = enzymeUsage(ecModel, sol.x);
usageReport = reportEnzymeUsage(ecModel, usageData);
usageReport.topAbsUsage
```

## Compare flux distributions of different models

Flux distributions from ecModels cannot be directly compared with those from the
starting GEM, because the structure is changed substantially by `makeEcModel`.
It is therefore essential to map the fluxes between the two formulations.

**Step 72.** Map an ecModel-derived flux distribution back to its starting
conventional GEM with `mapRxnsToConv`, where flux values from isozymatic
reactions and inverted reversible reactions are combined:

```matlab
sol = solveLP(ecModel);
[mappedFlux, enzUsageFlux, usageEnz] = mapRxnsToConv(ecModel, model, sol.x);
```

The resulting `mappedFlux` vector has the same number and order of fluxes as
would be obtained from FBA on the conventional GEM, and can be treated as any
other conventional flux vector.

!!! warning "Critical step"
    When mapping reactions back to a conventional GEM, the ecModel must indeed
    be derived from that conventional GEM, because reactions are mapped by their
    identifiers without checking whether the chemical reactions are identical.
    Any larger stoichiometric changes made beyond applying enzyme and proteomics
    constraints will not be correctly reflected. Examples include changing a
    reaction's directionality or adding completely new reactions.

## Evaluate solution space

A major benefit of ecModels is the reduced solution space compared with
conventional GEMs, which can be evaluated by FVA. Common methods such as FVA
work as well with ecModels as with any other constraint-based model. In RAVEN
this can be done with `getAllowedBounds`, but for comparison with non-ecModel
FVA results it is convenient to map directly to the original model via the
`ecFVA` function.

**Step 73.** Apply the same exchange flux constraints to three models: an
ecModel with proteomics integrated (from
[Stage 4, Step 64](stage4-proteomics.md#flexibilize-measured-protein-concentrations),
here `ecModelProt`), the same ecModel without proteomics (from
[Stage 3, Step 50](stage3-model-tuning.md#evaluate-the-tuned-kcat-values), here
`ecModel`), and their corresponding conventional GEM:

```matlab
ecModelProt = constrainFluxData(ecModelProt, fluxData, 1, 'max', 'loose');
ecModel = constrainFluxData(ecModel, fluxData, 1, 'max', 'loose');
model = constrainFluxData(model, fluxData, 1, 'max', 'loose');
```

The ecFVA results from all three models are kept in `minFlux` and `maxFlux`
matrices, first defined as zeros before being populated.

**Step 74.** Run `ecFVA`:

```matlab
minFlux = zeros(numel(model.rxns),3);
maxFlux = minFlux;
[minFlux(:,1), maxFlux(:,1)] = ecFVA(model, model);
[minFlux(:,2), maxFlux(:,2)] = ecFVA(ecModel, model);
[minFlux(:,3), maxFlux(:,3)] = ecFVA(ecModelProt, model);
```

**Step 75.** Define a range of allowable fluxes for each reaction by subtracting
the minimum flux from the maximum flux, and visualize the resulting ranges as a
cumulative distribution:

```matlab
plotEcFVA(minFlux, maxFlux);
saveas(gca, fullfile(params.path, 'output', 'ecFVA.pdf'))
```

## Compare full and light ecModel simulations

**Step 76.** To demonstrate the similarity between full and light ecModel
simulations, a custom function in `tutorials/full_ecModel/code` generates light
and full ecModels for yeast-GEM populated with identical $k_{cat}$ values and
performs FBA with maximizing growth rate on each. Map the flux distributions
back to the conventional GEM for comparison, presented in a scatter plot and the
two mapped flux vectors:

```matlab
cd(fullfile(findGECKOroot, 'tutorials', 'full_ecModel', 'code'))
[fluxLight, fluxFull] = plotlightVSfull();
```

**Step 77.** Compare the ratio between the two flux distributions. Any flux that
deviates more than an arbitrary 0.1% between the two ecModels can be considered
different:

```matlab
fluxRatio = fluxFull ./ fluxLight;
nonsimilarFlux = abs(fluxRatio - 1) > 0.001;
model.rxnNames(nonsimilarFlux)
```

## Context-specific models

While ecModels can be reconstructed for higher organisms such as humans, the
starting GEM should not be the generic model but rather a context-specific model
based on omics data, by approaches such as tINIT. There are two paths to obtain
context-specific ecModels:

1. Contextualize the generic model and then convert it to an ecModel.
2. Reconstruct a generic ecModel and then contextualize it.

The second path has the benefit that any contextualized ecModel derived from the
same generic ecModel has the same $k_{cat}$ data, and it is much faster, which
becomes essential when reconstructing hundreds of single-cell ecModels. The
demonstration uses the human-GEM in `tutorials/light_ecModel`, where `HT29` is a
context-specific model of the human colorectal adenocarcinoma cell line HT-29
and `ecModel` is the generic ecModel, both derived from Human-GEM.

**Step 78.** Reconstruct the context-specific ecModel:

```matlab
ecHT29 = getSubsetEcModel(ecModel, HT29);
```

**Step 79.** As a simple demonstration that making a model context specific and
considering enzyme constraints both affect the predicted fluxes, compare the
maximum growth rates between the different models:

```matlab
sol = solveLP(HT29);
fprintf('Growth rate in HT29-GEM: %.3f /hour.\n', abs(sol.f))
sol = solveLP(ecModel);
fprintf('Growth rate in ecHuman-GEM: %.3f /hour.\n', abs(sol.f))
sol = solveLP(ecHT29);
fprintf('Growth rate in ecHT29-GEM: %.3f /hour.\n', abs(sol.f))
```
