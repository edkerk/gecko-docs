# Troubleshooting

This page collects the troubleshooting guidance for specific steps, plus the
overall timing of the protocol.

## Troubleshooting table

### Step 9: Warnings when the conventional GEM is loaded

**Possible reason.** Not all GEMs in SBML format strictly adhere to the L3V1
FBCv2 standard. Run the SBML Validator for more information on what is wrong.

**Solution.** In many cases the model still loads. However, when exported again
to SBML, RAVEN attempts to avoid writing the same invalid file. It can be useful
to run a cycle of `importModel`, `exportModel` and `importModel` to make the
loaded GEM as close to valid SBML as possible.

### Step 12: Complex data is missing for some or all complexes

**Possible reason.** Complex Portal does not contain all complexes; in most
cases some complexes will be missing.

**Solution.** Complex information is not critical for GECKO; uncertainties in
$k_{cat}$ values are a larger problem than uncertainties in complex
stoichiometry. A reasonable option is to skip Step 12 and keep the default
stoichiometry of one for all subunits. It is also possible to manually
complement `ComplexPortal.json` with complex information collected from databases
or the literature.

### Step 17: Difficulties finding EC numbers for the reactions

**Possible reason.** Fuzzy matching requires EC numbers to be matched to
reactions.

**Solution.** EC numbers can be entered manually in the `model.eccodes` field,
based on any species-specific information you have, and loaded with
`getECfromGEM`. Because DLKcat does not require EC numbers, an alternative
strategy is to use only DLKcat as the $k_{cat}$ source.

### Step 24: DLKcat fails to run

**Possible reason.** Difficulty or insufficient rights to install Docker
Desktop.

**Solution.** The `src/dlkcat-gecko/` folder contains all required Python
scripts and data to run DLKcat with the `DLKcat.tsv` output from
`writeDLKcatInput`. Instead of using Docker, install all DLKcat requirements
directly in the system terminal (not MATLAB):

```bash
pipenv install -r requirements.txt
```

After this, run DLKcat from the system terminal:

```bash
pipenv run python DLKcat.py DLKcat.tsv DLKcatOutput.tsv
```

### Step 28: Many entries in noMatch after applyCustomKcats

**Possible reason.** The $k_{cat}$ values in `customKcats.tsv` are possibly
combined with enzyme annotations that do not match the reactions in the model.

**Solution.** Confirm in the ecModel which enzymes are associated with a
particular reaction.

### Step 32: Values to define the total protein pool are missing

**Possible reason.** The protein pool is defined from f, $P_{tot}$ and sigma.

**Solution.** The values can all be assigned a standard value of 0.5. If the
maximum growth rate is too small or large, modify the sigma parameter manually
until a reasonable maximum growth rate is reached.

### Step 43: Many kcat values are changed during tuning

**Possible reason.** Various parameters might not be correctly set.

**Solution.** It is expected that some $k_{cat}$ values need changing (typically
about 20 to 40). If a large fraction are changed, something else is likely
happening. Check the following:

- Ensure there are no constraints set on any nutrient uptake; only the protein
  pool should be limiting.
- Confirm that the maximum growth rate specified in the model adapter as
  `obj.params.gR_exp` is realistic.
- Test whether the starting GEM can simulate the intended growth rate, to check
  whether the metabolic network stoichiometry is limiting.

### Step 54: No access to absolute quantitative proteomics data

**Possible reason.** Proteomics measurements were not performed with external
standards for quantification.

**Solution.** Protein quantification through label-free mass spectrometry is a
powerful alternative that does not require expensive external standards or
stable isotope labeling. Such data has routinely been used with GECKO analyses.

### Step 64: The flexEnz structure contains many entries

**Possible reason.** Lower-quality proteomics data substantially increase the
risk of overconstraining the model.

**Solution.** Constraining individual enzyme levels substantially reduces the
solution space. Confirm that the total protein amount is still realistic and
that low-quality protein concentrations are filtered out. The filtering in
`loadProtData` can be adjusted via various parameters. Being stricter on which
concentrations are included (for example with a lower `maxRSD`, the relative
standard deviation) ensures that only the highest-certainty enzyme levels are
directly constrained, while the others continue to be constrained by the overall
protein pool.

## Timing

The timing of the entire protocol depends on the size of the starting GEM and
the internet connection.

| Stage | Steps | Timing | Notes |
|-------|-------|--------|-------|
| Stage 0 | 1-7 | 15 min | |
| Stage 1 | 8-14 | 15 min | |
| Stage 2 | 15-32 | 1 h | DLKcat deep learning prediction accounts for most of the time |
| Stage 3 | 33-52 | 15 min | |
| Stage 4 | 53-65 | 15 min | Step 64 accounts for most of the time |
| Stage 5 | 66-79 | 3 h | Step 74 accounts for most of the time |
