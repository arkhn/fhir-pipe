# Fhir-pipe: a smart standardization pipeline

Fhir-pipe helps extracting data from SQL database and mapping it into the standardized health format [FHIR](https://www.hl7.org/fhir/), using given mapping rules.

The link to a presentation will be made available soon to illustrate Arkhn's approach to standardization.

## Mapping rules

The mapping rules are made of `yml` files. To each FHIR Ressource (e.g. `Patient`) corresponds a `yml` file, and each attribute of the ressource (for example `patient.firstname`) has a mapping instruction which details which `DATABASE/TABLE/COLUMN` to select and which processing scripts to apply. The scripts are available in [arkhn/scripts](https://github.com/arkhn/fhir-pipe/tree/master/arkhn/scripts).

The mapping rules for a specific usecase will be made available soon.

## Mapping automation

As of now, the rules are generated manually. This a repetitive and slow process, which can benefit easily from some kinds of automatisation:

* A clustering algorithm on SQL columns that labels groups of columns (e.g. all adresses, phones, etc) so that the user can search by "type" of columns instead of browsing the whole database.
* A web interface that generates automatically the `yml` file from the instructions given by the user, and which leverages the suggestions made by the clustering algorithm.

