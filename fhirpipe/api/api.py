from flask import Flask
from flask_cors import CORS

from fhirpipe import set_global_config, setup_logging
from fhirpipe.api.routes import api


def create_app():
    set_global_config("config.yml")
    setup_logging()

    app = Flask(__name__)
    app.register_blueprint(api)

    CORS(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=3000, load_dotenv=True)
