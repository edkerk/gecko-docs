# Stage 3: Model tuning

!!! info "Timing"
    Approximately 15 minutes (Steps 33-52).

To make the ecModel functional, a maximum constraint must be imposed on the
protein pool. The value of the maximum constraint is calculated as:

$$ \sigma \times f \times P_{tot} $$

where sigma is the average in vivo saturation of all enzymes in the model, f is
the mass fraction occupied by metabolic enzymes in the total proteome, and
$P_{tot}$ is the total protein mass in grams per gram cell dry weight. If one or
more factors are unknown, a default of 0.5 can be used for each, giving a default
maximum constraint of $0.5 \times 0.5 \times 0.5 = 0.125$.

Because there is also uncertainty in the $k_{cat}$ values, which can lead to
incorrect predictions, the model is tuned in this stage using known
physiological data. Tuning can adjust the protein pool and/or the $k_{cat}$ of
specific enzymes:

- The easiest approach is to increase the maximum constraint on the protein
  pool. Letting it increase without constraint reaches a higher growth rate, but
  may give an unrealistically high protein pool, mostly because of extremely low
  and incorrect $k_{cat}$ values of some key enzymes. (Protein pool values above
  one imply that at least one of sigma, f and $P_{tot}$ is greater than one,
  which is theoretically impossible.)
- Another option is to replace extremely low $k_{cat}$ values with an arbitrary
  value, for example tenfold of the original, which is easy and can be combined
  with the first option.
- A more biologically meaningful option is to identify the enzymes that most
  limit growth and substitute their $k_{cat}$ with higher values.

!!! note "When no physiological data are available"
    Model tuning requires physiological data, particularly growth rate data.
    Without such data, for example in large-scale reconstruction for various cell
    lines, only draft ecModels can be obtained. A draft model may not be
    functional for simulating realistic fluxes (because of the undefined upper
    bound on the protein pool) but can still compare cellular parameters such as
    protein costs. Even with no experimental data, functional ecModels can be
    obtained by assuming an arbitrary value for the protein pool and increasing
    low kcat values so that reasonable simulations are achieved.

## Simulate growth rate

**Step 33.** After applying enzyme constraints, examine whether the ecModel can
simulate a realistic growth rate. Microorganisms should reach their maximum
growth rate if nutrient supply is not limiting. To allow unconstrained uptake of
the carbon source:

=== "MATLAB"

    ```matlab
    ecModel = setParam(ecModel, 'lb', params.c_source, -1000);
    ```

    Or by directly referring to the glucose exchange reaction in the
    *S. cerevisiae* ecModel:

    ```matlab
    ecModel = setParam(ecModel, 'lb', 'r_1714', -1000);
    ```

=== "Python"

    geckopy/cobrapy has no `setParam` wrapper: bounds are attributes on the
    `cobra.Reaction` object itself.

    ```python
    ec_model.reactions.get_by_id(params.c_source).lower_bound = -1000
    ```

    Or directly:

    ```python
    ec_model.reactions.get_by_id("r_1714").lower_bound = -1000
    ```

**Step 34.** In this example the glucose exchange reaction is defined as
`glucose[e] <=>`. A positive, forward flux represents dissipation from the
system, so a negative flux signifies uptake into the cytoplasm. Modify the
constraint on glucose uptake by setting a negative lower bound. Query the
direction of a reaction with:

=== "MATLAB"

    ```matlab
    constructEquations(ecModel, 'r_1714');
    ```

=== "Python"

    cobrapy reactions print their own equation:

    ```python
    print(ec_model.reactions.get_by_id("r_1714").reaction)
    ```

**Step 35.** Set growth as the objective, predict the flux distribution and
print the growth rate:

=== "MATLAB"

    ```matlab
    ecModel = setParam(ecModel, 'obj', params.bioRxn, 1);
    sol = solveLP(ecModel);
    bioRxnIdx = getIndexes(ecModel, params.bioRxn, 'rxns');
    fprintf('Growth rate: %f /hour\n', sol.x(bioRxnIdx))
    ```

