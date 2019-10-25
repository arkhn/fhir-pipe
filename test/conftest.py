import pytest

from fhirpipe import set_global_config
from fhirpipe.config import Config


@pytest.fixture(scope="session", autouse=True)
def config():
    config = Config()
    set_global_config(config)
    return config
