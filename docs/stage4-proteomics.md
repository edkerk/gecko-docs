# Stage 4: Integration of proteomics data

!!! info "Timing"
    Approximately 15 minutes (Steps 53-65). Step 64 accounts for most of the
    time.

Enzyme usage reactions allow the integration of proteomics data into ecModels
reconstructed by GECKO, leading to **proteome-constrained ecModels** that are
context specific. Because of measurement errors in proteomics data and
uncertainties in enzyme kinetics, the ecModels are most likely to be
overconstrained by proteomics data, resulting in an infeasible solution. This is
addressed by a proteomics integration algorithm that loosens the constraints on
enzymes with great control coefficients, where the control coefficient of an
enzyme is the change in growth rate over the change in its concentration.

!!! warning "Full ecModels only"
    This process is not suitable for light ecModels. Stage 4 assumes the ecModel
    is a full version.

## Constrain with proteomics data

**Step 53.** Instead of constraining the total protein content, the
concentration of individual enzymes can be constrained by integrating proteomics
data. Constraining individual enzymes will in most cases generate an
overconstrained ecModel that cannot reach the intended growth rate, because
there are now uncertainties in both the enzyme levels and the $k_{cat}$ values.
It is therefore imperative that the proteomics data is of high quality and that
protein concentrations of lower certainty are discarded.

**Step 54.** Prepare the proteomics data. It is important to:

- Provide the protein concentrations in milligram per gram dry cell weight,
  obtainable through various methods.
- Store the data in `data/proteomics.tsv`, which can contain data from multiple
  experimental conditions.
- Filter out lower-certainty data: discard very low protein concentrations,
  proteins with high relative standard deviation, and proteins absent from most
  of the replicates.

**Step 55.** Check that the proteomics data is in a standardized file format by
referring to `data/proteomics.tsv`. Integration of proteomics data involves four
steps, analogous to integrating $k_{cat}$ values:

