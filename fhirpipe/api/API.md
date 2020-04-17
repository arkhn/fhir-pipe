# FHIRPIPE API


## Run

Runs the ETL with on resources for which the ids are given and loads the created objects in the Mongo database.

### Request

`POST /run`

### Body parameters

The route expects the following parameters, taking these ones as default is not provided.

```
{
    "mapping": None,
    "resource_ids": None,
    "override": False,
    "chunksize": None,
    "bypass_validation": False,
    "skip_ref_binding": False,
    "multiprocessing": False,
    "credentialId"
}
```
`credentialId` has no default value and is required.

These are the arguments taken by the `run()` function of fhirpipe.

### Response

This route only return a success response if no error occurred in the process.

### Errors

Throws an `OperationOutcome` error with the error message if any error occurred while running fhirpipe or if credentials where not provided for the source DB in Pyrog.

This `OperationOutcome` error returns a response with status code 400 and data containing the error as a string.

## Preview

Returns a fhir object generated by fhirpipe for a single row of the source database. The arguments are the id of the resource in Pyrog's database and the primary key value of the row to transform. 

### Request

`POST /preview/<resource_id>/<primary_key_value>`

### Response

The response contains the fhir object asked for and potential validation errors associated to this object.

```
{
  preview: <fhir-object>, errors: [<validation-errors>]
}
```

### Errors

Throws an `OperationOutcome` error with the error message if any error occurred while running fhirpipe or if credentials where not provided for the source DB in Pyrog. 

This `OperationOutcome` error returns a response with status code 400 and data containing the error as a string.