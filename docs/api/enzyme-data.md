# Enzyme & EC data

Annotating the model with EC numbers, enzyme molecular weights, and the
underlying databases (UniProt, KEGG, BRENDA, Complex Portal). MATLAB:
`src/geckomat/get_enzyme_data`. Python: `geckopy.get_enzyme_data` and
`geckopy.databases`.

## fill_eccodes_from_database / getECfromDatabase

Fill EC numbers for genes/reactions from UniProt (with a KEGG fall-back
in geckopy).

=== "Python · geckopy"

    ::: geckopy.fill_eccodes_from_database

=== "MATLAB · GECKO"

    ::: getECfromDatabase
        handler: matlab

## fill_eccodes_from_gem / getECfromGEM

Use the EC numbers already annotated in the conventional GEM.

=== "Python · geckopy"

    ::: geckopy.fill_eccodes_from_gem

=== "MATLAB · GECKO"

    ::: getECfromGEM
        handler: matlab

## find_ec_in_db / findECInDB

Look up EC numbers for proteins in the loaded database.

=== "Python · geckopy"

    ::: geckopy.find_ec_in_db

=== "MATLAB · GECKO"

    ::: findECInDB
        handler: matlab

## copy_ec_to_gem / copyECtoGEM

Copy EC-number annotations from the ecModel back onto the conventional
GEM.

=== "Python · geckopy"

    ::: geckopy.copy_ec_to_gem

=== "MATLAB · GECKO"

    ::: copyECtoGEM
        handler: matlab

## calculate_mw / calculateMW

Compute enzyme molecular weights from protein sequences.

=== "Python · geckopy"

    ::: geckopy.calculate_mw

=== "MATLAB · GECKO"

    ::: calculateMW
        handler: matlab

## load_brenda_data / loadBRENDAdata

Load the BRENDA kcat / specific-activity / molecular-weight tables.

=== "Python · geckopy"

    ::: geckopy.load_brenda_data

=== "MATLAB · GECKO"

    ::: loadBRENDAdata
        handler: matlab

## Database loaders

geckopy exposes a typed loader per data source. In MATLAB these are bundled
behind `loadDatabases`.

=== "Python · geckopy"

    ::: geckopy.load_uniprot_tsv

    ::: geckopy.load_phyl_dist

    ::: geckopy.load_pax_db

    ::: geckopy.load_complex_portal_json

    ::: geckopy.load_dlkcat_ignore_lists

=== "MATLAB · GECKO"

    ::: loadDatabases
        handler: matlab
