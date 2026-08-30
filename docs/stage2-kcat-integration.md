# Stage 2: Integration of kcat values

!!! info "Timing"
    Approximately 1 hour (Steps 15-32). Deep learning prediction with DLKcat
    accounts for most of the time.

This stage integrates enzyme $k_{cat}$ values, together with the prepared enzyme
information, into the empty ecModel. Not every enzymatic reaction has a reported
measurement. GECKO can retrieve reported data from the BRENDA database for a
reaction when both the EC number and the substrate of the organism's reaction
match the $k_{cat}$ annotation. If multiple $k_{cat}$ values match, the maximum
is selected.

When a perfect match across organism, substrate and EC number is not found,
GECKO uses a set of hierarchical matching criteria:

- If the organism is not matched, the $k_{cat}$ of the phylogenetically closest
  organism is selected.
- If the substrate is not matched, the $k_{cat}$ for any alternative substrate
  is selected.
- If the EC number is not found, a fuzzy EC number (introducing wildcards) is
  used for matching.
- Where no $k_{cat}$ is available in BRENDA, specific activities (typically in
  micromol per min per mg protein) can be converted into $k_{cat}$ values.

The DLKcat package, which is independent of EC number, can complement these
BRENDA-based matches, particularly for less studied organisms, or even serve as
the sole $k_{cat}$ source. GECKO also allows manual curation of $k_{cat}$ values
from other sources, such as in vivo estimations and predictions by other
approaches.

Once the $k_{cat}$ values are obtained, enzymes with their protein costs in the
form of $MW/k_{cat}$ are added into all enzymatic reactions. The product of this
stage is a **draft ecModel**. This model is not yet functional, because the
protein pool is unlimited and the enzyme constraint is therefore not active.

## Choose kcat sources

**Step 15.** Decide which source(s) of $k_{cat}$ data to use. Any combination
can be used in any order, but at least one approach must be conducted:

- Fuzzy matching with the [BRENDA database](https://www.brenda-enzymes.org/).
- Deep learning prediction with DLKcat.
- A list of manually curated custom $k_{cat}$ values.
- Assignment of a standard $k_{cat}$ value.

## Fuzzy matching with BRENDA

**Step 16.** Gather reaction-specific $k_{cat}$ data from BRENDA, where
reactions are matched by EC numbers and substrate names. Because this allows
wildcards in the EC number or $k_{cat}$ values from other substrates, it is
called fuzzy matching.

**Step 17.** Assign EC numbers to reactions, either by reading them from the
`model.eccodes` field (if it exists) or by gathering them from UniProt and KEGG
annotations.

If the starting GEM has manually curated EC numbers, populate
`ecModel.ec.eccodes` with model-derived EC numbers, then fill in the rest from
the database. In MATLAB `getECfromDatabase` overwrites entries in
`ecModel.ec.eccodes`, so first define which entries were not populated:

=== "MATLAB"

    ```matlab
    ecModel = getECfromGEM(ecModel);
    noEC = cellfun(@isempty, ecModel.ec.eccodes);
    ecModel = getECfromDatabase(ecModel, noEC);
    ```

    If the starting GEM is not annotated with a `model.eccodes` field, does
    not contain standard EC numbers (four groups of digits separated by
    periods), or you have low confidence in its accuracy, only run
    `getECfromDatabase`:

    ```matlab
    ecModel = getECfromDatabase(ecModel);
    ```

    If desired, the EC numbers derived from the database can be transferred
    to the `model.eccodes` fields with `copyECtoGEM`.

=== "Python"

    ```python
    from geckopy import fill_eccodes_from_database, fill_eccodes_from_gem

    fill_eccodes_from_gem(ec_model)
    fill_eccodes_from_database(ec_model, uniprot_db)
    ```

    `fill_eccodes_from_database` only fills entries that are still empty, so
    there is no separate "which entries were not populated" step to manage —
    calling `fill_eccodes_from_gem` first and `fill_eccodes_from_database`
    second already has the same effect as the MATLAB two-call sequence. If the
    starting GEM's EC annotations should not be trusted, skip the
    `fill_eccodes_from_gem` call and only run `fill_eccodes_from_database`.
    The equivalent of `copyECtoGEM` is `copy_ec_to_gem`, which writes into
    each reaction's `annotation["ec-code"]` (cobrapy's convention) rather than
    a top-level `model.eccodes` cell array.

