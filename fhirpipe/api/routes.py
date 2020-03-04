from flask import Blueprint, request, jsonify

from fhirpipe.errors import OperationOutcome
from fhirpipe.run import run as fp_run
from fhirpipe.run import preview as fp_preview
from fhirpipe.extract.graphql import get_credentials, get_resource_from_id
from fhirpipe.extract.sql import get_engine
from flask_cors import CORS


api = Blueprint("api", __name__)
# Enable CORS from all origins '*'.
CORS(api)

default_params = {
    "mapping": None,
    "source": None,
    "resources": None,
    "labels": None,
    "override": False,
    "chunksize": None,
    "bypass_validation": False,
    "multiprocessing": False,
}


@api.route("/run", methods=["POST"])
def run():
    body = request.get_json()

    # Merge body with default_params to get parameters to use
    params = {k: body[k] if k in body else default_params[k] for k in default_params}

    # Get credentials if given in request
    if "credentialId" not in body:
        raise OperationOutcome("credentialId is required to run fhirpipe.")

    try:
        credentials = get_credentials(body["credentialId"])
    except OperationOutcome as e:
        raise OperationOutcome(f"Error while fetching credientials for DB: {e}.")

    try:
        # Connect to DB and run
        engine = get_engine(credentials)
        fp_run(engine, **params)
    except Exception as e:
        # If something went wrong
        raise OperationOutcome(e)

    return jsonify(success=True)


@api.route("/preview/<resource_id>/<primary_key_value>", methods=["GET"])
def preview(resource_id, primary_key_value):
    resource_mapping = get_resource_from_id(resource_id)

    # Get credentials if given in request
    credentials = None

    if not resource_mapping["source"]["credential"]:
        raise OperationOutcome("credentialId is required to run fhirpipe.")

    credentials = resource_mapping["source"]["credential"]

    try:
        # Connect to DB and run
        engine = get_engine(credentials)
        fhir_object = fp_preview(engine, resource_id, [primary_key_value])
    except Exception as e:
        # If something went wrong
        raise OperationOutcome(e)

    return jsonify(fhir_object)


@api.errorhandler(OperationOutcome)
def handle_bad_request(e):
    return str(e), 400
