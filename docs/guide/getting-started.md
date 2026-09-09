# Getting started

An ecModel reconstruction starts from a curated conventional genome-scale
metabolic model (GEM) and a **model adapter**: a file that collates the
organism-specific data and parameters every later step reads. Creating a
project scaffolds both the folder layout and a template model adapter to
fill in.

## Functions on this page

| MATLAB | Python | |
|---|---|---|
| `startGECKOproject` | `geckopy init` | scaffold a new project folder |
| `ModelAdapter` (classdef) | `ModelAdapter.from_folder` | define and load the model adapter |
| `loadDatabases('kegg')` | `geckopy kegg-download` | download KEGG data for identifier conversion |

## Start a new project

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
startGECKOproject();
```

A dialog prompts for a location and creates the new folder there.
:::
:::{tab-item} 🐍 Python
:sync: python

```bash
geckopy init myproject
```

`init` is a subcommand of the `geckopy` command-line tool installed
alongside the package (see [Installation](../installation/index.md)). Add
`--advanced` to also scaffold the Bayesian kcat-tuning hyperparameter
section described in
[Tuning against experimental data](tuning-against-experimental-data.md).
:::
::::

The new folder contains four subfolders: `code` and `data` hold custom code
and data used during reconstruction and analysis; `models` and `output` hold
reconstructed ecModels and simulation results. Store the starting GEM under
`models`; other locations work too, but keeping it there makes the project
self-contained. The folder that contains the model adapter is called the
**adapter folder** throughout this guide.

`data` files use the same formats (TSV, JSON) in both languages, so a
project's `data` folder built with one toolbox can be reused with the other.
[Reference tables](#reference) at the end of this page lists every file that
belongs there and where it gets populated.

## The model adapter

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

The model adapter is a class that inherits the `ModelAdapter` base class.
Parameters are assigned in its constructor, and organism-specific behavior
that a plain value cannot express (for example a non-standard way to
identify spontaneous reactions) is added by overriding a method of the base
class.

```matlab
classdef ecYeastGEMAdapter < ModelAdapter
    methods
        function obj = ecYeastGEMAdapter()
            obj.params.path = fullfile(findGECKOroot, 'tutorials', 'full_ecModel');
            obj.params.convGEM = fullfile(obj.params.path, 'models', 'yeast-GEM.xml');
            obj.params.org_name = 'saccharomyces cerevisiae';

            obj.params.sigma = 0.5;
            obj.params.Ptot = 0.5;
            obj.params.f = 0.5;
            obj.params.gR_exp = 0.41;

            obj.params.c_source = 'r_1714';
            obj.params.bioRxn = 'r_4041';
            obj.params.enzyme_comp = 'cytoplasm';

            obj.params.uniprot.type = 'proteome';
            obj.params.uniprot.ID = 'UP000002311';
            obj.params.uniprot.geneIDfield = 'gene_oln';
            obj.params.uniprot.reviewed = true;

            obj.params.kegg.ID = 'sce';
            obj.params.kegg.geneID = 'kegg';

            obj.params.complex.taxonomicID = 559292;
        end
    end
end
```
:::
:::{tab-item} 🐍 Python
:sync: python

The model adapter is a `model_adapter.toml` file, loaded with
`ModelAdapter.from_folder(path)`. The same values as the MATLAB class above,
from the `full_ecModel` tutorial:

```toml
conv_gem = "models/yeast-GEM.yml"
org_name = "saccharomyces cerevisiae"

sigma = 0.5
p_tot = 0.5
f = 0.5
gr_exp = 0.41

c_source = "r_1714"
bio_rxn = "r_4041"
enzyme_comp = "cytoplasm"

[kegg]
id = "sce"
gene_id = "kegg"

[uniprot]
type = "proteome"
id = "UP000002311"
gene_id_field = "gene_oln"
reviewed = true

