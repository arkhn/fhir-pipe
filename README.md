[![GitHub license](https://img.shields.io/github/license/arkhn/fhir-pipe.svg)](https://github.com/arkhn/fhir-pipe/blob/master/LICENSE)
[![Website arkhn.org](https://img.shields.io/website-up-down-green-red/https/arkhn.org.svg)](http://arkhn.org/)


# FHIR pipeline: a smart ETL to standardize health data

Fhir-pipe helps extracting data from SQL databases and converting it to the standardized health format [FHIR](https://www.hl7.org/fhir/), using given mapping rules provided by the [pyrog project](https://github.com/arkhn).


## Mapping rules

The mapping rules are provided through the **pyrog** graphql API. To each FHIR Resource (e.g. `Patient`) corresponds a rule file, and each attribute of the ressource (for example `patient.name.firstname`) has a mapping instruction which details which `DATABASE/TABLE/COLUMN` to select and which processing scripts to apply, as the data might need to be cleaned. A non-exhaustive list of scripts is available in [arkhn/scripts](https://github.com/arkhn/cleaning-scripts).

## Goal of `fhirpipe`

fhirpipe is an ETL which is agnostic of the type of input SQL databases. It should be able to parse mapping rules, connect to arbitrary SQL databases, and populate processed FHIR objects using these databases and the processing rules given.

## Get started

[Read our guide](https://github.com/arkhn/fhir-pipe/blob/master/GET_STARTED.md) to start standardizing health data! 

## Contribute

We have reported several issues with the label `Good first issue` which can be a good way to start! You can also join our [Slack](https://join.slack.com/t/arkhn/shared_invite/enQtNTc1NDE5MDIxMDU3LWZmMzUwYWIwN2U0NGI1ZjM2MjcwNTAyZDZhNzcyMWFiYjJhNTIxNWQ1MWY4YmRiM2VhMDY4MDkzNGU5MTQ4ZWM) to contact us if you have trouble or questions :)

If you're enthusiastic about our project, :star: it to show your support! :heart:

* * *

## License

[Apache License 2.0](https://github.com/OpenMined/PySyft/blob/master/LICENSE)
