from flask import request

from fhirpipe.cli.run import run as fp_run
from fhirpipe.api import app


@app.route("/run", methods=["POST"])
def run():
    config = request.args.get("config", default="config.yml")
    mapping = request.args.get("mapping", default=None)
    source = request.args.get("source", default=None)
    resources = request.args.get("resources", default=None)
    reset_store = request.args.get("reset_store", default=False)
    chunksize = request.args.get("chunksize", default=None)
    multiprocessing = request.args.get("multiprocessing", default=False)

    fp_run(
        config_path=config,
        mapping_file=mapping,
        source_name=source,
        resources=resources,
        reset_store=reset_store,
        chunksize=chunksize,
        multiprocessing=multiprocessing,
    )