=== "Python"

    ```python
    ec_model.objective = params.bio_rxn
    sol = ec_model.optimize()
    print(f"Growth rate: {sol.fluxes[params.bio_rxn]:.4f} /hour")
    ```

    Setting `.objective` to a reaction id maximizes it by default — there is
    no separate "set objective coefficient" call, and no reaction-index
    lookup: `sol.fluxes` is a pandas Series indexed by reaction id.

**Step 36.** Examine the predicted growth rate. In this example the ecModel
reaches a growth rate far lower than 0.41 h^-1 (the maximum growth rate of
*S. cerevisiae*, entered in the model adapter as `obj.params.gR_exp`). This
indicates the model needs to be tuned.

**Step 37.** Confirm why the ecModel did not reach the experimental maximum
growth rate. Three reasons can be systematically checked:

- The stoichiometry of the metabolic network is not fully correct.
- The protein pool exchange is too tightly constrained.
- Incorrect (too low) $k_{cat}$ values are assigned to reactions.

## Network stoichiometry limits growth rate

**Step 38.** Investigate the stoichiometry by predicting the growth rate in the
conventional GEM (without enzyme constraints) with the same exchange flux
constraints:

=== "MATLAB"

    ```matlab
    model = loadConventionalGEM();
    model = setParam(model, 'lb', params.c_source, -1000);
    model = setParam(model, 'obj', params.bioRxn, 1);
    sol = solveLP(model);
    bioRxnIdx = getIndexes(model, params.bioRxn, 'rxns');
    fprintf('Growth rate: %f /hour\n', sol.x(bioRxnIdx))
    ```

=== "Python"

    ```python
    from geckopy import load_conventional_gem

    model = load_conventional_gem(adapter)
    model.reactions.get_by_id(params.c_source).lower_bound = -1000
    model.objective = params.bio_rxn
    sol = model.optimize()
    print(f"Growth rate: {sol.fluxes[params.bio_rxn]:.4f} /hour")
    ```

If the conventional GEM also cannot reach the maximum growth rate, the starting
GEM contains errors in its stoichiometry or constraints that should be resolved
before reconstructing an ecModel.

## Too tight protein pool constraint

**Step 39.** Confirm that the protein pool constraint set in Step 32 is
realistic. Inspect the sigma, $P_{tot}$ and f parameters in the model adapter
and modify them to more realistic values if discrepancies are observed (Step 4).

**Step 40.** Regardless of whether the protein pool parameters are realistic,
the simplest way to enable the intended growth is to relax the constraint on the
protein pool usage reaction, relieving all enzyme constraints at once. Set the
lower bound to -1,000 (for reaction direction, see Step 34):

=== "MATLAB"

    ```matlab
    ecModel = setParam(ecModel, 'lb', 'prot_pool_exchange', -1000);
    ```

=== "Python"

    !!! warning "prot_pool_exchange runs in the opposite direction — a known GECKO inconsistency, not a design choice"
        MATLAB GECKO's `prot_pool_exchange` still carries a *negative* flux
        (protein flows out of the model, `bounds = (-1000, 0)` by default),
        so relaxing it means lowering the lower bound. The individual
        `usage_prot_*` reactions were recently swapped in GECKO to run
        *forward* instead; `prot_pool_exchange` should have been swapped to
        match at the same time, but wasn't. geckopy implements the corrected,
        consistent forward convention throughout — both `usage_prot_*` and
        `prot_pool_exchange` run forward (`bounds = (0, 1000)`), so relaxing
        `prot_pool_exchange` means raising the upper bound instead of
        lowering the lower bound.

        This is a real difference between current GECKO (MATLAB, described
        here) and geckopy today, expected to be resolved by a matching fix in
        a future GECKO release — not a permanent, intentional divergence.
        Keep it in mind for every `prot_pool_exchange` / `usage_prot_*` bound
        or objective coefficient below.

    ```python
    ec_model.reactions.prot_pool_exchange.upper_bound = 1000
    ```

**Step 41.** With neither a protein pool constraint nor a nutrient constraint,
predict the lowest protein pool usage that still supports the experimental
maximum growth rate:

