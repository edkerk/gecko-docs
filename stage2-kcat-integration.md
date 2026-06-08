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
`ecModel.ec.eccodes` with model-derived EC numbers using `getECfromGEM`. Because
`getECfromDatabase` overwrites entries in `ecModel.ec.eccodes`, first define
which entries were not populated:

```matlab
ecModel = getECfromGEM(ecModel);
noEC = cellfun(@isempty, ecModel.ec.eccodes);
ecModel = getECfromDatabase(ecModel, noEC);
```

If the starting GEM is not annotated with a `model.eccodes` field, does not
contain standard EC numbers (four groups of digits separated by periods), or you
have low confidence in its accuracy, only run `getECfromDatabase`:

```matlab
ecModel = getECfromDatabase(ecModel);
```

If desired, the EC numbers derived from the database can be transferred to the
`model.eccodes` fields with `copyECtoGEM`.

**Step 18.** After populating `ecModel.ec.eccodes`, gather $k_{cat}$ from BRENDA.
BRENDA is queried by EC number, substrate and organism:

```matlab
kcatList_fuzzy = fuzzyKcatMatching(ecModel);
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
these by querying PubChem with `findMetSmiles`, creating `data/smilesDB.tsv`, or
manually populating that file:

```matlab
[ecModel, noSMILES] = findMetSmiles(ecModel);
```

!!! warning "Critical step"
    `findMetSmiles` reports the percentage of unique metabolites assigned a
    SMILES annotation. If below 100%, as is almost always the case, inspect the
    `noSMILES` list of metabolite names. For example, in some models the
    metabolite name is suffixed with the metabolite formula, which prevents
    matching with PubChem. Manual curation of `ecModel.metNames` is required to
    resolve such issues.

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

```matlab
writeDLKcatInput(ecModel);
```

!!! warning "Critical step"
    Any `DLKcat.tsv` file is specific to either the full or the light version of
    the ecModel, because it contains the reaction identifiers from
    `ecModel.ec.rxns` needed when loading the predicted values back into MATLAB.
    Construct separate `DLKcat.tsv` files for the two ecModel versions.

**Step 24.** Run the DLKcat prediction pipeline, which automatically downloads
and starts a Docker image. No other input parameters are given, because the
function assumes the input file is at `data/DLKcat.tsv`:

```matlab
runDLKcat();
```

**Step 25.** Construct a `kcatList` structure by loading the DLKcat output back
into MATLAB:

```matlab
kcatList_DLKcat = readDLKcatOutput(ecModel);
```

## Merge DLKcat and BRENDA structures

**Step 26.** If $k_{cat}$ values are gathered from both DLKcat (Step 25) and
BRENDA (Step 18), merge the two `kcatList` structures to increase coverage:

```matlab
kcatList_merged = mergeDLKcatAndFuzzyKcats(kcatList_DLKcat, kcatList_fuzzy);
```

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

**Step 27.** Integrate the $k_{cat}$ data into the ecModel with
`selectKcatValue`, using any `kcatList` from a previous step. Here the merged
list populates `ecModel.ec.kcat`:

```matlab
ecModel = selectKcatValue(ecModel, kcatList_merged);
```

## Provide custom kcat values

**Step 28.** Custom $k_{cat}$ values can be provided as an alternative or sole
source. They can be based on manual curation, on results from later in the
procedure, or on another prediction procedure such as in vivo apparent enzyme
turnover numbers. Document them in `data/customKcats.tsv` in the adapter folder,
mapped to reactions or enzymes, and apply them:

```matlab
[ecModel, rxnUpdated, notMatch] = applyCustomKcats(ecModel);
```

This overwrites existing values in `ecModel.ec.kcat` for matching reactions,
assuming the custom values have higher confidence. Pay attention if `notMatch`
contains reactions, because their values were not successfully applied. A common
reason is that the gene association between the model and the input file matches
less than 50%. To resolve, inspect and manually curate the input file.

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

```matlab
ecModel = getKcatAcrossIsozymes(ecModel);
```

This situation is not relevant for light ecModels, where only the most efficient
isozyme is considered.

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

```matlab
[ecModel, rxnsMissingGPR, standardMW, standardKcat] = getStandardKcat(ecModel);
```

The standard MW and the subsystem-agnostic standard $k_{cat}$ are reported in
`standardMW` and `standardKcat`.

## Apply the enzyme constraints

**Step 31.** After populating `ecModel.ec.kcat` from the various sources, apply
the enzyme constraints:

```matlab
ecModel = applyKcatConstraints(ecModel);
```

This modifies the `ecModel.S` matrix to directly include the protein cost, based
on the $k_{cat}$ values from `ecModel.ec.kcat`, the MWs from `ecModel.ec.mw` and,
if relevant, the enzyme complex stoichiometry from `applyComplexData`. The
enzymes are directly involved as pseudo-substrates to reflect enzyme usage. This
function can be run at any point to re-apply the $k_{cat}$, MW and complex data.

## Constrain the protein pool exchange reaction

**Step 32.** The enzyme pseudo-metabolites are, by default, replenished from the
total protein pool. The protein pool exchange reaction should therefore be
constrained by a realistic value, calculated from the sigma, $P_{tot}$ and f
parameters in the model adapter (average enzyme saturation, total protein
content and fraction of proteins included in the model):

```matlab
ecModel = setProtPoolSize(ecModel);
```

If quantitative proteomics data are available, for example via PaxDB, store them
in `data/paxDB.tsv` and calculate the f factor:

```matlab
f = calculateFfactor(ecModel);
```

Then use this new f factor to set the protein pool constraint:

```matlab
ecModel = setProtPoolSize(ecModel, [], f);
```

## The ecModel.ec structure

The internal enzyme-related information is stored in `ecModel.ec`. The structure
is similar for full and light ecModels but differs in how the reaction-related
fields are populated. In full ecModels the whole model is expanded, each
isozyme gets a separate reaction, and each reaction maps to a reaction in the
structure. In light ecModels the reactions are not split per isozyme, but there
are several reaction entities in the structure for some starting-GEM reactions.

| Field | Data type | Size | Description |
|-------|-----------|------|-------------|
| `rxns` | string array | m | Reaction identifiers gathered from the ecModel (after expansion and making irreversible). |
| `rxnEnzMat` | matrix | m x n | Comparable to `rxnGeneMat`, but Enz refers to `ecModel.ec.enzymes`. Positive integers indicate the number of enzyme subunits annotated to each reaction. |
| `kcat` | float vector | m | One value per reaction-enzyme (complex) combination, in s^-1. Gathered from various sources. |
| `source` | string array | m | Where the kcat is derived from, for example `dlkcat`, `brenda`, `standard` or `custom`. |
| `notes` | string array | m | Any notes the user wants to add. |
| `eccodes` | string array | m | EC numbers gathered from the ecModel and/or UniProt/KEGG. Only used for fuzzy kcat matching. |
| `genes` | string array | n | Gene identifiers, corresponding to `ecModel.genes`, matching the columns in `rxnEnzMat`. |
| `enzymes` | string array | n | UniProt protein identifiers derived from the matching entries in `genes`. |
| `mw` | string array | n | MW for each enzyme, in Dalton. |
| `sequence` | string array | n | Amino acid sequence for each enzyme. |
| `concs` | float vector | n | Measured concentration of each enzyme in mg/gDCW. |
