import json
from unittest import mock

import pytest

from gitlabci_checker.helpers import (
    parse_gitlab_response,
    read_pipeline_config_file,
    send_lint_request,
)


def test_read_valid_pipeline_config_file():
    read_config = (
        "image: python:latest\n"
        "variables:\n"
        '    PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"\n'
        "test:\n"
        "    script:\n"
        "        - python setup.py test\n"
        "        - pip install tox flake8  # you can also use tox\n"
        "        - tox -e py36,flake8\n"
    )
    mock_open = mock.mock_open(read_data=read_config)
    with mock.patch("builtins.open", mock_open):
        result = read_pipeline_config_file(".gitlab-ci.yaml")

    mock_open.assert_called_once_with(".gitlab-ci.yaml", "r")
    assert result == read_config


def test_read_invalid_pipeline_config_file():
    with pytest.raises(OSError):
        read_pipeline_config_file("no_file")


@mock.patch("requests.post")
def test_send_lint_request(mock_requests):
    class MockResponse(str):
        """Dummy str extension to allow the mock to access the text attribute"""

        def __init__(self, a_string) -> None:
            self.text = a_string

    dummy_gitlab_url = "https://dummy.gitlab.com/api/v4/ci/lint"
    expected_response = {
        "status": "invalid",
        "errors": ["variables config should be a hash of key value pairs"],
        "warnings": [],
    }
    dummy_gitlab_token = "dummy_gitlab_token"
    expected_headers = {
        "Content-Type": "application/json",
        "PRIVATE-TOKEN": dummy_gitlab_token,
    }
    json_string = json.dumps(expected_response)
    mock_requests.return_value = MockResponse(json_string)

    response = send_lint_request(dummy_gitlab_url, "dummy string", dummy_gitlab_token)

    mock_requests.assert_called_once_with(
        dummy_gitlab_url, headers=expected_headers, json={"content": "dummy string"}
    )
    assert response == expected_response


@pytest.mark.parametrize(
    "response,expected",
    [
        ({}, ({}, {})),
        ({"message": "401 Unauthorized"}, ({}, {"message": "401 Unauthorized"})),
        (
            {"status": "valid", "errors": [], "warnings": []},
            ({"status": "valid", "errors": [], "warnings": []}, {}),
        ),
        (
            {
                "status": "valid",
                "errors": [],
                "warnings": [],
                "includes": [],
                "valid": True,
            },
            (
                {
                    "status": "valid",
                    "errors": [],
                    "warnings": [],
                    "includes": [],
                    "valid": True,
                },
                {},
            ),
        ),
    ],
)
def test_parse_gitlab_response(response, expected):
    parsed = parse_gitlab_response(response)
    assert parsed == expected
