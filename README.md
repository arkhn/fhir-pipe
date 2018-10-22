[![Website arkhn.org](https://img.shields.io/website-up-down-green-red/https/arkhn.org.svg)](http://arkhn.org/)

# FHIR Pipe: a smart standardization pipeline

Fhir-pipe helps extracting data from SQL database and mapping it into the standardized health format [FHIR](https://www.hl7.org/fhir/), using given mapping rules.

The link to a presentation will be made available soon to illustrate Arkhn's approach to standardization.

## Mapping rules

The mapping rules are made of `yml` files. To each FHIR Resource (e.g. `Patient`) corresponds a `yml` file, and each attribute of the ressource (for example `patient.firstname`) has a mapping instruction which details which `DATABASE/TABLE/COLUMN` to select and which processing scripts to apply. The scripts are available in [arkhn/scripts](https://github.com/arkhn/fhir-pipe/tree/master/arkhn/scripts).

The mapping rules for a specific usecase are available in the repo `fhir-mapping`, and the general structure of the format is in the repo `fhir-store`.

## Goal of `fhir-pipe`

Be able to parse a mapping rule, connect to SQL databases, and populate FHIR-compliant objects using these databases and the processing rules given.

## How to start

We have reported several issues with the label `Good first issue` which can be a good way to start! Also of course, feel free to contact us on Slack in you have trouble with the project.

If you're enthusiastic about our project, :star: it to show your support! :heart:

* * *

## License

[Apache License 2.0](https://github.com/OpenMined/PySyft/blob/master/LICENSE)