=== "MATLAB"

    ```matlab
    ecModel = setParam(ecModel, 'lb', 'r_4041', 0.41);
    ecModel = setParam(ecModel, 'obj', 'prot_pool_exchange', 1);
    sol = solveLP(ecModel);
    protPoolIdx = strcmp(ecModel.rxns, 'prot_pool_exchange');
    fprintf('Protein pool usage is: %.0f mg/gDCW\n', abs(sol.x(protPoolIdx)))
    ```

    !!! warning "Critical step"
        Because of the direction of the exchange reaction (Step 34),
        minimization of protein pool usage is implied by using `1` (not
        `-1`) as the objective coefficient.

=== "Python"

    Because `prot_pool_exchange` runs forward in geckopy, minimizing its
    usage means minimizing the reaction directly (a plain positive
    objective, then optimizing in the `min` direction) — the opposite of
    MATLAB's "maximize with coefficient +1" trick:

    ```python
    ec_model.reactions.get_by_id("r_4041").lower_bound = 0.41
    ec_model.objective = "prot_pool_exchange"
    ec_model.objective_direction = "min"
    sol = ec_model.optimize()
    pool_usage = sol.fluxes["prot_pool_exchange"]
    print(f"Protein pool usage is: {pool_usage:.0f} mg/gDCW")
    ```

**Step 42.** Set the predicted protein pool usage as the constraint on the
protein pool exchange reaction, then revert the previously asserted objective
function and growth rate constraint:

=== "MATLAB"

    ```matlab
    ecModel = setParam(ecModel, 'lb', protPoolIdx, sol.x(protPoolIdx));
    ecModel = setParam(ecModel, 'lb', 'r_4041', 0);
    ecModel = setParam(ecModel, 'obj', 'r_4041', 1);
    ```

=== "Python"

    ```python
    ec_model.reactions.prot_pool_exchange.upper_bound = pool_usage
    ec_model.reactions.get_by_id("r_4041").lower_bound = 0
    ec_model.objective = "r_4041"
    ec_model.objective_direction = "max"
    ```

While this always yields an ecModel that reaches the intended growth rate
(assuming the conventional GEM can too), it often sets the protein pool usage to
an unrealistic protein content. It is therefore recommended to instead increase
$k_{cat}$ values of some reactions.

## Sensitivity tuning of kcat values

**Step 43.** Rather than relaxing the pool, it is advised to iteratively
increase the $k_{cat}$ values of enzymes that limit growth until the desired
growth rate is reached. At this stage the enzyme constraints are dominated by
the overarching protein pool constraint, so in each deterministic iteration the
most-limiting enzyme is identified as the one demanding the largest fraction of
the protein pool. One $k_{cat}$ is increased per iteration; it is the value that
contributes most to overconstraining the model, though not necessarily the one
most deviating from its in situ value. First revert the protein pool constraint
to a realistic value (Step 32), then tune and report the changes:

=== "MATLAB"

    ```matlab
    ecModel = setProtPoolSize(ecModel);
    [ecModel, tunedKcats] = sensitivityTuning(ecModel);
    struct2table(tunedKcats)
    ```

=== "Python"

    ```python
    from geckopy import sensitivity_tuning, set_prot_pool_size

    set_prot_pool_size(ec_model)
    tuning_result = sensitivity_tuning(ec_model)
    ```

    `sensitivity_tuning` mutates `ec_model` in place (no separate returned
    model) and returns a `TunedKcatsResult` with a `.rxns` field (and the
    previous/tuned values); with no explicit growth-rate argument it targets
    `params.gr_exp` from the adapter. Not available for light ecModels
    (raises `NotImplementedError` if `ec_model.ec.gecko_light` is `True`).
    The Bayesian ABC-SMC variant introduced in GECKO MATLAB 3.3.0
    (`bayesianSensitivityTuning`) is not yet ported to geckopy.

**Step 44.** Look at the report. The `tunedKcats` (Python: `tuning_result`)
output documents which $k_{cat}$ values were modified, with their previous
value and the catalyzed reaction. Inspect this to find whether any modified
value was initially gathered wrongly from a $k_{cat}$ source.

## Evaluate the tuned kcat values

