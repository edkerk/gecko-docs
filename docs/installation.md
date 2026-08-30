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

GECKO is available as a MATLAB toolbox and as geckopy, a Python package. Both
implement the same procedure and can reconstruct, simulate and analyze the same
ecModels; pick whichever fits your existing workflow. This protocol shows
MATLAB and Python side by side throughout.

=== "MATLAB"

    - **MATLAB** version 2019b or above
      ([MathWorks](https://mathworks.com/products/matlab.html)). No additional
      MathWorks toolboxes are required.
    - **RAVEN toolbox** version 2.8.3 or above
      ([repository](https://github.com/SysBioChalmers/RAVEN)). RAVEN provides
      built-in functions used to reconstruct ecModels, and some RAVEN
      functions are also used to simulate and analyze ecModels.

=== "Python"

    - **Python** 3.11 or above.
    - **geckopy** ([repository](https://github.com/SysBioChalmers/geckopy)),
      built on [cobrapy](https://github.com/opencobra/cobrapy) for the
      constraint-based modeling layer and
      [raven-toolbox](https://github.com/SysBioChalmers/raven-toolbox) (the
      Python port of RAVEN) for model-manipulation primitives and ecModel YAML
      I/O. Both are pulled in automatically when installing geckopy.

    !!! note "geckopy is alpha, and not yet on PyPI"
        geckopy is under active development. All MATLAB GECKO functions used in
        the standard ecModel build are ported and the yeast-GEM tutorial runs
        end to end, but the package is not yet published to PyPI, so it is
        installed directly from GitHub (see below). Some steps in this
        protocol note where geckopy does not yet have an equivalent.

- **Gurobi Optimizer**
  ([product page](https://www.gurobi.com/solutions/gurobi-optimizer/)) is
  strongly recommended for simulations (a free academic license is available).
  Alternatively, SoPlex as part of the SCIP Optimization Suite
  ([scipopt.org](https://scipopt.org/)) can be used. Both MATLAB and Python use
  the same underlying solvers: MATLAB through RAVEN/the COBRA Toolbox, Python
  through cobrapy.
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

### RAVEN Toolbox / raven-toolbox

=== "MATLAB"

    Installation instructions are on the
    [RAVEN Wiki](https://github.com/SysBioChalmers/RAVEN/wiki/Installation). In
    brief, the RAVEN repository is downloaded via `git clone`, as a ZIP archive
    from GitHub, or installed as a MATLAB Add-On. Instructions for installing
    the recommended solver Gurobi are described on the
    [RAVEN wiki (solvers)](https://github.com/SysBioChalmers/RAVEN/wiki/Installation#solvers).

    After finishing all installation instructions, run the installation checks
    in MATLAB with:

    ```matlab
    checkInstallation;
    ```

=== "Python"

    raven-toolbox is a dependency of geckopy and is installed automatically
    with it (see [GECKO Toolbox / geckopy](#gecko-toolbox-geckopy) below); there
    is no separate installation step. raven-toolbox is also not yet on PyPI, so
    geckopy's install command pulls it directly from GitHub.

### GECKO Toolbox / geckopy

=== "MATLAB"

    The latest GECKO release can be installed as a
    [MATLAB Add-On](https://mathworks.com/help/matlab/matlab_env/get-add-ons.html).

    Alternatively, the GECKO toolbox can be obtained via `git clone` of the
    GECKO repository:

    ```bash
    git clone --depth=1 https://github.com/SysBioChalmers/GECKO
    ```

    As a third option, a ZIP archive of the GECKO toolbox can be downloaded
    from the
    [GitHub releases page](https://github.com/SysBioChalmers/GECKO/releases).
    The ZIP archive should be extracted to a disk location where the user has
    read and write access rights.

    After cloning or extracting, navigate in MATLAB to the GECKO folder,
    modifying the path to match its location:

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

=== "Python"

    geckopy and raven-toolbox are not yet on PyPI, so both are installed
    directly from their GitHub `develop` branches:

    ```bash
    pip install \
        git+https://github.com/SysBioChalmers/raven-toolbox.git@develop \
        git+https://github.com/SysBioChalmers/geckopy.git@develop
    ```

    Once both packages are published to PyPI, this will collapse to
    `pip install geckopy` (raven-toolbox will be pulled in transitively).

    Verify the install:

    ```bash
    python -c "import geckopy; print(geckopy.__version__)"
    ```

    To remove:

    ```bash
    pip uninstall geckopy raven-toolbox
    ```

    geckopy also installs a `geckopy` command-line tool, used in this protocol
    to scaffold new ecModel projects and to download UniProt/KEGG data (see
    [Stage 0](stage0-preparation.md)).

### Docker

Installation instructions are available at
[https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/).

!!! tip "Running DLKcat without Docker"
    If you have difficulty installing Docker Desktop, the `src/dlkcat-gecko/`
    folder contains all required Python scripts and data to run DLKcat with the
    `DLKcat.tsv` output from `writeDLKcatInput`. See the
    [Troubleshooting](troubleshooting.md) page for the terminal commands.

## Tutorial code

All code included in this protocol is also available as runnable tutorial
scripts, in both languages:

=== "MATLAB"

    In `GECKO/tutorials`:

    - Most code, related to a full ecModel, is demonstrated in
      `full_ecModel/protocol.m`, which reconstructs and analyzes a tutorial
      ecModel for *Saccharomyces cerevisiae*.
    - `light_ecModel/protocol.m` contains example code for making a light
      ecModel of the generic human-GEM.

=== "Python"

    In `geckopy/tutorials`:

    - `full_ecModel/protocol.py` mirrors the MATLAB full-ecModel tutorial
      step-for-step (same STEP numbers), covering Stages 0-3 plus Stages 4-5
      for *S. cerevisiae*.
    - `light_ecModel/protocol.py` demonstrates a light ecModel, using a small
      5-reaction demo model (`geckopy/examples/ecTestGEM`) rather than
      human-GEM, so the tutorial runs in seconds without external data.

Both tutorials, in both languages, generate ecModels that are only suitable for
use as part of the respective tutorials. The reconstructing code may contain
functions applied for demonstration purposes that depend on how the ecModel is
intended to be used. The ecModel may require additional curation and
evaluation.
