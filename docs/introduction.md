# Introduction

## Background

The use of genome-scale models is a valuable approach to mathematically explore
metabolism, and has accelerated biotechnology, biomedicine and fundamental
biology studies. A conventional genome-scale metabolic model (GEM) is
reconstructed from all metabolic reactions of the organism of interest and
converted into a computational format. The model is based on a system of
equations whose variables are reaction rates, represented in a stoichiometric
matrix (S-matrix) that contains the stoichiometric coefficients of metabolites
in reactions.

The system can be solved by constraint-based methods, which impose constraints
on reaction rates and search for solutions within an allowable solution space
where all possible metabolic states reside. Integrating more constraints into
the model shrinks the solution space and can further improve the predictive
power of the model.

While the most widely used constraints come from condition-dependent
measurements such as nutrient uptake rates, constraints on the catalytic
capacity of enzymes have recently gained attention. Several methods integrate
such constraints into conventional models, including metabolism and
expression models, resource balance analysis, expression and thermodynamics
flux, pcModel, flux balance analysis with molecular crowding, MOMENT, GECKO,
sMOMENT and ECMpy. Among these, GECKO has been widely adopted to build
enzyme-constrained models (ecModels) by expanding conventional GEMs for various
organisms. This protocol presents GECKO version 3.0.

GECKO can in principle convert not only genome-scale models but also
smaller-size metabolic models to ecModels. This protocol focuses on GEMs.

## The GECKO framework

GECKO enables direct conversion of a conventional GEM into an
enzyme-constrained version. The conversion is based on the relation:

$$ v \le k_{cat} \times e $$

where $v$ is the rate of the enzymatic reaction, $k_{cat}$ is the turnover
number of the enzyme that catalyzes the reaction, and $e$ is the concentration
of the enzyme. The minimum usage of the enzyme for the reaction is therefore
the rate $v$ over $k_{cat}$, and the mass usage is the rate $v$ times the
molecular weight (MW) of the enzyme over $k_{cat}$.

Accordingly, each enzyme is included as a pseudo-substrate in the reaction that
it catalyzes, and the model captures both the turnover number and the MW of the
enzyme.

### Enzyme usage reactions

Enzyme usage reactions are added to the model. In the absence of any proteomic
data, all protein masses are drawn from a total protein pool. If quantitative
data are available for any enzyme, this knowledge can be used to explicitly
constrain the reactions catalyzed by that enzyme, and the measured enzyme mass
is subsequently subtracted from the protein pool.

In GECKO versions 1 and 2, $k_{cat}$ and MW were included as separate
coefficients in metabolic and enzyme usage reactions. In version 3 they are
combined to form a single stoichiometric coefficient:

$$ -\frac{MW}{k_{cat}} $$

This conversion reduces the chance that the program predicts extremely low
fluxes in enzyme usage reactions, which could otherwise fall below the numeric
tolerance of some linear programming solvers and cause numerical issues. This
form links to the concept of protein cost, which quantitatively reflects the
protein mass required per unit flux of an enzymatic reaction. Compared with a
conventional GEM, the S-matrix is expanded and the model can predict enzyme
usage in addition to reaction rates.

## GECKO light

GECKO 3.0 offers an option to reconstruct a light ecModel, with a formalism
similar to other frameworks: the protein cost of the enzyme is included
directly in the metabolic reaction while separate enzyme usage reactions are
excluded.

- Light ecModels have a much shorter calculation time than the full version and
  are therefore more practical for large-scale model reconstruction and
  analysis, for example for cell lines.
- Light ecModels are incapable of proteomics integration and individual enzyme
  usage prediction, because they do not include enzyme usage reactions.
- When only a total proteome constraint is used, light ecModels give results
  comparable to full ecModels.

## DLKcat for predicted kcat values

Because $k_{cat}$ values dominate model performance, their availability and
accuracy are critical. Measured $k_{cat}$ values can be gathered from public
databases such as BRENDA, but coverage is far from complete, especially for
lesser studied organisms. This partly explains why ecModels have historically
been reconstructed for relatively few organisms.

To address this, the deep learning-based model DLKcat predicts $k_{cat}$ values
for given enzyme-substrate pairs. Predicted $k_{cat}$ values have been shown to
drastically improve ecModel reconstruction across 343 yeast and fungi species.
GECKO can run DLKcat to provide predicted $k_{cat}$ values as an alternative
source, which in principle allows assigning $k_{cat}$ values to all enzymatic
reactions and turning any conventional GEM into an ecModel.

