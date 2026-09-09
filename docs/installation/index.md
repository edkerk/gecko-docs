---
icon: material/folder-open
---

# Installation

GECKO is available as a **MATLAB toolbox** and as the **Python package
geckopy**. Both implement the same procedure and can reconstruct, simulate
and analyze the same ecModels: pick whichever fits your existing workflow.

## Equipment

A computer running macOS, Windows or Linux, with an internet connection to
reach [KEGG](https://www.genome.jp/kegg/), [UniProt](https://www.uniprot.org/),
[PubChem](https://pubchem.ncbi.nlm.nih.gov/) and
[GitHub](https://github.com/SysBioChalmers/GECKO/). Data from these sources
can also be downloaded or reconstructed manually elsewhere, but downloading
it directly through GECKO functions is the most convenient route.

The starting point is a conventional constraint-based metabolic model, at
genome scale or smaller, in SBML format L3V1 FBCv2. A well-curated model
produces a well-performing ecModel, but the procedure works on any valid
model, regardless of whether it belongs to a model organism.

## Software

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

- **MATLAB** version 2019b or above
  ([MathWorks](https://mathworks.com/products/matlab.html)). No additional
  MathWorks toolboxes are required.
- **RAVEN toolbox** version 2.8.3 or above
  ([repository](https://github.com/SysBioChalmers/RAVEN)), which provides
  the reconstruction functions GECKO builds on, and some of the functions
  used to simulate and analyze ecModels.
:::
:::{tab-item} 🐍 Python
:sync: python

- **Python** 3.11 or above.
- **geckopy** ([repository](https://github.com/SysBioChalmers/geckopy)),
  built on [cobrapy](https://github.com/opencobra/cobrapy) for the
  constraint-based modeling layer and
  [raven-toolbox](https://github.com/SysBioChalmers/raven-toolbox) (the
  Python port of RAVEN) for model-manipulation primitives and ecModel YAML
  I/O. Installing geckopy pulls in both dependencies automatically.
:::
::::

Both toolboxes also need a linear-programming solver (see
[Choosing a solver](#choosing-a-solver) below) and, for DLKcat,
[Docker](#docker).

## RAVEN toolbox / raven-toolbox

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

Installation instructions are on the
[RAVEN Wiki](https://github.com/SysBioChalmers/RAVEN/wiki/Installation): the
repository is downloaded via `git clone`, as a ZIP archive from GitHub, or
installed as a MATLAB Add-On. Instructions for installing the recommended
solver Gurobi are on the
[RAVEN wiki (solvers)](https://github.com/SysBioChalmers/RAVEN/wiki/Installation#solvers).

After finishing installation, run the checks in MATLAB:

```matlab
checkInstallation;
```
:::
:::{tab-item} 🐍 Python
:sync: python

raven-toolbox is a dependency of geckopy and installs automatically with it
(see [GECKO Toolbox / geckopy](#gecko-toolbox-geckopy) below); there is no
separate installation step.
:::
::::

(gecko-toolbox-geckopy)=
## GECKO Toolbox / geckopy

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

The latest GECKO release installs as a
[MATLAB Add-On](https://mathworks.com/help/matlab/matlab_env/get-add-ons.html):
Home → Add-Ons → Get Add-Ons → search "GECKO Toolbox".

Alternatively, clone the repository:

```bash
git clone --depth=1 https://github.com/SysBioChalmers/GECKO
```

or download a ZIP archive from the
[GitHub releases page](https://github.com/SysBioChalmers/GECKO/releases) and
extract it to a location with read and write access.

After cloning or extracting, navigate to the GECKO folder in MATLAB and
install it, which adds the GECKO subfolders to the MATLAB path:

```matlab
cd('path/to/GECKO')
GECKOInstaller.install
```

To remove:

```matlab
GECKOInstaller.uninstall
```
:::
:::{tab-item} 🐍 Python
:sync: python

geckopy and raven-toolbox are both pre-release on PyPI, so `--pre` is
required:

```bash
pip install --pre geckopy
```

geckopy's dependency on raven-toolbox already names a pre-release specifier,
which opts pip into matching pre-releases for that package too; `--pre`
alone is enough, raven-toolbox does not need naming separately. To pin the
exact versions of both instead of "whatever's newest":

```bash
pip install raven-toolbox==3.0.0b1 geckopy==4.0.0b1
```

For the development branch, ahead of the latest PyPI release, install from
GitHub instead:

```bash
pip install \
    git+https://github.com/SysBioChalmers/raven-toolbox.git@develop \
    git+https://github.com/SysBioChalmers/geckopy.git@develop
```

Verify the install:

```bash
python -c "import geckopy; print(geckopy.__version__)"
```

To remove:

```bash
pip uninstall geckopy raven-toolbox
```

geckopy also installs a `geckopy` command-line tool, used to scaffold new
ecModel projects and to download UniProt/KEGG data.
:::
::::

## Choosing a solver

| Solver | License | Good for |
|---|---|---|
| Gurobi | Free academic | Genome-scale models, sensitivity tuning, large ecModels (recommended) |
| SoPlex (SCIP Optimization Suite) | Open source | An open-source alternative to Gurobi |

Both MATLAB and Python use the same underlying solvers: MATLAB through RAVEN
and the COBRA Toolbox, Python through cobrapy.

## Docker

DLKcat runs in a Docker container. Installation instructions are at
[docs.docker.com/get-started/get-docker](https://docs.docker.com/get-started/get-docker/).

:::{tip} Running DLKcat without Docker
If installing Docker Desktop is difficult, the `src/dlkcat-gecko/` folder
contains the Python scripts and data needed to run DLKcat directly from the
`DLKcat.tsv` output of `writeDLKcatInput`.
:::

## Tutorial code

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

In `GECKO/tutorials`:

- `full_ecModel/protocol.m` reconstructs and analyzes a tutorial ecModel for
  *Saccharomyces cerevisiae*.
- `light_ecModel/protocol.m` builds a light ecModel of the generic
  human-GEM.
:::
:::{tab-item} 🐍 Python
:sync: python

In `geckopy/tutorials`:

- `full_ecModel/protocol.py` mirrors the MATLAB full-ecModel tutorial step
  for step, covering the full pipeline for *S. cerevisiae*.
- `light_ecModel/protocol.py` builds a light ecModel from a small
  5-reaction demo model (`geckopy/examples/ecTestGEM`), so it runs in
  seconds without external data.
:::
::::

Both tutorials, in both languages, generate ecModels suitable only for use
within the respective tutorials; the reconstructed models may need
additional curation before other use.
