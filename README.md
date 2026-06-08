# GECKO Toolbox 3.0 Protocol Documentation

This repository contains a documentation version of the protocol:

> Chen, Y., Gustafsson, J., Tafur Rangel, A. et al. *Reconstruction, simulation
> and analysis of enzyme-constrained metabolic models using GECKO Toolbox 3.0.*
> Nature Protocols 19, 629-667 (2024).
> https://doi.org/10.1038/s41596-023-00931-7

The content has been reorganized into a set of Markdown pages suitable for
hosting on [Read the Docs](https://readthedocs.org/) with
[MkDocs](https://www.mkdocs.org/) and the
[Material theme](https://squidfunk.github.io/mkdocs-material/).

Alongside the protocol narrative, the site includes an auto-generated
**API reference** that documents the MATLAB (GECKO) and Python (geckopy)
implementations side by side, extracted directly from each toolbox's source
(pulled in as git submodules). See
[API reference (MATLAB + Python)](#api-reference-matlab--python) below.

## Repository layout

```
gecko-protocol/
├── .readthedocs.yaml          # Read the Docs build configuration (incl. submodules)
├── .gitmodules                # GECKO + geckopy submodule definitions
├── mkdocs.yml                 # MkDocs site configuration and navigation
├── requirements.txt           # Python build dependencies
├── README.md                  # This file
├── GECKO/                     # submodule: SysBioChalmers/GECKO    (MATLAB source)
├── geckopy/                   # submodule: SysBioChalmers/geckopy  (Python source)
└── docs/
    ├── index.md               # Landing page
    ├── introduction.md        # Background, framework, applications, limitations
    ├── installation.md        # Materials, software and equipment setup
    ├── stage0-preparation.md  # Stage 0: project files and data
    ├── stage1-structure-expansion.md
    ├── stage2-kcat-integration.md
    ├── stage3-model-tuning.md
    ├── stage4-proteomics.md
    ├── stage5-simulation-analysis.md
    ├── troubleshooting.md
    ├── anticipated-results.md
    ├── references.md
    └── api/                   # auto-generated bilingual API reference
        ├── index.md           # overview + MATLAB <-> Python mapping
        ├── build.md
        ├── gather-kcats.md
        ├── enzyme-data.md
        ├── kcat-sensitivity.md
        ├── limit-proteins.md
        ├── simulation-utilities.md
        └── adapter.md
```

## Building locally

```bash
# from the repository root
git submodule update --init --recursive   # fetch the GECKO + geckopy sources
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
mkdocs serve
```

The `git submodule update --init` step is required: without it the `GECKO/`
and `geckopy/` source trees are empty and the API reference fails to build.

Then open http://127.0.0.1:8000 in your browser. The site rebuilds
automatically as you edit the Markdown files.

To produce a static build:

```bash
mkdocs build        # output written to ./site
```

## Hosting on Read the Docs

1. Push this folder to a GitHub, GitLab or Bitbucket repository.
2. Sign in at https://readthedocs.org/ and import the repository.
3. Read the Docs detects `.readthedocs.yaml` and builds the site
   automatically on every push.

Read the Docs initializes the git submodules automatically because
`.readthedocs.yaml` sets `submodules.include: all`, so the API reference is
built on every push without any extra configuration.

## API reference (MATLAB + Python)

The `docs/api/` pages document both toolboxes side by side using
[mkdocstrings](https://mkdocstrings.github.io/) with its Python and MATLAB
handlers. Each function is shown in a tabbed block — the Python docstring and
the MATLAB help text are extracted live from the source. The sources are git
submodules pinned to each project's `main` branch:

- `GECKO/`   — [SysBioChalmers/GECKO](https://github.com/SysBioChalmers/GECKO) (MATLAB)
- `geckopy/` — [SysBioChalmers/geckopy](https://github.com/SysBioChalmers/geckopy) (Python)

Neither toolbox needs to be installed to build the docs: the Python handler
reads the source statically (via griffe) and the MATLAB handler parses it with
tree-sitter (no MATLAB runtime required).

To refresh the reference against the latest upstream code:

```bash
git submodule update --remote --recursive
git add GECKO geckopy
git commit -m "docs: bump GECKO and geckopy submodules"
```

## License and attribution

The GECKO source code is released under the MIT license at
https://github.com/SysBioChalmers/GECKO. The scientific content summarized in
these pages is the work of the original authors; please cite the Nature
Protocols article above when using this protocol.
