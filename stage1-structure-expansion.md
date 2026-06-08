# Stage 1: Expansion to an ecModel structure

!!! info "Timing"
    Approximately 15 minutes (Steps 8-14).

In this stage the starting GEM is expanded so that enzyme constraints can be
implemented in later stages. The conceptual operations are:

1. Reversible reactions are split into forward and backward reactions, because
   enzyme kinetics are direction dependent.
2. Reactions catalyzed by isozymes are split into multiple reactions by
   individual isozymes, because of differences in kinetics and MWs. (The light
   ecModel skips this and instead uses the lowest protein cost among isozymes.)
3. The protein pool is added as a pseudo-metabolite with an exchange reaction.
4. Enzymes are added as pseudo-metabolites that draw protein resources from the
   protein pool by enzyme usage reactions. (Not performed in the light version,
   where the protein pool is added directly into enzymatic reactions.)

The product of this stage is an **empty ecModel**, in which enzyme constraints
are not yet incorporated. See [Box 1](#box-1-extension-of-a-conventional-gem)
for the detailed 12-step algorithm.

## Set the default model adapter

**Step 8.** The model adapter is required by many GECKO functions. Instead of
passing it as an input parameter every time, set a default with the
`ModelAdapterManager`. This default is then used by all GECKO functions for the
rest of that MATLAB instance unless another adapter is explicitly given. Here
the adapter is assumed to be at
`GECKO/tutorials/full_ecModel/YeastGEMAdapter.m`:

```matlab
adapterLocation = fullfile(findGECKOroot, 'tutorials', ...
    'full_ecModel', 'YeastGEMAdapter.m');
ModelAdapterManager.setDefault(adapterLocation);
```

If desired, you can use the adapter explicitly as an input parameter, for
example when simulating multiple ecModels in the same MATLAB instance:

```matlab
ModelAdapter = ModelAdapterManager.getDefault();
```

Get a quick reference to the parameters in the model adapter:

```matlab
params = ModelAdapter.getParameters();
```

The rest of this protocol assumes a default model adapter is set.

!!! warning "Critical step"
    If any changes are made to the model adapter after setting it as default,
    for example editing `YeastGEMAdapter.m`, set it as default again:

    ```matlab
    ModelAdapterManager.setDefault(adapterLocation);
    ```

## Load the conventional GEM

**Step 9.** Load the conventional GEM into MATLAB. If its location is specified
in the model adapter (`obj.params.convGEM`):

```matlab
model = loadConventionalGEM();
```

Both YAML and XML files are supported. To load a model at a different location
or without a model adapter, use the usual RAVEN command for XML files:

```matlab
model = importModel('path/to/modelFile.xml');
```

Or for YAML files:

```matlab
model = readYAMLmodel('path/to/modelFile.yml');
```

!!! warning "Critical step"
    By default, GECKO loads models through RAVEN. If the model is loaded through
    the COBRA toolbox (recognizable by the `model.rules` field), convert it to
    the required RAVEN format (recognizable by the `model.metComps` field) with
    `ravenCobraWrapper()`.

## Choose full or light, then build

**Step 10.** Decide whether to reconstruct a full or light ecModel. This
decision affects the general structure of the model, and the two versions are
not interconvertible. Light ecModels are smaller and faster in simulations, but
a full ecModel is required to constrain individual enzymes by their
concentration (for example from proteomics data).

**Step 11.** Run one of the two commands.

Full ecModel:

```matlab
[ecModel, noUniprot] = makeEcModel(model);
```

Light ecModel:

```matlab
[ecModel, noUniprot] = makeEcModel(model, true);
```

The result is an empty ecModel: the model structure (see
[the ecModel.ec structure](stage2-kcat-integration.md#the-ecmodelec-structure))
is changed to allow enzyme constraints, but no constraints are applied yet.
While running, `makeEcModel` may report a warning about how gene associations
are specified in the starting GEM. This warning can be ignored if you are
confident the gene associations are correct; it does not prevent creation of an
ecModel.

!!! warning "Critical step"
    Occasionally not all model genes are found in UniProt. The `noUniprot` cell
    array contains those model genes without a UniProt match, reported as a
    warning. If `noUniprot` contains many genes, for example more than ten, it
    may be worth considering whether a different UniProt taxonomy or proteome
    identifier (Step 5) is more suitable.

## Apply enzyme complex stoichiometry (optional)

**Step 12.** In Step 11, `ecModel.ec.rxnEnzMat` is populated with single
subunits for enzyme complexes, but in reality the copy number of each subunit
can vary. GECKO can add this information from the
[Complex Portal](https://www.ebi.ac.uk/complexportal/complex/organisms) using
the taxonomic identifier in `obj.params.complex.taxonomicID`. The Complex Portal
has only a limited number of allowed taxonomic identifiers. Download and apply
the data:

```matlab
complexInfo = getComplexData();
[ecModel, foundComplex, proposedComplex] = ...
    applyComplexData(ecModel, complexInfo);
```

Note that `getComplexData` requires no input parameters; the required
parameters are gathered from the default model adapter. This behavior is shared
by several other GECKO functions.

!!! warning "Critical step"
    If Step 12 is omitted, or if information is missing for a particular
    complex, the ecModel assumes each subunit has a stoichiometry of one, which
    is not an unrealistic assumption for most complexes.

**Step 13.** Carefully inspect the content of `proposedComplex` and consider
whether manual curation of the respective ecModel gene association might be
appropriate. This may require additional literature study.

!!! warning "Critical step"
    `applyComplexData` only integrates complex data for a reaction if a full
    (100%) match is found between its ecModel gene association and the Complex
    Portal data. If no full match is found, `proposedComplex` suggests
    complexes with a partial match. A complex can be suggested when either
    (i) at least 75% of the ecModel genes of a reaction match a Complex Portal
    complex, or (ii) a Complex Portal complex contains more subunits than the
    genes associated to an ecModel reaction.

## Save the ecModel

**Step 14.** Save the ecModel to disk; this can be done at any point in the
procedure. To retain all ecModel content, including the `ecModel.ec` fields,
store it in YAML format. `saveEcModel` does this automatically in the adapter
folder, while the more generic `writeYAMLmodel` can store the file anywhere. To
load the model back into MATLAB, use `loadEcModel` or the generic
`readYAMLmodel`:

```matlab
saveEcModel(ecModel, 'ecModel.yml');
writeYAMLmodel(ecModel, 'C:\path\to\ecModel.yml');
ecModel = loadEcModel('ecModel.yml');
ecModel = readYAMLmodel('C:\path\to\ecModel.yml');
```

To enable constraint-based analysis in other software packages, it may be more
suitable to exchange the model in SBML format (with an XML extension). Use
`exportModel` and `importModel`, but be aware that this file does not retain the
`ecModel.ec` fields:

```matlab
exportModel(ecModel, 'C:\path\to\ecModelFull.xml');
ecModel = importModel('C:\path\to\ecModelFull.xml');
```

!!! warning "Critical step"
    Only the YAML format contains the `ecModel.ec` fields that are required to
    make modifications on the enzyme constraints of the ecModel.

## Box 1: Extension of a conventional GEM

To enable constraining metabolic reactions with enzyme constraints, the
conventional GEM is converted into an empty ecModel through up to 12 steps, some
of which are skipped for light models.

1. Any potential gene associations are removed from pseudo-reactions, since
   these are not assumed to be enzyme-catalyzed realistic metabolic reactions.
   Such reactions are identified either by a reaction name containing
   `pseudoreaction`, or by a reaction identifier listed in
   `data/pseudoRxns.tsv`.
2. Any irreversible reactions only allowed to carry a negative flux (lower bound
   < 0 and upper bound = 0) are inverted.
3. An `ecModel.rev` vector, indicating whether reactions are reversible, is
   defined from the vectors of lower and upper bounds.
4. Nearly all reversible reactions are split into forward and reverse reactions
   to yield an irreversible ecModel. The new (previously reverse) reactions have
   `_REV` appended to their identifier; the forward reaction keeps its
   identifier. The only exception is exchange reactions, which retain their
   original form and can still carry a negative flux.
5. *(Skipped for light ecModels)* Reactions catalyzed by isozymes (indicated by
   `or` in `ecModel.grRules`) are split so each reaction is catalyzed by one
   enzyme or complex. The new reactions are suffixed with `_EXP_` followed by a
   sequential number. For example, reaction `r_0001` catalyzed by two isozymes
   becomes `r_0001_EXP_1` and `r_0001_EXP_2`. A backward reaction `r_0001_REV`
   yields `r_0001_REV_EXP_1` and `r_0001_REV_EXP_2`. For light ecModels the
   identifiers remain unchanged.
6. An empty `ecModel.ec` structure is constructed, to be populated with enzymes,
   kcat values and reaction-enzyme associations.
7. Enzyme details such as MW and amino acid sequence are added to `ecModel.ec`,
   gathered from UniProt using the UniProt parameters in the model adapter.
8. `ecModel.ec.rxnEnzMat` indicates which reactions are catalyzed by which
   enzymes, momentarily by a 1, which can later be modified to reflect different
   numbers of subunits in a complex.
9. *(Skipped for light ecModels)* Enzymes are added as pseudo-metabolites and
   appear in `ecModel.mets` with the prefix `prot_` followed by the protein
   identifier. For instance, *S. cerevisiae* enolase gene YHR174W with UniProt
   identifier P00925 appears as pseudo-metabolite `prot_P00925`.
10. A protein pool pseudo-metabolite is added to `ecModel.mets`.
11. *(Skipped for light ecModels)* Usage reactions are added for the enzyme
    pseudo-metabolites, replenishing the enzymes used by catalyzing reactions.
    Their identifiers are `usage_` followed by the enzyme metabolite identifier,
    for example `usage_prot_P00925`.
12. An exchange reaction for the `prot_pool` pseudo-metabolite is added.
