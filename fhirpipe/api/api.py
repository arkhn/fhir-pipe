import os
from flask import Flask

from fhirpipe import set_global_config, setup_logging
from fhirpipe.api.routes import api


def create_app():
    app = Flask(__name__)
    app.register_blueprint(api)

    config_file = os.getenv("CONFIG_PATH", "config.yml")
    print(f"Using config from {config_file}...")
    set_global_config(config_file)
    setup_logging()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", load_dotenv=True)
