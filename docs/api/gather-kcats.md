# Gather kcats

Finding turnover numbers (kcats) for each enzyme-reaction pair, from
BRENDA fuzzy matching, deep-learning prediction (DLKcat /
OpenKineticsPredictor), or standard subsystem values. MATLAB:
`src/geckomat/gather_kcats`. Python: `geckopy.gather_kcats`.

## fuzzy_kcat_matching / fuzzyKcatMatching

Match kcats from BRENDA by EC number, substrate and organism, with a
graded fall-back when an exact match is missing.

=== "Python · geckopy"

    ::: geckopy.fuzzy_kcat_matching

=== "MATLAB · GECKO"

    ::: fuzzyKcatMatching
        handler: matlab

## apply_kcat_list / selectKcatValue

Choose a single kcat per reaction from the candidate list and write it
onto the model.

=== "Python · geckopy"

    ::: geckopy.apply_kcat_list

=== "MATLAB · GECKO"

    ::: selectKcatValue
        handler: matlab

## merge_kcats / mergeDLKcatAndFuzzyKcats

Merge DLKcat-predicted kcats with BRENDA fuzzy-matched kcats into one
list.

=== "Python · geckopy"

    ::: geckopy.merge_kcats

=== "MATLAB · GECKO"

    ::: mergeDLKcatAndFuzzyKcats
        handler: matlab

## assign_standard_kcat / getStandardKcat

Assign a "standard" (subsystem-average) kcat to reactions that have no
better value.

=== "Python · geckopy"

    ::: geckopy.assign_standard_kcat

=== "MATLAB · GECKO"

    ::: getStandardKcat
        handler: matlab

## remove_standard_kcat / removeStandardKcat

Remove previously assigned standard kcats (e.g. before re-running the
matching).

=== "Python · geckopy"

    ::: geckopy.remove_standard_kcat

=== "MATLAB · GECKO"

    ::: removeStandardKcat
        handler: matlab

## write_dlkcat_input / writeDLKcatInput

Write the input file consumed by DLKcat.

=== "Python · geckopy"

    ::: geckopy.write_dlkcat_input

=== "MATLAB · GECKO"

    ::: writeDLKcatInput
        handler: matlab

## read_dlkcat_output / readDLKcatOutput

Parse DLKcat's predicted-kcat output file.

=== "Python · geckopy"

    ::: geckopy.read_dlkcat_output

=== "MATLAB · GECKO"

    ::: readDLKcatOutput
        handler: matlab

## run_dlkcat / runDLKcat

Run DLKcat on the prepared input.

=== "Python · geckopy"

    ::: geckopy.run_dlkcat

=== "MATLAB · GECKO"

    ::: runDLKcat
        handler: matlab

## OpenKineticsPredictor (Python)

geckopy can submit jobs to, and fetch results from, the
OpenKineticsPredictor (OKP) REST service. The equivalent MATLAB helpers are
not yet on GECKO's `main` branch, so they are not shown here.

::: geckopy.submit_open_kinetics_predictor

::: geckopy.fetch_open_kinetics_predictor
