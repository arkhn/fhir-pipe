from flask import Blueprint, request, jsonify

from fhirpipe.errors import OperationOutcome
from fhirpipe.run import run as fp_run
from fhirpipe.run import preview as fp_preview
from fhirpipe.extract.graphql import get_credentials, get_resource_from_id
from fhirpipe.extract.sql import get_connection
from flask_cors import CORS


api = Blueprint("api", __name__)
# Enable CORS from all origins '*'.
CORS(api)

default_params = {
    "mapping": None,
    "source": None,
    "resources": None,
    "labels": None,
    "reset_store": False,
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
    credentials = None
    connection_type = None

    if "credentialId" in body:
        try:
            credentials, connection_type = transform_credentials(
                get_credentials(body["credentialId"])
            )
        except OperationOutcome as e:
            raise OperationOutcome(f"Error while fetching credientials for DB: {e}.")
    else:
        raise OperationOutcome("credentialId is required to run fhirpipe.")

    try:
        # Connect to DB and run
        with get_connection(credentials, connection_type=connection_type) as connection:
            fp_run(connection, **params)
    except Exception as e:
        # If something went wrong
        raise OperationOutcome(e)

    return jsonify(success=True)


@api.route("/preview", methods=["GET"])
def preview():
    resource_id = request.args.get("resourceId")
    primary_key_value = request.args.get("primaryKeyValue")

    resource_mapping = get_resource_from_id(resource_id)

    # Get credentials if given in request
    credentials = None
    connection_type = None

    if not resource_mapping["source"]["credential"]:
        raise OperationOutcome("credentialId is required to run fhirpipe.")

    credentials, connection_type = transform_credentials(resource_mapping["source"]["credential"])

    try:
        # Connect to DB and run
        with get_connection(credentials, connection_type=connection_type) as connection:
            fhir_object = fp_preview(connection, resource_id, [primary_key_value])
    except Exception as e:
        # If something went wrong
        raise OperationOutcome(e)

    return jsonify(fhir_object)


@api.errorhandler(OperationOutcome)
def handle_bad_request(e):
    return str(e), 400


def transform_credentials(credentials):
    """ The structure expected is not exactly the same as the one
    provided by the graphql query. """
    connection_type = credentials["model"].lower()
    # The structure expected is not exactly the same as the one
    # provided by the graphql query
    credentials = {
        "host": credentials["host"],
        "port": credentials["port"],
        "database": credentials["database"],
        "user": credentials["login"],
        "password": credentials["password"],
    }
    return credentials, connection_type
