from flask import Blueprint, request, jsonify

from fhirpipe.errors import OperationOutcome
from fhirpipe.run import run as fp_run
from fhirpipe.extract.graphql import get_credentials
from fhirpipe.extract.sql import get_connection


api = Blueprint("api", __name__)

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
            credentials = get_credentials(body["credentialId"])
            connection_type = credentials["model"].lower()
            # The structure expected is not exatly the same as the one provided by graphql query
            credentials = {
                "host": credentials["host"],
                "port": credentials["port"],
                "database": credentials["database"],
                "user": credentials["login"],
                "password": credentials["password"],
            }
        except OperationOutcome as e:
            raise ValueError(f"Error while fetching credientials for DB: {e}.")
    else:
        raise Exception("credentialId is required to run fhirpipe.")

    try:
        # Connect to DB and run
        with get_connection(credentials, connection_type=connection_type) as connection:
            fp_run(connection, **params)
    except Exception as e:
        # If something went wrong
        # TODO is it the right way to send back error message?
        return jsonify({"errors": str(e)})

    return jsonify(success=True)
