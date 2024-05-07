import socket

import pytest


@pytest.fixture(scope="session")
def httpserver_listen_address():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 0))
        address = s.getsockname()
        return address


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
