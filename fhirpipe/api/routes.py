from flask import Blueprint, request, jsonify, g

from fhirpipe.errors import OperationOutcome
from fhirpipe.run import run as fp_run
from fhirpipe.run import preview as fp_preview
from fhirpipe.extract.graphql import PyrogClient
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


def get_pyrog_client():
    if "pyrog_client" not in g:
        g.pyrog_client = PyrogClient()
    return g.pyrog_client


@api.route("/run", methods=["POST"])
def run():
    body = request.get_json()

    # Get credentials if given in request
    if "credentialId" not in body:
        raise OperationOutcome("credentialId is required to run fhirpipe.")

    credential_id = body.pop("credentialId")
    try:
        credentials = get_pyrog_client().get_credentials(credential_id)
    except OperationOutcome as e:
        raise OperationOutcome(f"Error while fetching credientials for DB: {e}.")

    # Merge body with default_params to get parameters to use
    params = {**default_params, **body}

    try:
        # Connect to DB and run
        fp_run(**params, credentials=credentials, pyrog_client=get_pyrog_client())
    except Exception as e:
        # If something went wrong
        raise OperationOutcome(e)

    return jsonify(success=True)


@api.route("/preview/<resource_id>/<primary_key_value>", methods=["GET"])
def preview(resource_id, primary_key_value):
    resource_mapping = get_pyrog_client().get_resource_from_id(resource_id)

    # Get credentials if given in request
    if not resource_mapping["source"]["credential"]:
        raise OperationOutcome("credentialId is required to run fhirpipe.")

    credentials = resource_mapping["source"]["credential"]

    try:
        # Connect to DB and run
        fhir_objects, errors = fp_preview(
            resource_id, [primary_key_value], credentials, pyrog_client=get_pyrog_client()
        )
    except Exception as e:
        # If something went wrong
        raise OperationOutcome(e)

    return jsonify({"preview": fhir_objects[0], "errors": errors})


@api.errorhandler(OperationOutcome)
def handle_bad_request(e):
    return str(e), 400
