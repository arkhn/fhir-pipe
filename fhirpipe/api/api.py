import os
from flask import Flask
from flask_cors import CORS

from fhirpipe import set_global_config, setup_logging
from fhirpipe.api.routes import api, get_pyrog_client


def create_app():
    config_file = os.getenv("CONFIG_PATH", "config.yml")
    print(f"Using config from {config_file}...")
    set_global_config(config_file)
    setup_logging()

    app = Flask(__name__)
    app.register_blueprint(api)

    with app.app_context():
        get_pyrog_client()

    CORS(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=3000, load_dotenv=True)
