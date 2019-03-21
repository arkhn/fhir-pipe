import pytest

from fhirpipe.config import Config


@pytest.fixture(scope="session", autouse=True)
def config():
    config = Config()
    return config
