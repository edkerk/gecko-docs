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

**Step 8.** The model adapter is required by many GECKO functions.

=== "MATLAB"

    Instead of passing it as an input parameter every time, set a default with
    the `ModelAdapterManager`. This default is then used by all GECKO
    functions for the rest of that MATLAB instance unless another adapter is
    explicitly given. Here the adapter is assumed to be at
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
        If any changes are made to the model adapter after setting it as
        default, for example editing `YeastGEMAdapter.m`, set it as default
        again:

        ```matlab
        ModelAdapterManager.setDefault(adapterLocation);
        ```

=== "Python"

    geckopy has no global default adapter: every function that needs one takes
    it as an explicit argument (no `ModelAdapterManager` equivalent). Load it
    once and pass it (or `params`, its `.params` attribute) to each call:

    ```python
    from pathlib import Path
    from geckopy import ModelAdapter

    adapter = ModelAdapter.from_folder(Path("GECKO/tutorials/full_ecModel"))
    params = adapter.params
    ```

    If the adapter file changes, reload it by calling `from_folder` again;
    there is no separate "set as default" step to repeat.

## Load the conventional GEM

**Step 9.** Load the conventional GEM.

=== "MATLAB"

    Load the model into MATLAB. If its location is specified in the model
    adapter (`obj.params.convGEM`):

    ```matlab
    model = loadConventionalGEM();
    ```

    Both YAML and XML files are supported. To load a model at a different
    location or without a model adapter, use the usual RAVEN command for XML
    files:

    ```matlab
    model = importModel('path/to/modelFile.xml');
    ```

    Or for YAML files:

    ```matlab
    model = readYAMLmodel('path/to/modelFile.yml');
    ```

    !!! warning "Critical step"
        By default, GECKO loads models through RAVEN. If the model is loaded
        through the COBRA toolbox (recognizable by the `model.rules` field),
        convert it to the required RAVEN format (recognizable by the
        `model.metComps` field) with `ravenCobraWrapper()`.

=== "Python"

    Load the model. If its location is specified in the model adapter
    (`params.conv_gem`):

    ```python
    from geckopy import load_conventional_gem

    model = load_conventional_gem(adapter)
    ```

    This returns a plain `cobra.Model`, so there is no RAVEN/COBRA format
    distinction to manage: cobrapy is the native format throughout geckopy,
    and no conversion step is needed. To load a model at a different location
    or without an adapter, use cobrapy directly:

    ```python
    import cobra

    model = cobra.io.read_sbml_model("path/to/modelFile.xml")
    ```

    For a YAML file in RAVEN/GECKO's YAML schema, use raven-toolbox's reader
    (installed automatically with geckopy):

    ```python
    from raven_toolbox.io import read_yaml_model

    model = read_yaml_model("path/to/modelFile.yml")
    ```

## Choose full or light, then build

**Step 10.** Decide whether to reconstruct a full or light ecModel. This
decision affects the general structure of the model, and the two versions are
not interconvertible. Light ecModels are smaller and faster in simulations, but
a full ecModel is required to constrain individual enzymes by their
concentration (for example from proteomics data).

**Step 11.** Build the ecModel.

=== "MATLAB"

    Full ecModel:

    ```matlab
    [ecModel, noUniprot] = makeEcModel(model);
    ```

    Light ecModel:

    ```matlab
    [ecModel, noUniprot] = makeEcModel(model, true);
    ```

    While running, `makeEcModel` may report a warning about how gene
    associations are specified in the starting GEM. This warning can be
    ignored if you are confident the gene associations are correct; it does
    not prevent creation of an ecModel.

    !!! warning "Critical step"
        Occasionally not all model genes are found in UniProt. The
        `noUniprot` cell array contains those model genes without a UniProt
        match, reported as a warning. If `noUniprot` contains many genes, for
        example more than ten, it may be worth considering whether a
        different UniProt taxonomy or proteome identifier (Step 5) is more
        suitable.

    !!! tip "GECKO 4: KEGG fallback for genes UniProt can't match"
        Not part of the original protocol: if the KEGG database is also
        loaded (Step 5-7), `makeEcModel` now consults it for genes that
        UniProt couldn't match, before giving up on them — `ec.enzymes`
        gets the UniProt accession carried on the matching KEGG row, or the
        bare KEGG gene id if that row has no accession of its own (flagged
        in a separate warning, since a bare KEGG id isn't a standard UniProt
        accession). This can shrink `noUniprot` without any adapter changes.

=== "Python"

    Full ecModel (`gecko_light` defaults to `False`):

    ```python
    from geckopy import make_ec_model

    ec_model = make_ec_model(model, adapter)
    ```

    Light ecModel:

    ```python
    ec_model = make_ec_model(model, adapter, gecko_light=True)
    ```

    UniProt data is loaded automatically from `params.path / "data" /
    "uniprot.tsv"`; pass a pre-loaded `uniprot_db=` to use a different file
    or avoid re-reading it across multiple calls. Pass a pre-loaded
    `kegg_db=` for the same KEGG fallback described in the GECKO 4 tip
    above — `None` (the default) skips it, matching the current MATLAB
    behavior when no KEGG database is loaded.

    !!! warning "Critical step"
        `make_ec_model` returns only the built `EcModel`, not a second
        `noUniprot`-style list. Unmatched genes are instead logged as a
        warning summary and recorded on the affected reactions themselves,
        in `reaction.notes["geckopy_warning"]`. As in MATLAB, if many genes
        are unmatched it is worth reconsidering the UniProt taxonomy or
        proteome identifier (Step 5).