[complex]
taxonomic_id = 559292
```

`geckopy init` also scaffolds an `adapter.py` stub next to the TOML file,
for organism-specific behavior that cannot be expressed as a plain value
(analogous to overriding a method on the MATLAB `ModelAdapter` base class).
Most projects only edit the TOML file and leave `adapter.py` untouched.
:::
::::

If a parameter cannot be defined, because the information is absent or not
relevant, comment it out (MATLAB) or omit the key (Python). For an organism
not on KEGG:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
% obj.params.kegg.ID = '';
```
:::
:::{tab-item} 🐍 Python
:sync: python

```toml
# [kegg]
# id = ""
```
:::
::::

### Querying UniProt and KEGG

The UniProt database is the source of enzyme molecular weights and amino
acid sequences and is essential; KEGG can assign EC number annotations and
is useful but optional. The query parameters must select data that identify
genes with the same style of identifier as the starting GEM: a mismatch
here means enzyme data cannot be matched to model genes later.

:::{warning} Proteome over taxonomy
UniProt data can be identified either by proteome or by taxonomy. Proteome
is preferred, because it avoids redundant matches between gene and protein
identifiers.
:::

To find a UniProt proteome dataset, search
[uniprot.org/proteomes](https://www.uniprot.org/proteomes) for the organism.
If several proteome datasets exist for the same organism, prefer a
[reference proteome](https://www.uniprot.org/proteomes?facets=proteome_type%3A1&query=%2A).
Then open the UniProt page for one of its proteins and check, under "Names &
Taxonomy - Gene names", that its gene identifiers use the same style as the
starting GEM.

For example, *Saccharomyces cerevisiae* has 93 UniProt proteomes, one of
which is the reference proteome for strain S288c (`UP000002311`). A protein
in that proteome carries the gene identifier `YFL026W`, which matches the
style used in yeast-GEM; UniProt labels this style "Ordered locus name",
returned by the API field `gene_oln`. The model adapter accordingly sets
`uniprot.type` to `proteome`, `uniprot.ID` to `UP000002311` and
`uniprot.geneIDfield` to `gene_oln`.

Taxonomy is the alternative when no proteome fits: the
[taxonomy browser](https://www.uniprot.org/taxonomy/) identifier should be
as specific as possible. For *S. cerevisiae* the taxonomy identifier 4932
covers 322 strains and 53,526 proteins in total, while 559292 refers to
strain S288c alone, at 6,735 proteins. In that case `uniprot.type` is
`taxonomy` and `uniprot.ID` is `559292`.

For KEGG, choose the three- or four-letter species identifier (`kegg.ID`)
from the
[KEGG organism list](https://www.genome.jp/kegg/catalog/org_list.html); for
*Homo sapiens* this is `hsa`. Then check which gene identifier KEGG links to
its genes, on the genome entry page (for example
[genome.jp/entry/hsa](https://www.genome.jp/entry/hsa)), which links to the
list of KEGG genes. For *H. sapiens* those genes are numbered sequentially,
which does not match the identifiers used in human-GEM; the "Other DBs"
section of the same page instead lists Ensembl gene identifiers (for
example `ENSG00000236362`). `kegg.geneID` for human-GEM is therefore
`Ensembl`, not `KEGG`.

## Handling unusual identifier formats

If an organism is in UniProt but no `uniprot.geneIDfield` matches the
model's gene identifiers, build a conversion table at
`data/uniprotConversion.tsv` with columns of model genes and UniProt
identifiers.

For example, the *Escherichia coli* model iML1515 uses gene identifiers
styled as `b0008`, which UniProt does not carry as a field, but KEGG links
both identifiers. Build `uniprotConversion.tsv` from KEGG data (this
requires a model adapter that is already loaded; see
[Building an empty ecModel](building-ec-model.md#set-the-default-model-adapter)):

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
DB = loadDatabases('kegg');
fID = fopen(fullfile(params.path, 'data', 'uniprotConversion.tsv'), 'w');
output = transpose([DB.kegg.keggGene, DB.kegg.uniprot]);
fprintf(fID, '%s\t%s\n', 'genes', 'uniprot');
fprintf(fID, '%s\t%s\n', output{:});
fclose(fID);
```
:::
:::{tab-item} 🐍 Python
:sync: python

geckopy downloads KEGG data through the `geckopy` CLI rather than a Python
function, writing a CSV with `uniprot`, `gene`, `kegg_gene` and further EC,
MW, pathway and sequence columns:

```bash
geckopy kegg-download eco data/kegg.csv
```

Select the two relevant columns and write them out as
`uniprotConversion.tsv`:

```python
import pandas as pd

kegg = pd.read_csv(params.path / "data" / "kegg.csv")
kegg[["kegg_gene", "uniprot"]].rename(columns={"kegg_gene": "genes"}).to_csv(
    params.path / "data" / "uniprotConversion.tsv", sep="\t", index=False,
)
```
:::
::::

Other organisms may need a different source for the conversion table. For
human-GEM, a conversion table ships with the starting GEM and is converted
to `uniprotConversion.tsv` in the `light_ecModel` tutorial's
`protocol.m`/`protocol.py`.

If an organism is in neither UniProt nor KEGG, the database files
themselves need to be built manually: use `data/kegg.tsv` and
`data/uniprot.tsv` from the `full_ecModel` tutorial as templates for their
column layout. Artificial UniProt and KEGG identifiers work in these
reconstructed files, but the molecular weight and sequence of each protein
must be accurate for the rest of the reconstruction to work.

:::{note} Example output
Scaffolding a project produces empty `code`, `data`, `models` and `output`
subfolders, plus a template model adapter file named after the model and
suffixed `Adapter.m` (MATLAB) or `model_adapter.toml` (Python). Populating
the model adapter, then querying UniProt and KEGG, fills `data/uniprot.tsv`
and `data/kegg.tsv`. If no UniProt or KEGG parameters could be identified
for the organism, `data/uniprotConversion.tsv`, `data/kegg.tsv` and
`data/uniprot.tsv` are constructed by hand instead, as described above.
:::

## Reference

### Files in the data folder

| File | Description | Used in |
|---|---|---|
| `ComplexPortal.json` | Enzyme complex information retrieved from the Complex Portal, downloaded by `getComplexData` (Python: `get_complex_data`). | [Building an empty ecModel](building-ec-model.md) |
| `customKcats.tsv` | Manually curated kcat values for specific enzymes or reactions, constructed by the user from other data sources. | [Applying kcats](applying-kcats.md) |
| `DLKcat.tsv` | Input and, once run, output for DLKcat kcat prediction. Generated by `writeDLKcatInput` (Python: `write_dlkcat_input`). | [Gathering kcats](gathering-kcats.md) |
| `fluxData.tsv` | Experimental growth rate, protein content and carbon-source uptake, used to constrain the ecModel during proteomics integration. Exchange fluxes in mmol/gDCWh; uptake negative, excretion positive. Not required for the initial reconstruction. | [Proteomics integration](proteomics-integration.md) |
| `kegg.tsv` | KEGG information for the organism: UniProt protein ID, gene, KEGG gene ID, EC number, MW, pathway and sequence. Downloaded by `loadDatabases` (Python: `geckopy kegg-download`). | Getting started, [Gathering kcats](gathering-kcats.md) |
| `paxDB.tsv` | Protein abundance data used to compute the f factor (the mass fraction of proteins accounted for in the ecModel). Retrieved from [pax-db.org](https://pax-db.org). Without it, f defaults to 0.5. | [Applying kcats](applying-kcats.md) |
| `proteomics.tsv` | Measured protein levels (mg protein/gDCW) from one or more experiments: UniProt identifiers in the first column, protein levels from individual replicates in each subsequent column. | [Proteomics integration](proteomics-integration.md) |
| `smilesDB.tsv` | SMILES for metabolites in `ecModel.mets`, generated when `findMetSmiles` (Python: `find_met_smiles`) queries PubChem. | [Gathering kcats](gathering-kcats.md) |
| `uniprot.tsv` | UniProt data for the organism: protein identifier, gene identifier, EC number, MW and sequence. Downloaded by `loadDatabases` (Python: `geckopy uniprot-download`). | Getting started, [Building an empty ecModel](building-ec-model.md) |
| `uniprotConversion.tsv` | Conversion table needed when no UniProt field carries genes in the same format as `ecModel.genes`. First column is `ecModel.genes`, second is the UniProt identifier. Constructed by the user. | Getting started |

### Model adapter parameters

These are the `obj.params` entries in the MATLAB model adapter, and the
corresponding TOML keys in the Python `model_adapter.toml` (dotted keys are
`[section]` tables; see the example above). Example values come from the
`full_ecModel` tutorial.

| MATLAB parameter | Python (TOML) | Example | Explanation |
|-------------------|---------------|---------|-------------|
| `bioRxn` | `bio_rxn` | `r_4041` | Reaction identifier for the biomass or growth pseudo-reaction, whose flux is the growth rate in h^-1. |
| `c_source` | `c_source` | `r_1714` | Reaction identifier for the glucose exchange reaction (or other preferred carbon source). |
| `complex.taxonomicID` | `complex.taxonomic_id` | `559292` | Taxonomic identifier as available from the [Complex Portal](https://www.ebi.ac.uk/complexportal/home). |
| `convGEM` | `conv_gem` | `fullfile(obj.params.path, 'models', 'yeast-GEM.xml')` (MATLAB) / `"models/yeast-GEM.yml"` (Python) | Path to the starting conventional GEM file. |
| `enzyme_comp` | `enzyme_comp` | `cytoplasm` | Compartment name in which added enzymes are located; must match `ecModel.compNames`. |
| `f` | `f` | `0.5` | Fraction of enzymes in the ecModel relative to all proteins (g enzyme/g protein). `calculateFfactor()` (Python: `calculate_f_factor`) computes it from a proteomics dataset. |
| `gR_exp` | `gr_exp` | `0.41` | Reference (experimentally observed) maximum growth rate in h^-1, the default tuning target in [Growth-rate tuning](growth-rate-tuning.md#sensitivity-tuning-of-kcat-values). |
| `kegg.geneID` | `kegg.gene_id` | `kegg` | The gene identifier or database link from KEGG that corresponds to the ecModel genes; for human-GEM this is `Ensembl`. |
| `kegg.ID` | `kegg.id` | `sce` | Organism ID in the KEGG database, from the [KEGG organism list](https://www.genome.jp/kegg/catalog/org_list.html). |
| `org_name` | `org_name` | `saccharomyces cerevisiae` | Scientific name of the organism, used by `fuzzyKcatMatching` (Python: `fuzzy_kcat_matching`). |
| `path` | `path` | `fullfile(findGECKOroot, 'tutorials', 'full_ecModel')` (MATLAB) | Path to the directory holding all ecModel-specific content. In Python, `path` is set automatically to the folder passed to `ModelAdapter.from_folder()`, not written in the TOML file itself. |
| `Ptot` | `p_tot` | `0.5` | Total protein content in the cell (g protein/gDCW). |
| `sigma` | `sigma` | `0.5` | Average enzyme saturation factor sigma. |
| `uniprot.geneIDfield` | `uniprot.gene_id_field` | `gene_oln` | UniProt field with the gene identifiers used in the ecModel. Must be one of the "Returned Field" entries under "Names & Taxonomy". |
| `uniprot.ID` | `uniprot.id` | `UP000002311` | Identifier of the UniProt dataset (by taxonomy or proteome) with complete coverage of the ecModel genes. |
| `uniprot.type` | `uniprot.type` | `proteome` | Whether `uniprot.ID` is a taxonomy or a proteome identifier. |
| `uniprot.reviewed` | `uniprot.reviewed` | `true` | Whether only reviewed UniProt data is considered. Reviewed data has the highest confidence but may have low coverage for nonmodel organisms. |

## See also

- [Building an empty ecModel](building-ec-model.md), the next step: loading
  the conventional GEM and expanding it into an ecModel structure.
- [API reference](../api/index.md), every function in both toolboxes.
- [MATLAB vs Python](../matlab-vs-python.md), what each toolbox has.
