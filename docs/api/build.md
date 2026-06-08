# Build an ecModel

Turning a conventional genome-scale model into an enzyme-constrained
model, and editing the kcat constraints. MATLAB: `src/geckomat/change_model`.
Python: the `geckopy.ec_model` builder plus the pipeline edit functions, all
reachable from the top-level `geckopy` namespace.

## make_ec_model / makeEcModel

The top-level builder: expands a conventional GEM with enzyme information
and prepares the reactions for enzyme-usage constraints.

=== "Python · geckopy"

    ::: geckopy.make_ec_model

=== "MATLAB · GECKO"

    ::: makeEcModel
        handler: matlab

## apply_kcat_constraints / applyKcatConstraints

Incorporates the protein pseudo-metabolites into reactions as enzyme
usages by applying the assigned kcat values as constraints.

=== "Python · geckopy"

    ::: geckopy.apply_kcat_constraints

=== "MATLAB · GECKO"

    ::: applyKcatConstraints
        handler: matlab

## apply_custom_kcats / applyCustomKcats

Override kcat values for specific reactions or enzymes from a
user-supplied list.

=== "Python · geckopy"

    ::: geckopy.apply_custom_kcats

=== "MATLAB · GECKO"

    ::: applyCustomKcats
        handler: matlab

## set_kcat_for_reactions / setKcatForReactions

Manually set a kcat value for one or more reactions.

=== "Python · geckopy"

    ::: geckopy.set_kcat_for_reactions

=== "MATLAB · GECKO"

    ::: setKcatForReactions
        handler: matlab

## set_prot_pool_size / setProtPoolSize

Set the upper bound of the shared protein pool (the total enzyme budget).

=== "Python · geckopy"

    ::: geckopy.set_prot_pool_size

=== "MATLAB · GECKO"

    ::: setProtPoolSize
        handler: matlab

## fill_kcats_from_isozymes / getKcatAcrossIsozymes

Fill in missing kcats for a reaction from the values assigned to its
isozymes.

=== "Python · geckopy"

    ::: geckopy.fill_kcats_from_isozymes

=== "MATLAB · GECKO"

    ::: getKcatAcrossIsozymes
        handler: matlab

## get_reactions_from_enzyme / getReactionsFromEnzyme

List the reactions catalysed by a given enzyme.

=== "Python · geckopy"

    ::: geckopy.get_reactions_from_enzyme

=== "MATLAB · GECKO"

    ::: getReactionsFromEnzyme
        handler: matlab

## apply_complex_data / applyComplexData

Assign enzyme-complex subunit stoichiometry (e.g. from Complex Portal).

=== "Python · geckopy"

    ::: geckopy.apply_complex_data

=== "MATLAB · GECKO"

    ::: applyComplexData
        handler: matlab

## get_complex_data / getComplexData

Fetch enzyme-complex composition data.

=== "Python · geckopy"

    ::: geckopy.get_complex_data

=== "MATLAB · GECKO"

    ::: getComplexData
        handler: matlab

## find_met_smiles / findMetSmiles

Look up SMILES strings for metabolites (used by DLKcat).

=== "Python · geckopy"

    ::: geckopy.find_met_smiles

=== "MATLAB · GECKO"

    ::: findMetSmiles
        handler: matlab
