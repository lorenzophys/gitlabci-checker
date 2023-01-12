import json
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests


def read_pipeline_config_file(gitlabci_yaml: Path) -> str:
    with open(gitlabci_yaml, "r") as f:
        pipeline_definition = f.read()
    return pipeline_definition


def parse_url(origin_url: str) -> Optional[str]:
    if "http" not in origin_url and "ssh://" not in origin_url:
        origin_url = f"ssh://{origin_url}"
    return urlparse(origin_url).hostname


def send_lint_request(gitlab_server: str, gitlab_ci: str, gitlab_token: str) -> dict:
    headers = {
        "Content-Type": "application/json",
        "PRIVATE-TOKEN": gitlab_token,
    }
    data = {"content": gitlab_ci}
    response = requests.post(gitlab_server, headers=headers, json=data)
    print(response.text)
    return json.loads(response.text)