!!! warning "Critical"
    In Step 43 the values are tuned automatically, based only on the enzyme
    overconstraining the ecModel. However, there might be good evidence that the
    original value was unrealistic and the tuned value better reflects reality.
    The following steps show a worked example for the $k_{cat}$ of
    5'-phosphoribosylformyl glycinamidine synthetase. Repeat for each value of
    interest. Note that not every tuned value can be supported by literature
    data; alternatively, in vivo apparent enzyme turnover numbers can be
    considered.

**Step 45.** The `tunedKcats` structure might show that the tuned $k_{cat}$ of
5'-phosphoribosylformyl glycinamidine synthetase (reaction `r_0079`) was much
higher than the original (original 0.05 s^-1, tuned 5 s^-1), with BRENDA as the
original source. Get its location in the `kcatList`:

=== "MATLAB"

    ```matlab
    rxnIdx = find(strcmp(kcatList_merged.rxns, 'r_0079'));
    kcatList_merged.wildcardLvl(rxnIdx)
    kcatList_merged.eccodes(rxnIdx)
    kcatList_merged.origin(rxnIdx)
    ```

=== "Python"

    kcat lists are `pandas.DataFrame`s in geckopy (one row per reaction),
    rather than a struct of parallel arrays, so this is a row lookup:

    ```python
    row = kcat_list_merged.loc[kcat_list_merged["rxn_id"] == "r_0079"].iloc[0]
    print(row["wildcard_level"], row["eccode"], row["origin"])
    ```

This yields a wildcard level of 0, EC number 6.3.5.3 and origin 4 (any organism,
any substrate, kcat value).