The result is an empty ecModel either way: the model structure (see
[the ecModel.ec structure](stage2-kcat-integration.md#the-ecmodelec-structure))
is changed to allow enzyme constraints, but no constraints are applied yet.

## Apply enzyme complex stoichiometry (optional)

**Step 12.** In Step 11, `ecModel.ec.rxnEnzMat` is populated with single
subunits for enzyme complexes, but in reality the copy number of each subunit
can vary. GECKO can add this information from the
[Complex Portal](https://www.ebi.ac.uk/complexportal/complex/organisms) using
the taxonomic identifier in `obj.params.complex.taxonomicID`. The Complex Portal
has only a limited number of allowed taxonomic identifiers. Download and apply
the data:

=== "MATLAB"

    ```matlab
    complexInfo = getComplexData();
    [ecModel, foundComplex, proposedComplex] = ...
        applyComplexData(ecModel, complexInfo);
    ```

    Note that `getComplexData` requires no input parameters; the required
    parameters are gathered from the default model adapter. This behavior is
    shared by several other GECKO functions.

=== "Python"

    ```python
    from geckopy import apply_complex_data

    apply_complex_data(ec_model, path=params.path / "data" / "ComplexPortal.json")
    ```

    `apply_complex_data` mutates `ec_model` in place (no `foundComplex` /
    `proposedComplex` return values yet). To (re)download the Complex Portal
    data first, use `get_complex_data`, which does take the adapter
    explicitly (Python functions generally take the adapter or its
    parameters as an argument rather than reading a global default):

    ```python
    from geckopy import get_complex_data

    get_complex_data(adapter)
    ```

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
store it in YAML format.

=== "MATLAB"

    `saveEcModel` does this automatically in the adapter folder, while the
    more generic `writeYAMLmodel` can store the file anywhere. To load the
    model back into MATLAB, use `loadEcModel` or the generic `readYAMLmodel`:

    ```matlab
    saveEcModel(ecModel, 'ecModel.yml');
    writeYAMLmodel(ecModel, 'C:\path\to\ecModel.yml');
    ecModel = loadEcModel('ecModel.yml');
    ecModel = readYAMLmodel('C:\path\to\ecModel.yml');
    ```

    To enable constraint-based analysis in other software packages, it may be
    more suitable to exchange the model in SBML format (with an XML
    extension). Use `exportModel` and `importModel`, but be aware that this
    file does not retain the `ecModel.ec` fields:

    ```matlab
    exportModel(ecModel, 'C:\path\to\ecModelFull.xml');
    ecModel = importModel('C:\path\to\ecModelFull.xml');
    ```

=== "Python"

    `save_ec_model` writes YAML, either in the adapter folder or at an
    arbitrary path; `load_ec_model` reads it back:

    ```python
    from geckopy import load_ec_model, save_ec_model

    save_ec_model(ec_model, "ecModel.yml", adapter=adapter)
    save_ec_model(ec_model, r"C:\path\to\ecModel.yml")
    ec_model = load_ec_model("ecModel.yml", adapter=adapter)
    ec_model = load_ec_model(r"C:\path\to\ecModel.yml")
    ```

    geckopy does not provide a separate SBML export for ecModels — YAML is the
    only format that round-trips the `ec` fields. Since `ec_model` is a
    `cobra.Model`, plain cobrapy SBML I/O still works for interoperating with
    other tools, with the same caveat as MATLAB's `exportModel`: the `ec`
    fields are not retained.

    ```python
    import cobra

    cobra.io.write_sbml_model(ec_model, r"C:\path\to\ecModelFull.xml")
    model = cobra.io.read_sbml_model(r"C:\path\to\ecModelFull.xml")
    ```

!!! warning "Critical step"
    Only the YAML format contains the `ecModel.ec` fields (`ec_model.ec` in
    Python) that are required to make modifications on the enzyme constraints
    of the ecModel.

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
   kcat values and reaction-enzyme associations. (Python: `ec_model.ec`, an
   `EcData` instance with the same fields under snake_case names — see
   [the ecModel.ec structure](stage2-kcat-integration.md#the-ecmodelec-structure).)
7. Enzyme details such as MW and amino acid sequence are added to `ecModel.ec`,
   gathered from UniProt using the UniProt parameters in the model adapter.
8. `ecModel.ec.rxnEnzMat` (Python: `ec_model.ec.rxn_enz_mat`) indicates which
   reactions are catalyzed by which enzymes, momentarily by a 1, which can
   later be modified to reflect different numbers of subunits in a complex.
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

!!! tip "GECKO 4: usage and pool exchange reactions already run forward"
    Steps 11-12 above describe the original GECKO 3.0 protocol, where both
    the `usage_prot_*` reactions and the `prot_pool_exchange` reaction carry
    a *negative* flux (`bounds = (-1000, 0)`): protein flows out of
    `prot_pool` into each enzyme, and out of the model at
    `prot_pool_exchange`. Current GECKO has already flipped both to the more
    intuitive *forward* direction (`bounds = (0, 1000)`) —
    [PR #419](https://github.com/SysBioChalmers/GECKO/pull/419):
    `usage_prot_*` consumes `prot_pool` to produce `prot_<enzyme>`, and
    `prot_pool_exchange` supplies `prot_pool` in the first place. Every
    dependent function was updated to match: `setProtPoolSize`,
    `addNewRxnsToEC`, `getStandardKcat`, `constrainEnzConcs`,
    `flexibilizeEnzConcs`, `updateProtPool`, `getConcControlCoeffs`,
    `getSubsetEcModel`, `enzymeUsage`, `reportEnzymeUsage` and
    `sensitivityTuning`. geckopy implements this same forward convention
    throughout (it targets current GECKO, not the GECKO 3.0 protocol). This
    changes which bound you touch to relax a constraint and which objective
    coefficient minimizes usage — see the note in
    [Stage 3](stage3-model-tuning.md#too-tight-protein-pool-constraint) for
    the worked example.
