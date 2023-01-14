import pytest


@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("localhost", 8888)


@pytest.fixture(scope="session")
def dummy_ci_config():
    return (
        "image: python:latest\n"
        "variables:\n"
        '    PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"\n'
        "test:\n"
        "    script:\n"
        "        - python setup.py test\n"
        "        - pip install tox flake8  # you can also use tox\n"
        "        - tox -e py36,flake8\n"
    )