- Load the proteomics data into a `protData` structure.
- Populate `ecModel.ec.concs` with the relevant enzyme concentrations.
- Apply the enzyme concentrations as constraints in enzyme usage reactions (for
  reaction direction, see [Stage 3, Step 34](stage3-model-tuning.md#simulate-growth-rate)).
- Modify the usage reactions of enzymes with defined concentrations so they no
  longer draw from the generic protein pool pseudo-metabolite.

While it is possible to manually enter or modify `ecModel.ec.concs`, providing
the proteomics data in a standardized file format to be read by the provided
functions is recommended.

**Step 56.** Load the proteomics dataset.

=== "MATLAB"

    For one experiment with three replicates:

    ```matlab
    protData = loadProtData(3);
    ```

    For two experiments with three replicates each:

    ```matlab
    protData = loadProtData([3,3]);
    ```

    This function also filters the data, applied to the whole dataset. When
    `protData` contains multiple experiments, specify which to use
    (experiment 1 here):

    ```matlab
    ecModel = fillEnzConcs(ecModel, protData, 1);
    ```

=== "Python"

    For one experiment with three replicates, pass the replicate count as a
    one-element list:

    ```python
    from geckopy import fill_enz_concs, load_prot_data

    prot_data = load_prot_data(
        params.path / "data" / "proteomics.tsv", repl_per_cond=[3],
    )
    ```

    For two experiments with three replicates each: `repl_per_cond=[3, 3]`.
    `fill_enz_concs` takes a 0-indexed `data_col` (MATLAB's experiment index
    is 1-indexed) to select which experiment to use when there are several:

    ```python
    fill_enz_concs(ec_model, prot_data, data_col=0)
    ```

**Step 57.** Introduce the enzyme concentrations to the model bounds:

=== "MATLAB"

    Written to `ecModel.lb` — GECKO 3's negative-flux `usage_prot_*`
    convention (see the [Stage 1](stage1-structure-expansion.md#box-1-extension-of-a-conventional-gem)
    GECKO 4 note):

    ```matlab
    ecModel = constrainEnzConcs(ecModel);
    ```

=== "Python"

    Written to the upper bound of each `usage_prot_*` reaction — geckopy's
    forward convention:

    ```python
    from geckopy import constrain_enz_concs

    constrain_enz_concs(ec_model)
    ```

    Raises `ValueError` if called on a light ecModel — light ecModels have no
    `usage_prot_*` reactions to constrain, so proteomics integration is not
    possible for them in either language.

!!! warning "Critical step"
    The enzyme concentrations must be provided in milligram per gram dry cell
    weight (DCW). Relative proteomics cannot provide data in these units.
    Loading proteomics data with protein levels in incorrect units will produce
    nonsensical ecModels.

**Step 58.** Enzymes constrained by their concentrations are no longer drawn
from the protein pool pseudo-metabolite (defined in
[Stage 2, Step 32](stage2-kcat-integration.md#constrain-the-protein-pool-exchange-reaction)).
The protein pool exchange constraint should be modified to represent only the
enzymes not constrained by their concentrations. It is common that at least some
listed enzymes lack available concentrations because of technical challenges in
the experiments. As the proteomics data come from an experiment where the cells
may have changed their physiology, a sample-specific measured total protein
content (for example 0.5 g/gDCW) can be explicitly considered instead of
`params.Ptot`:

=== "MATLAB"

    ```matlab
    ecModel = updateProtPool(ecModel, 0.5);
    ```

    !!! note "updateProtPool is obsolete since GECKO 3.2.0"
        Since GECKO 3.2.0, all protein usage reactions draw from the protein
        pool, with or without a concentration constraint, which makes
        `updateProtPool` obsolete: use `setProtPoolSize` with a recalculated
        f-factor instead (see
        [Stage 2, Step 32](stage2-kcat-integration.md#constrain-the-protein-pool-exchange-reaction)).
        The call above is shown for legacy reference only — the current
        replacement is:

        ```matlab
        f = calculateFfactor(ecModel, 'protData', protData);
        ecModel = setProtPoolSize(ecModel, 'Ptot', 0.5, 'f', f);
        ```

=== "Python"

    geckopy never implemented `updateProtPool`, since it was already obsolete
    in GECKO by the time of the port. Recompute the f-factor from the
    proteomics data and pass the sample-specific total protein content to
    `set_prot_pool_size` directly:

    ```python
    from geckopy import calculate_f_factor, set_prot_pool_size

    f = calculate_f_factor(ec_model, prot_data)
    set_prot_pool_size(ec_model, p_tot=0.5, f=f)
    ```

## Constrain with experimentally measured exchange fluxes

**Step 59.** Because the integrated enzyme concentrations come from a particular
experiment, also constrain any exchange reaction for which experimental data are
available, such as glucose uptake, ethanol production or CO2 exchange rate
determined for the same experiment. The flux data file at `data/fluxData.tsv`
can contain data from multiple experiments and as many reaction fluxes as
desired. Providing a zero flux blocks an exchange reaction. Load the data:

=== "MATLAB"

    ```matlab
    fluxData = loadFluxData();
    ```

=== "Python"

    ```python
    from geckopy import load_flux_data

    flux_data = load_flux_data(params.path / "data" / "fluxData.tsv")
    ```

**Step 60.** Decide whether to use loose or strict constraints for the measured
metabolite exchange rates:

1. With **loose** constraints, the measured rate is set as the upper bound while
   the lower bound stays at zero (for exchange reactions with a negative rate,
   this means setting the lower bound to the measured value and the upper bound
   to zero).
2. With **strict** constraints, the lower and upper bounds are set at, for
   example, 95% and 105% of the measured value.

Stricter constraints force the ecModel to adhere more closely to the measured
fluxes, but risk that imprecision in the measured fluxes or enzyme
concentrations produces a nonfunctional model that cannot solve FBA. In that
case, use loose constraints.

**Step 61.** Decide how the growth rate is applied, as either a `max` or `min`
constraint:

- With **max**, the measured growth rate is the upper bound, indicating the
  maximum the ecModel should reach. Suitable when growth is the objective
  function ([Stage 3, Step 35](stage3-model-tuning.md#simulate-growth-rate)).
- With **min**, the measured growth rate is the lower bound, indicating the
  minimum the ecModel should reach. Suitable when minimizing the protein pool
  exchange reaction is the objective
  ([Stage 3, Step 41](stage3-model-tuning.md#too-tight-protein-pool-constraint)).

**Step 62.** After deciding (for example loose constraints for metabolic
exchange fluxes and `max` for the growth rate, to make the ecModel least likely
to be overconstrained), set the data from the first experiment and run FBA to
predict the growth rate:

=== "MATLAB"

    ```matlab
    ecModel = constrainFluxData(ecModel, fluxData, 1, 'max', 'loose');
    sol = solveLP(ecModel);
    fprintf('Growth rate that is reached: %f /hour\n', abs(sol.f))
    ```

=== "Python"

    ```python
    from geckopy import apply_flux_data_constraints

    apply_flux_data_constraints(
        ec_model, flux_data,
        condition=0, max_min_growth="max", loose_strict_flux="loose",
    )
    sol = ec_model.optimize()
    print(f"Growth rate that is reached: {sol.objective_value:.4f} /hour")
    ```

    `condition` is 0-indexed (MATLAB's experiment index is 1-indexed), so the
    first experiment is `condition=0`. `constrain_flux_data` also exists as a
    deprecated alias of `apply_flux_data_constraints`.

**Step 63.** Analyze the results. With `max` and `loose`, the FBA should reach a
solution unless too many zero-exchange fluxes were defined in Step 59. If the
ecModel cannot reach the intended growth rate, the overconstrained enzyme levels
must be made more flexible.

## Flexibilize measured protein concentrations

**Step 64.** Perform an iterative process that calculates the control
coefficients of all enzymes and increases the concentration of the enzyme with
the greatest control coefficient. This repeats until the intended growth rate
(here 0.1 h^-1) is reached. The fold change applied per iteration is adjustable
(here tenfold). Once the growth rate is reached, the adjusted enzyme levels are
reduced to the minimum concentration that still allows the same flux
distribution:

=== "MATLAB"

    ```matlab
    [ecModel, flexEnz] = flexibilizeEnzConcs(ecModel, 0.1, 10);
    ```

=== "Python"

    ```python
    from geckopy import flexibilize_enz_concs

    flex_result = flexibilize_enz_concs(ec_model, exp_growth=0.1, fold_change=10.0)
    ```

    `flexibilize_enz_concs` mutates `ec_model` in place and returns a
    `FlexEnzResult` with parallel arrays (`uniprot_ids`, `old_concs`,
    `flex_concs`, `ratio_incr`) — the Python equivalent of `flexEnz`.

The flexibilized enzyme levels are reflected in changed constraints of their
`usage_prot` reactions (in Python, `usage_prot_*`; see
[Stage 3, Step 40](stage3-model-tuning.md#too-tight-protein-pool-constraint)).

!!! warning "Critical step"
    The concentrations in `ecModel.ec.concs` remain unchanged and continue to
    reflect the measured values obtained via `fillEnzConcs`/`fill_enz_concs`.
    Only the bounds of selected `usage_prot`/`usage_prot_*` reactions are
    changed to the flexibilized value.

!!! tip "GECKO 4: a greedy shadow-price alternative (not part of the original protocol)"
    Both languages also offer a second relaxation algorithm alongside
    `flexibilizeEnzConcs`/`flexibilize_enz_concs`: at each iteration it
    relaxes whichever still-constrained enzyme has the largest absolute
    shadow price on its mass-balance constraint (fully, back to the default
    bound, rather than by a fixed fold-change), and stops as soon as the
    target growth rate is reached. Not part of the original Nature Protocols
    procedure — an alternative to try if Step 64's fold-change approach
    relaxes more enzymes than necessary.

    === "MATLAB"

        ```matlab
        result = relaxProteomicsGreedy(ecModel, 'minimalGrowth', 0.1);
        ```

        `result.trace` has one row per relaxation step (`iteration`,
        `relaxedUniprot`, `growthBefore`, `growthAfter`, `shadowPrice`);
        `result.relaxed` maps each relaxed enzyme back to its original
        `ecModel.ec.concs` value so it can be restored later; `result.converged`
        is true iff `result.finalGrowth >= minimalGrowth`.

    === "Python"

        ```python
        from geckopy import relax_proteomics_greedy

        result = relax_proteomics_greedy(ec_model, minimal_growth=0.1)
        ```

        Returns a `GreedyRelaxResult` with the same shape: `.trace`, `.relaxed`,
        `.final_growth`, `.converged`.

**Step 65.** Inspect which enzymes were modified in `flexEnz`. Flexibilizing
enzyme concentrations is reasonable because the protein measurement might have
been imprecise, but it is possible that the $k_{cat}$ should be modified instead.
If the same enzyme concentration is modified repeatedly, the user is prompted to
check its $k_{cat}$ and manually curate it by defining custom $k_{cat}$ values
(see [Stage 2, Step 28](stage2-kcat-integration.md#provide-custom-kcat-values)
and [Stage 3, Step 45](stage3-model-tuning.md#evaluate-the-tuned-kcat-values),
focusing on the reported problematic enzyme).
