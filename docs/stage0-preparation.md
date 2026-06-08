# Stage 0: Preparation of project files and data

!!! info "Timing"
    Approximately 15 minutes (Steps 1-7).

This stage generates files and prepares the data and parameters for ecModel
reconstruction, simulation and analysis. The ideal starting material is a
highly curated conventional constraint-based metabolic model of the organism of
interest. If such a model is not available, one can reconstruct it from scratch
or from template models following published protocols within public toolboxes.

In addition to the starting GEM file, each ecModel requires a **model adapter**,
a text file that is loaded as a MATLAB structure. The organism-specific data and
parameters are collated and populated into this adapter file.

## Project file structure

**Step 1.** Generate a new GECKO project file structure:

```matlab
startGECKOproject();
```

This automatically prepares a new folder in the location of your choice. The
folder contains four subfolders:

- `code` and `data` keep custom code and data for ecModel reconstruction and
  analysis.
- `models` and `output` save reconstructed ecModels and simulation results.

A description of the files in the `data` folder is given in the
[Files in the data folder](#files-in-the-data-folder) table below.

**Step 2.** Store the starting GEM. Using the `models` subfolder is recommended
for convenience and reproducibility, but other paths can be used. For the rest
of this protocol, the model-specific folder `tutorials/full_ecModel` is referred
to as the **adapter folder**, because it is where the model adapter is found.

## Model adapter

**Step 3.** Running `startGECKOproject()` in Step 1 generates a template model
adapter in the new adapter folder. In MATLAB, the model adapter is a class that
inherits the `ModelAdapter` base class, and you can override standard behaviors
implemented in the base class to adapt to a specific model.

**Step 4.** Before initiating reconstruction, populate the model adapter file
with organism- and model-specific information. An overview is given in the
[Model adapter parameters](#model-adapter-parameters) table below. If a
parameter cannot be defined, for example because the information is absent or
not relevant, comment out the line with `%`. For instance, if the organism is
not on KEGG:

```matlab
% obj.params.kegg.ID = '';
```

**Step 5.** Query the UniProt and KEGG databases using appropriate model adapter
parameters, following the guidelines in
[UniProt](#a-uniprot) and [KEGG](#b-kegg) below. The UniProt database is the
source of enzyme MWs and amino acid sequences (essential), while KEGG can be
used to assign EC number annotations (useful but optional).

It is critical to select the query parameters carefully so that the data
gathered from UniProt and KEGG refer to genes with the same style of identifiers
as those used in the starting GEM.

### (A) UniProt

!!! warning "Critical"
    Data can be identified either by proteome (i) or by taxonomy (iv). The
    proteome option is preferred, because it tends to avoid redundant matches
    between gene and protein identifiers.

1. Search for organism-specific proteome datasets on UniProt at
   [https://www.uniprot.org/proteomes](https://www.uniprot.org/proteomes).
2. If multiple proteome datasets are available for the same organism,
   preferentially choose a
   [reference proteome](https://www.uniprot.org/proteomes?facets=proteome_type%3A1&query=%2A).
3. When a potential proteome is identified, examine the UniProt page for one of
   its proteins to confirm that it refers to its gene with the same style of
   identifiers as used in the starting GEM. This is typically found under
   "Names & Taxonomy - Gene names".

    For example, searching for *Saccharomyces cerevisiae* yields 93 UniProt
    proteomes, one of which is the reference proteome for strain S288c
    (proteome UP00000231). On the UniProt page for one of its proteins, the gene
    identifier styled as `YFL026W` can be found, which matches the style used in
    the yeast-GEM. This style is marked as "Ordered locus name", accessible in
    the API via `gene_oln`. In the model adapter, set `uniprot.type` to
    `proteome`, `uniprot.ID` to `UP00000231` and `uniprot.geneIDfield` to
    `gene_oln`.

4. While most organisms have a defined proteome based on all proteins in their
   genome, [taxonomy](https://www.uniprot.org/taxonomy/) can also be used to
   identify UniProt datasets. The taxonomy identifier should be as specific as
   possible.

    For example, for *S. cerevisiae* the taxonomy identifier 4932 refers to 322
    different strains with 53,526 proteins in total, whereas 559292 refers to
    strain S288c with 6,735 proteins. In that case, `uniprot.type` is `taxonomy`
    and `uniprot.ID` is `559292`.

### (B) KEGG

1. Choose the correct KEGG-specific three- or four-letter species identifier
   (the `kegg.ID` in the model adapter) from
   [https://www.genome.jp/kegg/catalog/org_list.html](https://www.genome.jp/kegg/catalog/org_list.html).
   For *Homo sapiens* the KEGG identifier is `hsa`.
2. To check that the correct gene identifier is linked, refer to the genome
   entry page (for example
   [https://www.genome.jp/entry/hsa](https://www.genome.jp/entry/hsa)), which
   contains a link to the list of KEGG genes. For *H. sapiens* the genes are
   sequentially numbered, which does not match the identifiers used in the
   human-GEM. Instead, under "Other DBs", Ensembl gene identifiers are provided
   (for example `ENSG00000236362`). For human-GEM, `kegg.geneID` in the model
   adapter should therefore be `Ensembl` instead of `KEGG`.

## Handling unusual identifier formats

**Step 6.** If an organism is included in UniProt but no satisfactory
`uniprot.geneIDfield` can be identified in Step 5 (the model gene identifiers
are not in any UniProt field), manually construct a conversion table at
`data/uniprotConversion.tsv` with columns of model genes and UniProt
identifiers.

For example, the *Escherichia coli* model iML1515 uses gene identifiers styled
as `b0008`, which are not individually mentioned in UniProt, but KEGG carries
both identifiers. Reconstruct the required `uniprotConversion.tsv` with the
following code (the model adapter must already be loaded, see
[Stage 1, Step 8](stage1-structure-expansion.md#set-the-default-model-adapter)):

```matlab
DB = loadDatabases('kegg');
fID = fopen(fullfile(params.path, 'data', 'uniprotConversion.tsv'), 'w');
output = transpose([DB.kegg.keggGene, DB.kegg.uniprot]);
fprintf(fID, '%s\t%s\n', 'genes', 'uniprot');
fprintf(fID, '%s\t%s\n', output{:});
fclose(fID);
```

While this *E. coli* example gathers the conversion table from KEGG, other
organisms may require different data sources. For human-GEM (provided with GECKO
at `tutorials/light_ecModel`), a conversion table is distributed together with
the starting GEM and converted to `uniprotConversion.tsv` as detailed in
`tutorials/light_ecModel/protocol.m`.

**Step 7.** If an organism is not included in UniProt or KEGG, preventing
definition of appropriate parameters in Step 5, manually reconstruct the
database files. Use the `data/kegg.tsv` and `data/uniprot.tsv` files from
`full_ecModel` as templates for organizing the data. Artificial UniProt and
KEGG IDs can be used in these reconstituted files, but the real MW and sequence
of each protein are required for the rest of the protocol to function.

## Reference tables

### Files in the data folder

| File | Description | Steps |
|------|-------------|-------|
| `ComplexPortal.json` | Information on enzyme complexes retrieved from the Complex Portal, automatically downloaded by `getComplexData`. | 12, 13 |
| `customKcats.tsv` | Manually curated kcat values for specific enzymes or reactions. Constructed by the user from other data sources. Example in the `full_ecModel` tutorial. | 28 |
| `DLKcat.tsv` | Input file for DLKcat, filled in with predicted kcat values. Generated by `writeDLKcatInput`. | 23, 24 |
| `fluxData.tsv` | Experimental data such as growth rate, protein content and carbon source uptake, used to constrain the ecModel during proteomics integration. Exchange fluxes in mmol/gDCWh; uptake rates negative, excretion positive. Growth rate and carbon source uptake rate are essential. Not required for the initial reconstruction (Stages 1-3). | 59 |
| `kegg.tsv` | KEGG information for the organism. Must contain UniProt protein ID, gene, KEGG gene ID, EC number, MW, pathway and sequence. Used for assigning EC numbers. Downloaded by `loadDatabases`. | 5-7, 17 |
| `paxDB.tsv` | Protein abundance file used to compute the f factor (proxy for the mass fraction of proteins accounted for in the ecModel). Can be retrieved from [https://pax-db.org](https://pax-db.org). If absent, a default f factor of 0.5 is used. | 32 |
| `proteomics.tsv` | Measured protein levels (mg protein/gDCW) from one or more experiments. First column has UniProt identifiers; each subsequent column has protein levels from individual experiment replicates. | 54-56 |
| `smilesDB.tsv` | SMILES for metabolites in `ecModel.mets`. Generated when `findMetSmiles` queries the PubChem database. | 21-23 |
| `uniprot.tsv` | UniProt data for the organism. Must contain protein identifier, gene identifier, EC number, MW and sequence. Downloaded by `loadDatabases`. | 5-7, 11, 17 |
| `uniprotConversion.tsv` | Conversion table needed if UniProt has no field with the genes in the same format as `ecModel.genes`. First column is `ecModel.genes`, second is the UniProt identifier. Constructed by the user. Example in the `light_ecModel` tutorial. | 6 |

### Model adapter parameters

These are the `obj.params` entries in the model adapter. The example values come
from the `full_ecModel` tutorial.

| Parameter | Example | Explanation |
|-----------|---------|-------------|
| `bioRxn` | `r_4041` | Reaction identifier for the biomass or growth pseudo-reaction, whose flux is the growth rate in h^-1. |
| `c_source` | `r_1714` | Reaction identifier for the glucose exchange reaction (or other preferred carbon source). |
| `complex.taxonomicID` | `559292` | Taxonomic identifier as available from the [Complex Portal](https://www.ebi.ac.uk/complexportal/home). |
| `convGEM` | `fullfile(obj.params.path, 'models', 'yeast-GEM.xml')` | Path to the starting conventional GEM file. |
| `enzyme_comp` | `cytoplasm` | Compartment name in which added enzymes are located; should match `ecModel.compNames`. |
| `f` | `0.5` | Fraction of enzymes in the ecModel relative to all proteins (g enzyme/g protein). `calculateFfactor()` can compute it from a proteomics dataset. |
| `kegg.geneID` | `kegg` | The gene identifier or database link from KEGG that corresponds to the ecModel genes; for human-GEM this should be `Ensembl`. |
| `kegg.ID` | `sce` | Organism ID in the KEGG database, selected from the [KEGG organism list](https://www.genome.jp/kegg/catalog/org_list.html). |
| `org_name` | `saccharomyces cerevisiae` | Scientific name of the organism, used by `fuzzyKcatMatching`. |
| `path` | `fullfile(findGECKOroot, 'tutorials', 'full_ecModel')` | Path to the directory where all ecModel-specific content is found. Set in Step 8. |
| `Ptot` | `0.5` | Total protein content in the cell (g protein/gDCW). |
| `sigma` | `0.5` | Average enzyme saturation factor sigma. |
| `uniprot.geneIDfield` | `gene_oln` | UniProt field with the gene identifiers used in the ecModel. Must be one of the "Returned Field" entries under "Names & Taxonomy". |
| `uniprot.ID` | `UP00000231` | Identifier of the UniProt dataset (by taxonomy or proteome) with complete coverage of the ecModel genes. |
| `uniprot.type` | `proteome` | Whether a taxonomy or proteome is provided in `uniprot.ID`. |
| `uniprot.reviewed` | `true` | Whether only reviewed UniProt data should be considered. Reviewed data has the highest confidence but may have low coverage for nonmodel organisms. |
