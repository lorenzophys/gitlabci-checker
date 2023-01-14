import json
from pathlib import Path
from typing import Tuple

import requests


def read_pipeline_config_file(gitlabci_yaml: Path) -> str:
    """Read the .gitlab-ci.yaml configuration file.

    Args:
        gitlabci_yaml (Path): The file that contains the pipeline configuration

    Returns:
        str: The stringified version of the yaml file
    """
    with open(gitlabci_yaml, "r") as f:
        pipeline_definition = f.read()
    return pipeline_definition


def send_lint_request(gitlab_server: str, gitlab_ci: str, gitlab_token: str) -> dict:
    """Send the request to the CI lint endpoint.

    Args:
        gitlab_server (str): The complete address of the endpoint to use.
        gitlab_ci (str): The stringified version of the yaml configuration.
        gitlab_token (str): The token to interact with Gitlab API.

    Returns:
        dict: The response of the requerst to the Gitlab server.
    """
    headers = {
        "Content-Type": "application/json",
        "PRIVATE-TOKEN": gitlab_token,
    }
    data = {"content": gitlab_ci}

    try:
        response = requests.post(gitlab_server, headers=headers, json=data)
    except requests.ConnectionError:
        return {}

    return json.loads(response.text)


def parse_gitlab_response(gitlab_response: dict) -> Tuple[dict, dict]:
    """Parse the Gitlab response and separate the actual content from the errors.

    Args:
        gitlab_response (dict): The response of the requerst to the Gitlab server.

    Returns:
        Tuple[dict, dict]: A pair consisting of the error message and the actual response.
    """
    if all(key in gitlab_response for key in ("status", "errors", "warnings")):
        return gitlab_response, {}
    return {}, gitlab_response
