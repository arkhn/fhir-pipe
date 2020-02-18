from flask import Blueprint, request, jsonify

from fhirpipe.errors import OperationOutcome
from fhirpipe.run import run as fp_run
from fhirpipe.extract.graphql import get_credentials
from fhirpipe.extract.sql import get_connection
from flask_cors import CORS


api = Blueprint("api", __name__)
# Enable CORS from all origins '*'.
CORS(api)

default_params = {
    "mapping": None,
    "sources": None,
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

    if "credential_id" in body:
        try:
            credentials = get_credentials(body["credential_id"])
            connection_type = credentials["model"].lower()
        except OperationOutcome as e:
            raise ValueError(f"Error while fetching credientials for DB: {e}.")
    else:
        raise Exception("credential_id is required to run fhirpipe.")

    # Connect to DB and run
    with get_connection(credentials, connection_type=connection_type) as connection:
        fp_run(connection, **params)

    return jsonify(success=True)
