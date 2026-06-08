# Model adapter

The adapter holds the organism-specific parameters and file paths that
drive a reconstruction (taxonomy id, biomass reaction, sigma factor,
database locations, ...). MATLAB: `src/geckomat/model_adapter`. Python:
`geckopy.adapter`.

The main difference: GECKO MATLAB registers a global default adapter via
`ModelAdapterManager`, whereas geckopy has **no global default** — you pass
`adapter=` explicitly or set `model.adapter`, and parameters are validated
with pydantic.

## ModelAdapter

The adapter object itself.

=== "Python · geckopy"

    ::: geckopy.ModelAdapter

=== "MATLAB · GECKO"

    ::: ModelAdapter
        handler: matlab

## ModelParameters (Python)

The pydantic-validated parameter schema carried by a geckopy adapter
(nested `kegg`, `uniprot`, `okp`, ... sections). In MATLAB these are
properties on the adapter `classdef`.

::: geckopy.ModelParameters

## ModelAdapterManager / adapterTemplate (MATLAB)

The default-adapter registry and the adapter template, both MATLAB-only.

::: ModelAdapterManager
    handler: matlab

::: adapterTemplate
    handler: matlab
