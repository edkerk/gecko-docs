# Limit proteins

Constraining the model with proteomics data: the protein-pool f-factor,
per-enzyme concentration limits, and relaxation when the measured
proteome makes the model infeasible. MATLAB: `src/geckomat/limit_proteins`.
Python: `geckopy.limit_proteins`.

## calculate_f_factor / calculateFfactor

Compute the mass fraction *f* of total protein that is accounted for by
enzymes in the model.

=== "Python · geckopy"

    ::: geckopy.calculate_f_factor

=== "MATLAB · GECKO"

    ::: calculateFfactor
        handler: matlab

## constrain_enz_concs / constrainEnzConcs

Apply measured per-enzyme concentrations as upper bounds.

=== "Python · geckopy"

    ::: geckopy.constrain_enz_concs

=== "MATLAB · GECKO"

    ::: constrainEnzConcs
        handler: matlab

## fill_enz_concs / fillEnzConcs

Fill in missing enzyme concentrations from the pool.

=== "Python · geckopy"

    ::: geckopy.fill_enz_concs

=== "MATLAB · GECKO"

    ::: fillEnzConcs
        handler: matlab

## flexibilize_enz_concs / flexibilizeEnzConcs

Relax individual enzyme-concentration constraints until the model is
feasible at the target growth rate.

=== "Python · geckopy"

    ::: geckopy.flexibilize_enz_concs

=== "MATLAB · GECKO"

    ::: flexibilizeEnzConcs
        handler: matlab

## get_conc_control_coeffs / getConcControlCoeffs

Compute enzyme-concentration control coefficients.

=== "Python · geckopy"

    ::: geckopy.get_conc_control_coeffs

=== "MATLAB · GECKO"

    ::: getConcControlCoeffs
        handler: matlab

## apply_flux_data_constraints / constrainFluxData

Apply experimentally measured fluxes as constraints.

=== "Python · geckopy"

    ::: geckopy.apply_flux_data_constraints

=== "MATLAB · GECKO"

    ::: constrainFluxData
        handler: matlab

## relax_proteomics_greedy (Python)

A greedy proteomics-relaxation strategy specific to geckopy; returns
structured step-by-step results.

::: geckopy.relax_proteomics_greedy

::: geckopy.GreedyRelaxResult

::: geckopy.FlexEnzResult
