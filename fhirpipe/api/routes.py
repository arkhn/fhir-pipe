from flask import Blueprint, request, jsonify

import logging

from fhirpipe.errors import OperationOutcome
from fhirpipe.cli.run import run as fp_run
from fhirpipe.extract.graphql import get_credentials
from fhirpipe.extract.sql import get_connection


api = Blueprint("api", __name__)


@api.route("/run", methods=["POST"])
def run():
    default_params = {
        "mapping": None,
        "source": None,
        "resources": None,
        "reset_store": False,
        "chunksize": None,
        "bypass_validation": False,
        "multiprocessing": False,
    }

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
            logging.warning(
                f"Error while fetching credientials for DB: {e}. "
                "Will try to connect with default credentials provided in the config file."
            )

    # Connect to DB and run
    with get_connection(credentials, connection_type=connection_type) as connection:
        fp_run(connection, **params)

    return jsonify(success=True)
