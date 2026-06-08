# GECKO Toolbox 3.0 Protocol

**Reconstruction, simulation and analysis of enzyme-constrained metabolic models using GECKO Toolbox 3.0**

This documentation is a structured version of the published protocol:

> Chen, Y., Gustafsson, J., Tafur Rangel, A., Anton, M., Domenzain, I.,
> Kittikunapong, C., Li, F., Yuan, L., Nielsen, J. & Kerkhoven, E. J.
> *Reconstruction, simulation and analysis of enzyme-constrained metabolic
> models using GECKO Toolbox 3.0.* Nature Protocols **19**, 629-667 (2024).
> [https://doi.org/10.1038/s41596-023-00931-7](https://doi.org/10.1038/s41596-023-00931-7)

## What is GECKO?

Genome-scale metabolic models (GEMs) are computational representations that
enable mathematical exploration of metabolic behaviors within cellular and
environmental constraints. Despite their wide usage, there are many phenotypes
that GEMs cannot correctly predict.

GECKO is a method that enhances a **G**enome-scale metabolic model with
**E**nzymatic **C**onstraints using **K**inetic and **O**mics data. The result
is an enzyme-constrained model (ecModel) that shows better predictive
performance than a conventional GEM. GECKO 3.0 also incorporates deep
learning-predicted enzyme kinetics through DLKcat, which makes it possible to
build ecModels for virtually any organism or cell line even in the absence of
experimental data.

## How the protocol is organized

The procedure has a preparation stage followed by five stages. The first four
build the ecModel; the last one is for simulation and analysis.

| Stage | Topic | Steps | Approx. timing |
|-------|-------|-------|----------------|
| [Stage 0](stage0-preparation.md) | Preparation of project files and data | 1-7 | 15 min |
| [Stage 1](stage1-structure-expansion.md) | Expansion to an ecModel structure | 8-14 | 15 min |
| [Stage 2](stage2-kcat-integration.md) | Integration of kcat values | 15-32 | 1 h |
| [Stage 3](stage3-model-tuning.md) | Model tuning | 33-52 | 15 min |
| [Stage 4](stage4-proteomics.md) | Integration of proteomics data | 53-65 | 15 min |
| [Stage 5](stage5-simulation-analysis.md) | Simulation and analysis | 66-79 | 3 h |

The total runtime is organism dependent, for example about 5 hours for yeast.
Stages 1 to 3 are also applicable to light ecModels; Stage 4 is not, because
proteomics integration does not fit light ecModels.

## Quick start

1. Read the [Introduction](introduction.md) for the conceptual background.
2. Install the prerequisites in [Materials and installation](installation.md).
3. Work through the stages in order, beginning with
   [Stage 0](stage0-preparation.md).
4. Consult the [Troubleshooting](troubleshooting.md) and
   [Anticipated results](anticipated-results.md) pages as needed.

!!! note "Tutorial code"
    All code shown in this protocol is also available in `GECKO/tutorials`. The
    full ecModel workflow for *Saccharomyces cerevisiae* is in
    `full_ecModel/protocol.m`, and an example light ecModel of the generic
    human-GEM is in `light_ecModel/protocol.m`. Both tutorials generate models
    that are only suitable for use within the respective tutorials, and may
    require additional curation and evaluation.

## Source code

The GECKO toolbox is publicly available under the MIT license at
[https://github.com/SysBioChalmers/GECKO](https://github.com/SysBioChalmers/GECKO)
and archived at [https://doi.org/10.5281/zenodo.7699818](https://doi.org/10.5281/zenodo.7699818).
