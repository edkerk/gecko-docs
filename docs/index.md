<div class="gd-hero">
  <img class="gd-hero-logo" src="assets/gecko-logo.png" alt="GECKO">
  <p class="gd-tag">MATLAB &amp; Python</p>
  <h1>Enzyme-Constrained Genome-Scale<br>Metabolic Modeling</h1>
  <p class="gd-tagline">Reconstruction, simulation and analysis of enzyme-constrained metabolic models (ecModels) — a MATLAB toolbox built on RAVEN, and geckopy, a Python port built on cobrapy.</p>
  <div class="gd-badges">
    <span class="gd-badge">MIT license</span>
    <span class="gd-badge">MATLAB R2019b+</span>
    <span class="gd-badge">geckopy (alpha)</span>
    <span class="gd-badge">RAVEN &amp; cobrapy</span>
    <span class="gd-badge">DLKcat</span>
    <span class="gd-badge">Gurobi · SoPlex</span>
    <span class="gd-badge">Nat Protoc 19, 629–667</span>
  </div>
</div>

<div class="gd-install">
  <div class="gd-install-tabs">
    <button class="gd-itab active" data-cmd="Home &rarr; Add-Ons &rarr; Get Add-Ons &rarr; search GECKO Toolbox" data-plain>MATLAB (Add-Ons)</button>
    <button class="gd-itab" data-cmd="git clone --depth=1 https://github.com/SysBioChalmers/GECKO">MATLAB (git)</button>
    <button class="gd-itab" data-cmd="pip install \&#10;    git+https://github.com/SysBioChalmers/raven-toolbox.git@develop \&#10;    git+https://github.com/SysBioChalmers/geckopy.git@develop">Python (pip, from GitHub)</button>
  </div>
  <div class="gd-code-row">
    <code id="gd-cmd">Home &rarr; Add-Ons &rarr; Get Add-Ons &rarr; search GECKO Toolbox</code>
    <button class="gd-copy" onclick="navigator.clipboard.writeText(document.getElementById('gd-cmd').innerText)" title="Copy to clipboard" aria-label="Copy">&#10697;</button>
  </div>
</div>

<p class="gd-section-label">Key features</p>

<div class="grid cards gd-features" markdown>

-   :material-scale-balance:{ .gd-feat-icon }

    **Enzyme constraints**

    Convert a conventional GEM into an ecModel by bounding reaction rates with enzyme kcat and abundance.

-   :material-brain:{ .gd-feat-icon }

    **DLKcat kinetics**

    Fill in missing turnover numbers with deep-learning-predicted kcat values, no experimental data required.

-   :material-chart-bell-curve:{ .gd-feat-icon }

    **Proteomics integration**

    Constrain individual enzyme usage with absolute or relative proteomics measurements.

-   :material-feather:{ .gd-feat-icon }

    **Light ecModels**

    A smaller, faster-simulating ecModel variant for when full proteome coverage isn't needed.

-   :material-sitemap:{ .gd-feat-icon }

    **RAVEN-based reconstruction**

    Structure expansion and model tuning built on the RAVEN toolbox's reconstruction functions.

-   :material-chart-line:{ .gd-feat-icon }

    **Simulation and analysis**

    Flux analysis and enzyme-usage assessment of the resulting ecModel.

</div>

<hr class="gd-divider">

<p class="gd-section-label">Documentation</p>

<div class="grid cards gd-docs" markdown>

-   :material-book-open-variant:

    **[Protocol](stage0-preparation.md)**

    Six stages from a conventional GEM to a simulated, analyzed ecModel, following the published Nature Protocols pipeline.

-   :material-api:

    **[API reference](api/index.md)**

    Function reference generated from source for both GECKO (MATLAB) and geckopy (Python).

-   :material-download:

    **[Installation](installation.md)**

    Set up GECKO in MATLAB or geckopy in Python, plus the Gurobi/SoPlex solver and Docker for DLKcat.

</div>

---

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

!!! tip "This protocol is GECKO 3.0; the current software has moved on"
    The numbered stages and steps below follow the published Nature
    Protocols pipeline (`protocol.m`) exactly, which describes **GECKO
    3.0**. Development since then has continued on GECKO's `develop4`
    branch — the line this site tracks — heading towards a **GECKO 4.0**
    release, and several of those changes are **already implemented** in
    the current software even though the protocol text hasn't caught up
    yet: the protein pool and enzyme usage reactions now run in the
    forward direction ([PR #419](https://github.com/SysBioChalmers/GECKO/pull/419)),
    kcat prediction can go through the hosted OpenKineticsPredictor service
    instead of a local DLKcat, kcat-list merging now generalizes to any
    number of sources, and a few new analysis functions
    (`getEnzymeBottlenecks`, `pfbaEnzymes`, `relaxProteomicsGreedy`) aren't
    part of the original protocol at all. geckopy, being newer, targets this
    current behavior directly rather than the original GECKO 3.0 protocol.
    Pages below flag each of these with a box like this one, alongside the
    GECKO 3.0 protocol steps they sit next to.

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

!!! note "Tutorial code"
    All code shown in this protocol is also available in `GECKO/tutorials`. The
    full ecModel workflow for *Saccharomyces cerevisiae* is in
    `full_ecModel/protocol.m`, and an example light ecModel of the generic
    human-GEM is in `light_ecModel/protocol.m`. Both tutorials generate models
    that are only suitable for use within the respective tutorials, and may
    require additional curation and evaluation.

## Citing GECKO

This documentation is a structured version of the published protocol:

> Chen, Y., Gustafsson, J., Tafur Rangel, A., Anton, M., Domenzain, I.,
> Kittikunapong, C., Li, F., Yuan, L., Nielsen, J. & Kerkhoven, E. J.
> *Reconstruction, simulation and analysis of enzyme-constrained metabolic
> models using GECKO Toolbox 3.0.* Nature Protocols **19**, 629-667 (2024).
> [https://doi.org/10.1038/s41596-023-00931-7](https://doi.org/10.1038/s41596-023-00931-7)

## Source code

The GECKO toolbox is publicly available under the MIT license at
[https://github.com/SysBioChalmers/GECKO](https://github.com/SysBioChalmers/GECKO)
and archived at [https://doi.org/10.5281/zenodo.7699818](https://doi.org/10.5281/zenodo.7699818).
The Python port, geckopy, is at
[https://github.com/SysBioChalmers/geckopy](https://github.com/SysBioChalmers/geckopy).

<script>
(function () {
  var tabs = document.querySelectorAll('.gd-itab');
  var cmd  = document.getElementById('gd-cmd');
  tabs.forEach(function (btn) {
    btn.addEventListener('click', function () {
      tabs.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      cmd.innerHTML = btn.dataset.cmd;
    });
  });
})();
</script>
