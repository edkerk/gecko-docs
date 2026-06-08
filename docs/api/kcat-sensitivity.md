# kcat sensitivity tuning

Tuning kcat values so the model reproduces a measured growth rate, by
sensitivity analysis and by fitting the saturation factor sigma. MATLAB:
`src/geckomat/kcat_sensitivity_analysis`. Python:
`geckopy.kcat_sensitivity_analysis`.

## sensitivity_tuning / sensitivityTuning

Iteratively raise the most growth-limiting kcats until the model reaches
the target growth rate.

=== "Python · geckopy"

    ::: geckopy.sensitivity_tuning

=== "MATLAB · GECKO"

    ::: sensitivityTuning
        handler: matlab

## fit_sigma / sigmaFitter

Fit the average saturation factor (sigma) that scales the protein pool.

=== "Python · geckopy"

    ::: geckopy.fit_sigma

=== "MATLAB · GECKO"

    ::: sigmaFitter
        handler: matlab

## find_max_value / findMaxValue

Find the kcat/enzyme that most limits the objective.

=== "Python · geckopy"

    ::: geckopy.find_max_value

=== "MATLAB · GECKO"

    ::: findMaxValue
        handler: matlab

## truncate_values / truncateValues

Clamp kcats to a sensible range during tuning.

=== "Python · geckopy"

    ::: geckopy.truncate_values

=== "MATLAB · GECKO"

    ::: truncateValues
        handler: matlab

## Result types (Python)

geckopy returns structured result objects from the tuning routines.

::: geckopy.SigmaFitterResult

::: geckopy.TunedKcatsResult

## Bayesian tuning (MATLAB)

GECKO additionally provides ABC-SMC Bayesian kcat tuning (geckopy's port of
this is planned). These live in `kcat_sensitivity_analysis/Bayesian`.

::: bayesianSensitivityTuning
    handler: matlab