**Step 18.** After populating `ecModel.ec.eccodes`, gather $k_{cat}$ from BRENDA.
BRENDA is queried by EC number, substrate and organism:

=== "MATLAB"

    ```matlab
    kcatList_fuzzy = fuzzyKcatMatching(ecModel);
    ```

=== "Python"

    BRENDA data and the KEGG phylogenetic-distance file (used to find the
    phylogenetically closest organism when there's no exact match) are loaded
    explicitly, then passed in:

    ```python
    from geckopy import fuzzy_kcat_matching, load_brenda_data, load_phyl_dist

    brenda = load_brenda_data(adapter.get_brenda_db_folder())
    phyl_dist = load_phyl_dist(params.path / "data" / "PhylDist.mat")
    kcat_list_fuzzy = fuzzy_kcat_matching(ec_model, brenda, phyl_dist)
    ```

**Step 19.** Look at the results. The output is a `kcatList` structure
documenting which $k_{cat}$ could be assigned to each reaction and how precise
each match is (number of EC wildcards, and whether matched by substrate and
organism). It is common, even for model organisms such as *S. cerevisiae*, that
no full match is found, in which case partial organism or substrate matches are
returned. If no $k_{cat}$ is found for a particular EC number, wildcards are
introduced: for example EC 2.4.2.3 (uridine phosphorylase) becomes 2.4.2.-
(pentosyltransferase).

## Deep learning prediction with DLKcat

**Step 20.** Gather $k_{cat}$ through deep learning prediction with DLKcat,
based on enzyme sequence information and substrate structural information in
SMILES format.

**Step 21.** Because starting GEMs rarely include SMILES annotation, gather
these by querying PubChem, creating `data/smilesDB.tsv`, or manually populating
that file:

=== "MATLAB"

    ```matlab
    [ecModel, noSMILES] = findMetSmiles(ecModel);
    ```

    !!! warning "Critical step"
        `findMetSmiles` reports the percentage of unique metabolites assigned
        a SMILES annotation. If below 100%, as is almost always the case,
        inspect the `noSMILES` list of metabolite names. For example, in some
        models the metabolite name is suffixed with the metabolite formula,
        which prevents matching with PubChem. Manual curation of
        `ecModel.metNames` is required to resolve such issues.

=== "Python"

    ```python
    from geckopy import find_met_smiles

    find_met_smiles(ec_model, cache_path=params.path / "data" / "smilesDB.tsv")
    ```

    `find_met_smiles` mutates `ec_model` in place and reads/writes through the
    `cache_path` TSV — an existing cache (as shipped with the tutorial) means
    no PubChem network access is needed. Unmatched metabolites are logged
    rather than returned as a `noSMILES` list; check the log, and as in
    MATLAB, curate metabolite names (`metabolite.name`) if a formula suffix or
    similar naming issue prevents matching.

**Step 22.** Define which metabolites DLKcat should use. DLKcat does not run
natively in MATLAB and requires Python, but GECKO can write the required input
file. As part of this, currency metabolites that occur in pairs (for example ATP
versus ADP, NADH versus NAD) and a selection of small molecules (for example
Fe2+) are excluded. Nonexhaustive lists are provided under `GECKO/databases` as
`DLKcatCurrencyMets.tsv` and `DLKcatIgnore.tsv`; you can provide
ecModel-specific names by placing files with those same names under `data` in
your adapter folder. Currency metabolites are only excluded if the reactions
have other reactants after small-molecule removal, as for ATP synthase.

**Step 23.** Write the DLKcat input file to `data/DLKcat.tsv` in the adapter
folder. It contains, for example, amino acid sequences for proteins and SMILES
for metabolites:

=== "MATLAB"

    ```matlab
    writeDLKcatInput(ecModel);
    ```

    !!! warning "Critical step"
        Any `DLKcat.tsv` file is specific to either the full or the light
        version of the ecModel, because it contains the reaction identifiers
        from `ecModel.ec.rxns` needed when loading the predicted values back
        into MATLAB. Construct separate `DLKcat.tsv` files for the two
        ecModel versions.

=== "Python"

    ```python
    from geckopy import load_dlkcat_ignore_lists, write_dlkcat_input

    ignore_lists = load_dlkcat_ignore_lists(params.path / "data")
    write_dlkcat_input(
        ec_model, params.path / "data" / "DLKcat.tsv", ignore_lists,
    )
    ```

    `load_dlkcat_ignore_lists` reads the currency-metabolite and
    small-molecule exclusion lists (`DLKcatCurrencyMets.tsv` /
    `DLKcatIgnore.tsv`, or their project-specific overrides under `data/`)
    that MATLAB's `writeDLKcatInput` reads implicitly. The same
    full-vs-light `DLKcat.tsv` caveat applies: the file encodes
    `ec_model.ec.rxns` identifiers, so a full-model file cannot be reused for
    a light model or vice versa.

**Step 24.** Run the DLKcat prediction pipeline, which automatically downloads
and starts a Docker image. No other input parameters are given, because the
function assumes the input file is at `data/DLKcat.tsv`:

=== "MATLAB"

    ```matlab
    runDLKcat();
    ```

=== "Python"

    ```python
    from geckopy import run_dlkcat

    run_dlkcat(params.path / "data" / "DLKcat.tsv")
    ```

**Step 25.** Construct a `kcatList` structure by loading the DLKcat output back
in:

=== "MATLAB"

    ```matlab
    kcatList_DLKcat = readDLKcatOutput(ecModel);
    ```

=== "Python"

    ```python
    from geckopy import read_dlkcat_output

    kcat_list_dlkcat = read_dlkcat_output(
        ec_model, params.path / "data" / "DLKcat.tsv",
    )
    ```

## Merge DLKcat and BRENDA structures

**Step 26.** If $k_{cat}$ values are gathered from both DLKcat (Step 25) and
BRENDA (Step 18), merge the two `kcatList` structures to increase coverage:

=== "MATLAB"

    ```matlab
    kcatList_merged = mergeDLKcatAndFuzzyKcats(kcatList_DLKcat, kcatList_fuzzy);
    ```

=== "Python"

    ```python
    from geckopy import merge_dlkcat_and_fuzzy_kcats

    kcat_list_merged = merge_dlkcat_and_fuzzy_kcats(kcat_list_dlkcat, kcat_list_fuzzy)
    ```

    This is technically a thin wrapper kept for MATLAB-name parity — it calls
    the more general `merge_kcats(*kcat_lists, source_priority=...)` with the
    tiered priority `[best BRENDA matches, dlkcat, weaker BRENDA matches]`
    that matches the MATLAB behavior described below. For anything beyond
    this two-source case (for example merging in OpenKineticsPredictor
    results too), call `merge_kcats` directly with an explicit
    `source_priority`.

During this process, a single $k_{cat}$ is assigned to each reaction, with
priority given to BRENDA values from a full EC number match. By default,
mismatches on organism and substrate are allowed, modifiable through additional
input parameters. If no exact EC match is available, the DLKcat value is used.
If DLKcat could not predict a value for a reaction (for example because its
substrate had no SMILES), EC number wildcard matches from fuzzy matching are
allowed if available. For instance, instead of assigning a $k_{cat}$ to pyruvate
oxidase by querying EC 1.2.3.3, it queries EC 1.2.3.-, which includes any
oxidoreductase acting on the aldehyde or oxo group of donors with oxygen as
acceptor; the highest $k_{cat}$ from this group is selected. A more detailed
description of the fuzzy matching algorithm is in the GECKO 2 publication.

**Step 27.** Integrate the $k_{cat}$ data into the ecModel, using any
`kcatList` from a previous step. Here the merged list populates
`ecModel.ec.kcat`:

=== "MATLAB"

    ```matlab
    ecModel = selectKcatValue(ecModel, kcatList_merged);
    ```

=== "Python"

    ```python
    from geckopy import apply_kcat_list

    apply_kcat_list(ec_model, kcat_list_merged)
    ```

    `select_kcat_value` also exists as a deprecated alias of
    `apply_kcat_list`.

## Provide custom kcat values

**Step 28.** Custom $k_{cat}$ values can be provided as an alternative or sole
source. They can be based on manual curation, on results from later in the
procedure, or on another prediction procedure such as in vivo apparent enzyme
turnover numbers. Document them in `data/customKcats.tsv` in the adapter
folder, mapped to reactions or enzymes, and apply them:

=== "MATLAB"

    ```matlab
    [ecModel, rxnUpdated, notMatch] = applyCustomKcats(ecModel);
    ```

    This overwrites existing values in `ecModel.ec.kcat` for matching
    reactions, assuming the custom values have higher confidence. Pay
    attention if `notMatch` contains reactions, because their values were not
    successfully applied. A common reason is that the gene association
    between the model and the input file matches less than 50%. To resolve,
    inspect and manually curate the input file.

=== "Python"

    ```python
    from geckopy import apply_custom_kcats

    apply_custom_kcats(ec_model, path=params.path / "data" / "customKcats.tsv")
    ```

    Same overwrite behavior and same 50%-gene-match threshold for a match to
    be applied; unmatched rows are logged rather than returned as a
    `notMatch` list.

!!! warning "Critical step"
    Functions that populate `ecModel.ec.kcat`, such as `selectKcatValue` and
    `applyCustomKcats` (and others below), can be run in any order. Unless
    otherwise specified, they overwrite existing values and document the source
    in `ecModel.ec.source`, for example `brenda` or `custom`.

## Mean kcat of isozymes (optional)

**Step 29.** Situations occur where $k_{cat}$ values are not defined for all
isozymatic variants. The reaction variant associated with the isozyme lacking a
$k_{cat}$ then has no protein cost and would be preferred over variants that do.
To avoid this, missing values in `ecModel.ec.kcat` can be substituted by the
mean $k_{cat}$ of their isozymes:

=== "MATLAB"

    ```matlab
    ecModel = getKcatAcrossIsozymes(ecModel);
    ```

=== "Python"

    ```python
    from geckopy import fill_kcats_from_isozymes

    fill_kcats_from_isozymes(ec_model)
    ```

    `get_kcat_across_isozymes` also exists as a deprecated alias.

This situation is not relevant for light ecModels, where only the most
efficient isozyme is considered — in Python, calling `fill_kcats_from_isozymes`
on a light ecModel (`ec_model.ec.gecko_light == True`) raises
`NotImplementedError`, matching this MATLAB restriction.

## Assign a standard kcat value (optional)

**Step 30.** Reactions without genes associated in the starting GEM (empty
entries in `model.grRules`) cannot have enzyme constraints added, because of the
lack of enzyme data. For such reactions (excluding exchange, spontaneous,
transport and pseudo-reactions), a standard $k_{cat}$ and a standard
pseudo-enzyme (`prot_standard`) can be included to constrain catalytic capacity.
Standard $k_{cat}$ values are calculated as (i) the mean of $k_{cat}$ values of
reactions in the same subsystem, or (ii) the mean of all $k_{cat}$ values in
`ecModel.ec.kcat` if no subsystem is defined. A standard MW is calculated as the
median of all proteins in the organism, and a `usage_prot_standard` reaction is
added:

=== "MATLAB"

    ```matlab
    [ecModel, rxnsMissingGPR, standardMW, standardKcat] = getStandardKcat(ecModel);
    ```

    The standard MW and the subsystem-agnostic standard $k_{cat}$ are reported
    in `standardMW` and `standardKcat`.

=== "Python"

    ```python
    from geckopy import assign_standard_kcat

    assign_standard_kcat(ec_model, uniprot_db)
    ```

    `get_standard_kcat` also exists as a deprecated alias of
    `assign_standard_kcat`. The reactions that were missing a GPR, the
    standard MW and the standard kcat are logged rather than returned.

## Apply the enzyme constraints

**Step 31.** After populating `ecModel.ec.kcat` from the various sources, apply
the enzyme constraints:

=== "MATLAB"

    ```matlab
    ecModel = applyKcatConstraints(ecModel);
    ```

=== "Python"

    ```python
    from geckopy import apply_kcat_constraints

    apply_kcat_constraints(ec_model)
    ```

This modifies the S-matrix (`ecModel.S` / the cobra reaction stoichiometries in
Python) to directly include the protein cost, based on the $k_{cat}$ values
from `ecModel.ec.kcat`, the MWs from `ecModel.ec.mw` and, if relevant, the
enzyme complex stoichiometry from `applyComplexData`/`apply_complex_data`. The
enzymes are directly involved as pseudo-substrates to reflect enzyme usage.
This function can be run at any point to re-apply the $k_{cat}$, MW and
complex data.

## Constrain the protein pool exchange reaction

**Step 32.** The enzyme pseudo-metabolites are, by default, replenished from the
total protein pool. The protein pool exchange reaction should therefore be
constrained by a realistic value, calculated from the sigma, $P_{tot}$ and f
parameters in the model adapter (average enzyme saturation, total protein
content and fraction of proteins included in the model):

=== "MATLAB"

    ```matlab
    ecModel = setProtPoolSize(ecModel);
    ```

    If quantitative proteomics data are available, for example via PaxDB,
    store them in `data/paxDB.tsv` and calculate the f factor:

    ```matlab
    f = calculateFfactor(ecModel);
    ```

    Then use this new f factor to set the protein pool constraint:

    ```matlab
    ecModel = setProtPoolSize(ecModel, [], f);
    ```

=== "Python"

    ```python
    from geckopy import set_prot_pool_size

    set_prot_pool_size(ec_model, p_tot=params.p_tot, f=params.f, sigma=params.sigma)
    ```

    With no arguments beyond `ec_model`, `set_prot_pool_size` reads `p_tot`,
    `f` and `sigma` from `ec_model.adapter.params`, so the explicit keyword
    arguments above are only needed to override them. If quantitative
    proteomics data are available via PaxDB, store them in `data/paxDB.tsv`
    and calculate the f factor:

    ```python
    from geckopy import calculate_f_factor, load_pax_db

    pax_data = load_pax_db(params.path / "data" / "paxDB.tsv")
    f = calculate_f_factor(ec_model, pax_data)
    ```

    Then use this new f factor to set the protein pool constraint:

    ```python
    set_prot_pool_size(ec_model, f=f)
    ```

## The ecModel.ec structure

The internal enzyme-related information is stored in `ecModel.ec` (MATLAB) or
`ec_model.ec` (Python, an `EcData` instance). The field names are the same
between languages except for `rxnEnzMat` / `rxn_enz_mat`; the structure is
similar for full and light ecModels but differs in how the reaction-related
fields are populated. In full ecModels the whole model is expanded, each
isozyme gets a separate reaction, and each reaction maps to a reaction in the
structure. In light ecModels the reactions are not split per isozyme, but there
are several reaction entities in the structure for some starting-GEM reactions.

| Field | Data type | Size | Description |
|-------|-----------|------|-------------|
| `rxns` | string array (Python: `list[str]`) | m | Reaction identifiers gathered from the ecModel (after expansion and making irreversible). |
| `rxnEnzMat` (Python: `rxn_enz_mat`) | matrix (Python: sparse `scipy.sparse.csr_matrix`) | m x n | Comparable to `rxnGeneMat`, but Enz refers to `ecModel.ec.enzymes`. Positive integers indicate the number of enzyme subunits annotated to each reaction. |
| `kcat` | float vector (Python: `numpy.ndarray`) | m | One value per reaction-enzyme (complex) combination, in s^-1. Gathered from various sources. |
| `source` | string array (Python: `list[str]`) | m | Where the kcat is derived from, for example `dlkcat`, `brenda`, `standard` or `custom`. |
| `notes` | string array (Python: `list[str]`) | m | Any notes the user wants to add. |
| `eccodes` | string array (Python: `list[str]`) | m | EC numbers gathered from the ecModel and/or UniProt/KEGG. Only used for fuzzy kcat matching. |
| `genes` | string array (Python: `list[str]`) | n | Gene identifiers, corresponding to `ecModel.genes`, matching the columns in `rxnEnzMat`. |
| `enzymes` | string array (Python: `list[str]`) | n | UniProt protein identifiers derived from the matching entries in `genes`. |
| `mw` | string array (Python: `numpy.ndarray`) | n | MW for each enzyme, in Dalton. |
| `sequence` | string array (Python: `list[str]`) | n | Amino acid sequence for each enzyme. |
| `concs` | float vector (Python: `numpy.ndarray`) | n | Measured concentration of each enzyme in mg/gDCW. |

geckopy adds two convenience properties not present as MATLAB fields:
`ec_model.ec.n_rxns` and `ec_model.ec.n_enzymes` (the m and n sizes above), and
a `gecko_light: bool` flag recording which layout the model uses.
