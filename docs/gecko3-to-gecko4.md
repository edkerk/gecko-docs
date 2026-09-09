# GECKO 3 → GECKO 4

GECKO 4 continues development on the `develop4` branch, the line this site
tracks, and introduces changes that are not backward-compatible with
GECKO 3.0, the version described in the published Nature Protocols pipeline
(see [Citations](references.md)). Review the changes below before upgrading
an existing GECKO 3 workflow, or stay on GECKO 3 using the instructions at
the bottom of this page.

:::{admonition} If you read nothing else: the protein reaction direction flipped
:class: important

[PR #419](https://github.com/SysBioChalmers/GECKO/pull/419) reversed the
direction of the protein pool and enzyme usage reactions: they now run
**forward** instead of **reverse**. A script written against GECKO 3 that
reads or sets bounds on `prot_pool_exchange` or `usage_prot_*` reactions
keeps running under GECKO 4 without raising an error, but returns a
different, still plausible-looking result, because the sign convention on
those bounds changed. Every other change on this page either raises an
error or adds new, opt-in behavior; this is the one that can pass silently.
:::

## Additive and backward-compatible changes

These extend GECKO 4 without changing existing behavior, so an unmodified
GECKO 3 script keeps producing the same result:

- kcat prediction can go through the hosted OpenKineticsPredictor service,
  in addition to a local DLKcat installation.
- kcat-list merging generalizes to any number of sources, rather than a
  fixed DLKcat/fuzzy-matching pair.
- Three analysis functions are new and were not part of the GECKO 3.0
  protocol: `getEnzymeBottlenecks`, `pfbaEnzymes`, `relaxProteomicsGreedy`.

This page is updated as GECKO 4 development continues; it does not yet
cover every change. The [Guide](guide/index.md) pages flag GECKO-4-specific
behavior alongside the GECKO 3.0 protocol steps they sit next to.

## Staying on GECKO 3

If your workflow depends on GECKO 3 behavior, install the latest GECKO 3
release, v3.2.5, instead of GECKO 4:

::::{tab-set}
:::{tab-item} MATLAB (git)

```bash
git clone https://github.com/SysBioChalmers/GECKO
cd GECKO
git checkout v3.2.5
```

Then, in MATLAB, run `GECKOInstaller.install` as usual.
:::
:::{tab-item} MATLAB (ZIP)

Download the v3.2.5 archive from the
[GitHub releases page](https://github.com/SysBioChalmers/GECKO/releases/tag/v3.2.5)
instead of the latest release, extract it, then run
`GECKOInstaller.install` as usual.
:::
:::{tab-item} MATLAB (Add-On)

The MATLAB Add-On manager only distributes the latest GECKO release, so it
cannot install v3.2.5 directly. Uninstall the Add-On
(`GECKOInstaller.uninstall`, or remove it through the Add-On manager), then
install v3.2.5 via git or ZIP instead (see the tabs above).
:::
::::

See [Installation](installation/index.md) for the full installation
instructions.

## Earlier versions: GECKO 1 and 2

GECKO 3's refactor makes it largely incompatible with the two releases
before it, GECKO 1 ([Sánchez et al., 2017](references.md#gecko-1)) and
GECKO 2 ([Domenzain et al., 2022](references.md#gecko-2)). The two older
releases share the same underlying ecModel structure with each other, and
differ from GECKO 3 (and GECKO 4) in the same ways:

- GECKO 1 and 2 have no `ec` structure: enzyme and kcat information lives
  scattered across several model fields, rather than collected in one place
  the way `ecModel.ec` (Python: `ec_model.ec`) does from GECKO 3 onward.
- Enzymes enter the S-matrix as `1/kcat`, with the molecular weight handled
  separately in the protein exchange reactions, rather than the combined
  `MW/kcat` coefficient GECKO 3 introduced (see [Building an empty
  ecModel](guide/building-ec-model.md)).
- Neither stores an ecModel in a YAML format that retains full model
  content the way GECKO 3's does.

The practical consequence: functions from GECKO 3 or 4 do not work on a
GECKO 1 or 2 ecModel, and functions from GECKO 1 or 2 do not work on a
GECKO 3 or 4 ecModel. geckopy has no support for GECKO 1/2-formatted
ecModels; it targets GECKO 4 only.

GECKO 2's last release, 2.0.3, is still available on the [GitHub releases
page](https://github.com/SysBioChalmers/GECKO/releases/tag/v2.0.3), and the
[`gecko2` branch](https://github.com/SysBioChalmers/GECKO/tree/gecko2)
remains for anyone who needs to apply a fix to it. GECKO 1 predates this
repository's branch history; its release is cited in
[Citations](references.md#gecko-1) for anyone who needs to reference it.
