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