**Step 46.** Look at the specific
[BRENDA entry](https://www.brenda-enzymes.org/enzyme.php?ecno=6.3.5.3). The
reported $k_{cat}$ of 0.05 is from *E. coli* with NH3 as substrate. The usual
substrate is glutamine, so the reported value might not be a fair estimate for
the reaction in the ecModel.

**Step 47.** Refer to the original paper. Its abstract states that NH3 can
replace glutamine as a nitrogen donor with a Km of 1 M and a turnover of 3
min^-1 (2% of glutamine turnover). The same paper also reports a specific
activity with glutamine as substrate, which would be more reasonable to use.

**Step 48.** Calculate the activity with the more suitable substrate. The
specific activity was reported as 2.15 micromol/min/mg protein. Because
micromol/min/mg protein equals mmol/min/g protein, convert to mol/s/g protein,
then use the MW of the enzyme to convert to s^-1:

=== "MATLAB"

    ```matlab
    convKcat = 2.15;
    convKcat = convKcat / 1000;
    convKcat = convKcat / 60;
    enzMW = ecModel.ec.mw(strcmp(ecModel.ec.enzymes, 'P38972'));
    convKcat = convKcat * enzMW
    ```

=== "Python"

    ```python
    enz_idx = ec_model.ec.enzymes.index("P38972")
    enz_mw = ec_model.ec.mw[enz_idx]
    sa = 2.15  # umol/min/mg protein
    conv_kcat = sa / 1000 / 60 * enz_mw
    print(conv_kcat)
    ```

**Step 49.** Compare the new value with the tuned value. Here the converted
$k_{cat}$ is 5.34, not too dissimilar to the value of 5 reached by
`sensitivityTuning`.

**Step 50.** Replace the value in the ecModel with the new literature value.
You can either document it in `customKcats.tsv` (used in Step 28) or apply it
directly:

=== "MATLAB"

    ```matlab
    ecModel = setKcatForReactions(ecModel, 'r_0079', 5.34);
    ecModel = applyKcatConstraints(ecModel);
    ```

=== "Python"

    ```python
    from geckopy import apply_kcat_constraints, set_kcat_for_reactions

    set_kcat_for_reactions(ec_model, ["r_0079"], 5.34)
    apply_kcat_constraints(ec_model)
    ```

    `set_kcat_for_reactions` takes a list of reaction ids (even for one
    reaction) and a single kcat value applied to all of them.

**Step 51.** After repeating this for each tuned value, consider the results. If
convincing evidence exists that the original value is more realistic, the
network stoichiometry may be incomplete, with key reactions or whole pathways
missing from the starting GEM. Such issues (as in Step 38) should be resolved in
the conventional GEM before using it to reconstruct an ecModel.

## Save the functional ecModel

**Step 52.** The ecModel obtained is now a **functional ecModel**, able to
simulate the physiological data provided. Before progressing to Stages 4 and 5,
it is recommended to save it:

=== "MATLAB"

    ```matlab
    saveEcModel(ecModel);
    ```

=== "Python"

    ```python
    from geckopy import save_ec_model

    save_ec_model(ec_model, "ecYeastGEM.yml", adapter=adapter)
    ```

## Box 2: Selection of RAVEN toolbox functions

These operations work on both conventional GEMs and ecModels, in both
languages (RAVEN toolbox functions in MATLAB, cobrapy idioms in Python).

Set the upper bound of a reaction (see `ecModel.rxns`) to ten:

=== "MATLAB"

    ```matlab
    ecModel = setParam(ecModel, 'ub', 'r_0003', 10);
    ```

=== "Python"

    ```python
    ec_model.reactions.get_by_id("r_0003").upper_bound = 10
    ```

Set the lower bound of a reaction to zero:

=== "MATLAB"

    ```matlab
    ecModel = setParam(ecModel, 'lb', 'r_0003', 0);
    ```

=== "Python"

    ```python
    ec_model.reactions.get_by_id("r_0003").lower_bound = 0
    ```

Set the objective to maximize flux through the biomass reaction:

=== "MATLAB"

    ```matlab
    ecModel = setParam(ecModel, 'obj', params.bioRxn, 1);
    ```

=== "Python"

    ```python
    ec_model.objective = params.bio_rxn
    ```

Perform FBA, optimizing the objective:

=== "MATLAB"

    ```matlab
    sol = solveLP(ecModel);
    ```

=== "Python"

    ```python
    sol = ec_model.optimize()
    ```

Perform parsimonious FBA, optimizing the objective and minimizing the total sum
of flux:

=== "MATLAB"

    ```matlab
    sol = solveLP(ecModel, 1);
    ```

=== "Python"

    ```python
    from cobra.flux_analysis import pfba

    sol = pfba(ec_model)
    ```

    geckopy also offers `pfba_enzymes(ec_model)`, which instead minimizes
    only the L1 norm of `usage_prot_*` fluxes (enzyme usage) rather than all
    reaction fluxes — useful for the enzyme-usage inspection in
    [Stage 5](stage5-simulation-analysis.md#enzyme-usage). It is not
    available for light ecModels.

Inspect the nonzero fluxes:

=== "MATLAB"

    Through exchange reactions (this includes usage reactions for enzymes
    constrained by their concentration, but not enzymes that draw from the
    protein pool, because pool usage is the exchange reaction in that case):

    ```matlab
    printFluxes(ecModel, sol.x)
    ```

    Through all reactions:

    ```matlab
    printFluxes(ecModel, sol.x, false)
    ```

=== "Python"

    `sol.fluxes` is a pandas Series indexed by reaction id, so this is
    ordinary pandas filtering — through all reactions:

    ```python
    print(sol.fluxes[sol.fluxes != 0])
    ```

    Restricted to exchange reactions:

    ```python
    exchange_ids = [r.id for r in ec_model.exchanges]
    print(sol.fluxes[exchange_ids][sol.fluxes[exchange_ids] != 0])
    ```

Export the results to a spreadsheet (this file does not contain content
from the `ecModel.ec` structure, but is convenient for quickly finding reaction
identifiers):

=== "MATLAB"

    ```matlab
    exportToExcelFormat(ecModel, 'filename.xlsx');
    ```

=== "Python"

    geckopy has no dedicated spreadsheet exporter; write the solution
    directly with pandas:

    ```python
    sol.fluxes.to_excel("filename.xlsx")
    ```

Export the ecModel to an SBML file for use in other constraint-based model
software packages:

=== "MATLAB"

    ```matlab
    exportModel(ecModel, 'filename.xml');
    ```

=== "Python"

    ```python
    import cobra

    cobra.io.write_sbml_model(ec_model, "filename.xml")
    ```

    As noted in [Stage 1](stage1-structure-expansion.md#save-the-ecmodel),
    this plain-cobrapy SBML export does not retain the `ec_model.ec` fields
    — same caveat as MATLAB's `exportModel`.
