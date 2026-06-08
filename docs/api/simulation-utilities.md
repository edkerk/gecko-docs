# Simulation & utilities

Simulating and analysing the finished ecModel — FVA, strain design, enzyme
usage reports — plus loading/saving and other helpers. MATLAB:
`src/geckomat/utilities`. Python: `geckopy.utilities` (and SBML/YAML I/O).

## ec_fva / ecFVA

Enzyme-constrained flux variability analysis.

=== "Python · geckopy"

    ::: geckopy.ec_fva

=== "MATLAB · GECKO"

    ::: ecFVA
        handler: matlab

## ec_fseof / ecFSEOF

Flux-scanning with enforced objective function for strain-design target
identification.

=== "Python · geckopy"

    ::: geckopy.ec_fseof

=== "MATLAB · GECKO"

    ::: ecFSEOF
        handler: matlab

## enzyme_usage / enzymeUsage

Per-enzyme usage at a given flux distribution.

=== "Python · geckopy"

    ::: geckopy.enzyme_usage

=== "MATLAB · GECKO"

    ::: enzymeUsage
        handler: matlab

## report_enzyme_usage / reportEnzymeUsage

A formatted report of the most-used enzymes.

=== "Python · geckopy"

    ::: geckopy.report_enzyme_usage

=== "MATLAB · GECKO"

    ::: reportEnzymeUsage
        handler: matlab

## map_rxns_to_conv / mapRxnsToConv

Map ecModel reactions back to their conventional-GEM counterparts.

=== "Python · geckopy"

    ::: geckopy.map_rxns_to_conv

=== "MATLAB · GECKO"

    ::: mapRxnsToConv
        handler: matlab

## get_subset_ec_model / getSubsetEcModel

Extract a consistent sub-model for a subset of reactions.

=== "Python · geckopy"

    ::: geckopy.get_subset_ec_model

=== "MATLAB · GECKO"

    ::: getSubsetEcModel
        handler: matlab

## add_new_rxns_to_ec / addNewRxnsToEC

Add new reactions (and their enzymes) to an existing ecModel.

=== "Python · geckopy"

    ::: geckopy.add_new_rxns_to_ec

=== "MATLAB · GECKO"

    ::: addNewRxnsToEC
        handler: matlab

## load_conventional_gem / loadConventionalGEM

Load the starting conventional GEM defined by the adapter.

=== "Python · geckopy"

    ::: geckopy.load_conventional_gem

=== "MATLAB · GECKO"

    ::: loadConventionalGEM
        handler: matlab

## load_ec_model / loadEcModel

Load a previously saved ecModel (auto-upgrading legacy formats).

=== "Python · geckopy"

    ::: geckopy.load_ec_model

=== "MATLAB · GECKO"

    ::: loadEcModel
        handler: matlab

## save_ec_model / saveEcModel

Save an ecModel to the canonical YAML (and optionally SBML) format.

=== "Python · geckopy"

    ::: geckopy.save_ec_model

=== "MATLAB · GECKO"

    ::: saveEcModel
        handler: matlab

## load_prot_data / loadProtData

Load proteomics (enzyme-abundance) data.

=== "Python · geckopy"

    ::: geckopy.load_prot_data

=== "MATLAB · GECKO"

    ::: loadProtData
        handler: matlab

## load_flux_data / loadFluxData

Load experimental flux data.

=== "Python · geckopy"

    ::: geckopy.load_flux_data

=== "MATLAB · GECKO"

    ::: loadFluxData
        handler: matlab

## Analysis helpers (Python)

Additional analysis utilities provided by geckopy.

::: geckopy.get_enzyme_bottlenecks

::: geckopy.pfba_enzymes

## Project & plotting helpers (MATLAB)

GECKO ships MATLAB-only helpers for project setup and plotting.

::: plotEcFVA
    handler: matlab

::: startGECKOproject
    handler: matlab

::: findGECKOroot
    handler: matlab
