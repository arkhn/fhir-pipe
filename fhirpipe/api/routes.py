from flask import Blueprint, request, jsonify

from fhirpipe.errors import OperationOutcome
from fhirpipe.run import run as fp_run
from fhirpipe.run import preview as fp_preview
from fhirpipe.extract.graphql import get_credentials, get_resource_from_id
from flask_cors import CORS


api = Blueprint("api", __name__)
# Enable CORS from all origins '*'.
CORS(api)

default_params = {
    "mapping": None,
    "resource_ids": None,
    "override": False,
    "chunksize": None,
    "bypass_validation": False,
    "skip_ref_binding": False,
    "multiprocessing": False,
}


@api.route("/run", methods=["POST"])
def run():
    body = request.get_json()

    # Get credentials if given in request
    if "credentialId" not in body:
        raise OperationOutcome("credentialId is required to run fhirpipe.")

    credential_id = body.pop("credentialId")
    try:
        credentials = get_credentials(credential_id)
    except OperationOutcome as e:
        raise OperationOutcome(f"Error while fetching credientials for DB: {e}.")

    # Merge body with default_params to get parameters to use
    params = {**default_params, **body}

    try:
        # Connect to DB and run
        fp_run(**params, credentials=credentials)
    except Exception as e:
        # If something went wrong
        raise OperationOutcome(e)

    return jsonify(success=True)


@api.route("/preview/<resource_id>/<primary_key_value>", methods=["GET"])
def preview(resource_id, primary_key_value):
    resource_mapping = get_resource_from_id(resource_id)

    # Get credentials if given in request
    if not resource_mapping["source"]["credential"]:
        raise OperationOutcome("credentialId is required to run fhirpipe.")

    credentials = resource_mapping["source"]["credential"]

    try:
        # Connect to DB and run
        fhir_objects, errors = fp_preview(resource_id, [primary_key_value], credentials)
    except Exception as e:
        # If something went wrong
        raise OperationOutcome(e)

    return jsonify({"preview": fhir_objects[0], "errors": errors})


@api.errorhandler(OperationOutcome)
def handle_bad_request(e):
    return str(e), 400
