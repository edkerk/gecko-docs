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

## Repository layout

```
gecko-docs/
├── .readthedocs.yaml          # Read the Docs build configuration
├── mkdocs.yml                 # MkDocs site configuration and navigation
├── requirements.txt           # Python build dependencies
├── README.md                  # This file
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
    └── references.md
```

## Building locally

```bash
# from inside the gecko-docs folder
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
mkdocs serve
```

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

If your repository root is not the `gecko-docs` folder, move the contents of
`gecko-docs/` to the repository root, or update the `mkdocs.configuration`
path in `.readthedocs.yaml` accordingly.

## License and attribution

The GECKO source code is released under the MIT license at
https://github.com/SysBioChalmers/GECKO. The scientific content summarized in
these pages is the work of the original authors; please cite the Nature
Protocols article above when using this protocol.
