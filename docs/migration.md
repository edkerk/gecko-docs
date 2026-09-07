# Upgrading from GECKO 3

GECKO 4 continues development on the `develop4` branch — the line this site
tracks — and introduces changes that are not backward-compatible with GECKO
3.0, the version described in the published Nature Protocols pipeline (see
[Citing GECKO](index.md#citing-gecko)). If you have an existing GECKO 3
workflow, review the changes below before upgrading, or stay on GECKO 3 using
the instructions at the bottom of this page.

## What changed

- The protein pool and enzyme usage reactions now run in the forward
  direction ([PR #419](https://github.com/SysBioChalmers/GECKO/pull/419)),
  rather than the reverse direction used in GECKO 3.0.
- kcat prediction can go through the hosted OpenKineticsPredictor service, in
  addition to a local DLKcat installation.
- kcat-list merging generalizes to any number of sources, rather than a fixed
  DLKcat/fuzzy-matching pair.
- A few analysis functions are new and were not part of the GECKO 3.0
  protocol: `getEnzymeBottlenecks`, `pfbaEnzymes`, `relaxProteomicsGreedy`.

This page is updated as GECKO 4 development continues; it does not yet cover
every change. The [Procedure](stage0-preparation.md) pages flag
GECKO-4-specific behavior alongside the GECKO 3.0 protocol steps they sit
next to.

## Staying on GECKO 3

If your workflow depends on GECKO 3 behavior, install the latest GECKO 3
release, v3.2.5, instead of GECKO 4:

=== "MATLAB (git)"

    ```bash
    git clone https://github.com/SysBioChalmers/GECKO
    cd GECKO
    git checkout v3.2.5
    ```

    Then, in MATLAB, run `GECKOInstaller.install` as usual.

=== "MATLAB (ZIP)"

    Download the v3.2.5 archive from the
    [GitHub releases page](https://github.com/SysBioChalmers/GECKO/releases/tag/v3.2.5)
    instead of the latest release, extract it, then run
    `GECKOInstaller.install` as usual.

=== "MATLAB (Add-On)"

    The MATLAB Add-On manager only distributes the latest GECKO release, so
    it cannot install v3.2.5 directly. Uninstall the Add-On
    (`GECKOInstaller.uninstall`, or remove it through the Add-On manager),
    then install v3.2.5 via git or ZIP instead (see the tabs above).

See [Materials and installation](installation.md) for the full installation
instructions.
