import pytest

from arkhn.config import Config


@pytest.fixture(scope="session", autouse=True)
def config():
    config = Config()
    return config
