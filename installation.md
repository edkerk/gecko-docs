# Materials and installation

## Equipment

- A personal computer running MacOS, Windows or Unix.
- An internet connection to access the following resources. The data obtained
  from them can also be downloaded or reconstructed manually on another
  computer, but direct download through GECKO functions is most convenient.
    - KEGG: [https://www.genome.jp/kegg/](https://www.genome.jp/kegg/)
    - UniProt: [https://www.uniprot.org/](https://www.uniprot.org/)
    - PubChem: [https://pubchem.ncbi.nlm.nih.gov/](https://pubchem.ncbi.nlm.nih.gov/)
    - GitHub: [https://github.com/SysBioChalmers/GECKO/](https://github.com/SysBioChalmers/GECKO/)

## Software

- **MATLAB** version 2019b or above
  ([MathWorks](https://mathworks.com/products/matlab.html)). No additional
  MathWorks toolboxes are required.
- **RAVEN toolbox** version 2.8.3 or above
  ([repository](https://github.com/SysBioChalmers/RAVEN)). RAVEN provides
  built-in functions used to reconstruct ecModels, and some RAVEN functions are
  also used to simulate and analyze ecModels.
- **Gurobi Optimizer**
  ([product page](https://www.gurobi.com/solutions/gurobi-optimizer/)) is
  strongly recommended for simulations (a free academic license is available).
  Alternatively, SoPlex as part of the SCIP Optimization Suite
  ([scipopt.org](https://scipopt.org/)) can be used.
- **Docker** ([docker.com](https://www.docker.com/)) for running DLKcat.

## Equipment setup

### Conventional metabolic model

The conventional constraint-based metabolic model can either be at genome scale
(a GEM) or describe a smaller metabolic network. The steps of the procedure
assume that the starting model is a GEM. The model should be provided in the
community standard Systems Biology Markup Language (SBML) format L3V1 FBCv2.
Whether a model is in valid SBML format can be tested through the
[SBML Validator](https://synonym.caltech.edu/validator_servlet/).

- A well-curated model will result in a well-performing ecModel. However, this
  protocol works on any model, regardless of whether it is for a model organism.
- Conventional constraint-based metabolic models can be obtained from the
  literature or from databases such as the
  [BioModels database](https://www.ebi.ac.uk/biomodels/).

### RAVEN Toolbox

Installation instructions are on the
[RAVEN Wiki](https://github.com/SysBioChalmers/RAVEN/wiki/Installation). In
brief, the RAVEN repository is downloaded via `git clone`, as a ZIP archive from
GitHub, or installed as a MATLAB Add-On. Instructions for installing the
recommended solver Gurobi are described on the
[RAVEN wiki (solvers)](https://github.com/SysBioChalmers/RAVEN/wiki/Installation#solvers).

After finishing all installation instructions, run the installation checks in
MATLAB with:

```matlab
checkInstallation;
```

### GECKO Toolbox

The latest GECKO release can be installed as a
[MATLAB Add-On](https://mathworks.com/help/matlab/matlab_env/get-add-ons.html).

Alternatively, the GECKO toolbox can be obtained via `git clone` of the GECKO
repository:

```bash
git clone --depth=1 https://github.com/SysBioChalmers/GECKO
```

As a third option, a ZIP archive of the GECKO toolbox can be downloaded from the
[GitHub releases page](https://github.com/SysBioChalmers/GECKO/releases). The
ZIP archive should be extracted to a disk location where the user has read and
write access rights.

After cloning or extracting, navigate in MATLAB to the GECKO folder, modifying
the path to match its location:

```matlab
cd('path/to/GECKO')
```

Install GECKO, which adds the GECKO subfolders to the MATLAB path:

```matlab
GECKOInstaller.install
```

If desired, a removal command is available:

```matlab
GECKOInstaller.uninstall
```

### Docker

Installation instructions are available at
[https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/).

!!! tip "Running DLKcat without Docker"
    If you have difficulty installing Docker Desktop, the `src/dlkcat-gecko/`
    folder contains all required Python scripts and data to run DLKcat with the
    `DLKcat.tsv` output from `writeDLKcatInput`. See the
    [Troubleshooting](troubleshooting.md) page for the terminal commands.

## Tutorial code

All code included in this protocol is also available in `GECKO/tutorials`.

- Most code, related to a full ecModel, is demonstrated in
  `full_ecModel/protocol.m`, which reconstructs and analyzes a tutorial ecModel
  for *Saccharomyces cerevisiae*.
- `light_ecModel/protocol.m` contains example code for making a light ecModel of
  the generic human-GEM.

Both tutorials generate ecModels that are only suitable for use as part of the
respective tutorials. The reconstructing code may contain functions applied for
demonstration purposes that depend on how the ecModel is intended to be used.
The ecModel may require additional curation and evaluation.