## Applications of GECKO

GECKO is mainly used to convert a conventional GEM into an ecModel by including
enzyme constraints, which considerably reduces the solution space and the flux
variability ranges in simulations. This reduction can lead to accurate
predictions of phenotypes such as overflow metabolism and batch growth of
microbes, which conventional GEMs cannot capture unless specific enzymatic,
transport or exchange reactions (such as oxygen uptake) are constrained.

The reconstructed ecModels also enable calculation and comparison of parameters
such as pathway protein costs and flux control coefficients, and can guide and
interpret metabolic engineering strategies for overproduction of metabolites.

Any constraint-based method that fits a conventional GEM can also be applied to
an ecModel, because GECKO only expands the S-matrix with additional
pseudo-metabolites and pseudo-reactions while retaining linearity. This includes
flux balance analysis (FBA), flux variability analysis (FVA), flux scanning
based on enforced objective flux, and task-driven integrative network inference
for tissues (tINIT) for context-specific reconstruction.

## Comparison with other methods

Enzyme constraints can also be incorporated by alternative methods such as
sMOMENT and ECMpy, with similar applications.

- **sMOMENT** adds a protein pool pseudo-metabolite into metabolic reactions and
  an exchange reaction for it, so the resulting model is similar to the GECKO
  light ecModel. sMOMENT is Python-based and cannot construct a full ecModel.
- **ECMpy** avoids adding enzymes into reactions and constrains the protein pool
  outside the S-matrix, giving a smaller model. A limitation is that the enzyme
  constraints cannot be directly considered by constraint-based simulations that
  were developed for conventional GEMs.

GECKO differs from these methods in its capability for proteomics data
prediction and integration, and in its potential to explore links between
metabolism and other processes such as signaling. The ecModel structures defined
by GECKO are similar to conventional GEMs, so virtually any analysis developed
for conventional GEMs can be applied. By incorporating deep learning-predicted
enzyme kinetics, GECKO 3.0 considerably improves parameter coverage, which is
currently the major obstacle for other methods.

## Limitations

- ecModels are much larger than the starting GEMs, so the computational cost of
  large-scale simulations is substantially higher. GECKO 3.0 addresses this with
  light ecModels, where consideration of individual enzyme levels is disabled.
  There is therefore a trade-off between proteomics integration or individual
  enzyme-level prediction and computational speed.
- Reducing the solution space improves predictions but can also lead to larger
  deviations from experimental observations because of uncertainties in the
  applied constraints. One source of uncertainty is the $k_{cat}$ values, which
  come from measurements or DLKcat predictions and may be inaccurate, especially
  for enzyme complexes. Almost all sources reflect in vitro kinetics, which may
  differ from in vivo conditions. GECKO provides strategies to test the ecModel
  against known phenotype data and to suggest which constraints to modify, so
  experimental data are necessary for high-quality reconstruction.
- Even with enzyme constraints, ecModels cannot predict all phenotypes because
  of missing constraints. For example, metabolic fluxes can be influenced by
  allosteric regulation and posttranslational modifications, and integrating
  these processes could further reduce the solution space and increase
  prediction accuracy.

## Overview of the procedure

The starting material for Stage 1 is a conventional GEM that will be converted
to the ecModel format. At the end of Stage 1 most of the variable fields are
empty and are populated in Stage 2.

Before Stage 2, the enzyme data need to be assembled and well organized,
including molecular weights, protein sequences and EC numbers. These can
normally be collated from organism-specific entries in the UniProt database.
The KEGG database can be an alternative source for EC numbers.

The stages produce a sequence of models:

1. **Empty ecModel** (Stage 1): the structure is expanded so enzyme constraints
   can be implemented, but no constraints are applied yet.
2. **Draft ecModel** (Stage 2): enzyme $k_{cat}$ values are integrated,
   introducing enzymatic constraints.
3. **Functional ecModel** (Stage 3): model parameters are tuned with
   physiological data.
4. **Proteome-constrained ecModel** (Stage 4): proteomics data, if available,
   are integrated.

All of these stages also apply to light ecModels, except Stage 4.
