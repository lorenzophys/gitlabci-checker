from click.testing import CliRunner

from gitlabci_checker.cli import cli

GITLAB_CI_YAML = ".gitlab-ci.yaml"
DUMMY_FILENAME = "dummy_filename"


def test_cli_file_not_found():
    runner = CliRunner()
    result = runner.invoke(cli, [DUMMY_FILENAME])

    expected_output = f"{DUMMY_FILENAME} not found.\n"

    assert result.exit_code == 1
    assert result.output == expected_output


def test_conection_error(tmp_path, httpserver, dummy_ci_config, httpserver_listen_address):
    ci_config = tmp_path / GITLAB_CI_YAML
    ci_config.write_text(dummy_ci_config)

    headers = {
        "Content-Type": "application/json",
        "PRIVATE-TOKEN": "",
    }

    httpserver.expect_request("/api/v4/ci/lint", headers=headers).respond_with_json({})

    host, port = httpserver_listen_address

    runner = CliRunner()
    result = runner.invoke(cli, [str(ci_config), "-t", "", "-k", "-s", f"{host}:{port}"])

    expected_output = (
        "Check failed due to a connection error:\n"
        "make sure you're connected to the internet or the the Gitlab address is correct.\n"
    )
    print(result.output)

    assert result.exit_code == 1
    assert result.output == expected_output


def test_404_error(tmp_path, httpserver, dummy_ci_config, httpserver_listen_address):

    ci_config = tmp_path / GITLAB_CI_YAML
    ci_config.write_text(dummy_ci_config)

    headers = {
        "Content-Type": "application/json",
        "PRIVATE-TOKEN": "",
    }

    gitlab_response = {"error": "404 Not Found"}
    httpserver.expect_request("/api/v4/ci/lint", headers=headers).respond_with_json(gitlab_response)

    host, port = httpserver_listen_address

    runner = CliRunner()
    result = runner.invoke(cli, [str(ci_config), "-t", "", "-k", "-s", f"{host}:{port}"])

    expected_output = (
        "Check failed with the following error:\n" "{\n" '  "error": "404 Not Found"\n' "}\n"
    )

    assert result.exit_code == 1
    assert result.output == expected_output


def test_bad_pipeline(tmp_path, httpserver, dummy_ci_config, httpserver_listen_address):

    ci_config = tmp_path / GITLAB_CI_YAML
    ci_config.write_text(dummy_ci_config)

    headers = {
        "Content-Type": "application/json",
        "PRIVATE-TOKEN": "",
    }

    gitlab_response = {
        "status": "invalid",
        "errors": ["variables config should be a hash of key value pairs"],
        "warnings": [],
    }

    httpserver.expect_request("/api/v4/ci/lint", headers=headers).respond_with_json(gitlab_response)

    host, port = httpserver_listen_address

    runner = CliRunner()
    result = runner.invoke(cli, [str(ci_config), "-t", "", "-k", "-s", f"{host}:{port}"])

    expected_output = (
        "Check failed with error(s).\n"
        "{\n"
        '  "status": "invalid",\n'
        '  "errors": [\n'
        '    "variables config should be a hash of key value pairs"\n'
        "  ],\n"
        '  "warnings": []\n'
        "}\n"
    )

    assert result.exit_code == 1
    assert result.output == expected_output


def test_valid_pipeline_with_warning(
    tmp_path, httpserver, dummy_ci_config, httpserver_listen_address
):

    ci_config = tmp_path / GITLAB_CI_YAML
    ci_config.write_text(dummy_ci_config)

    headers = {
        "Content-Type": "application/json",
        "PRIVATE-TOKEN": "",
    }

    gitlab_response = {
        "status": "valid",
        "errors": ["this is a warning"],
        "warnings": [],
    }

    httpserver.expect_request("/api/v4/ci/lint", headers=headers).respond_with_json(gitlab_response)

    host, port = httpserver_listen_address

    runner = CliRunner()
    result = runner.invoke(cli, [str(ci_config), "-t", "", "-k", "-s", f"{host}:{port}"])

    expected_output = "Everything's fine.\n"

    assert result.exit_code == 0
    assert result.output == expected_output


def test_valid_pipeline(tmp_path, httpserver, dummy_ci_config, httpserver_listen_address):

    ci_config = tmp_path / GITLAB_CI_YAML
    ci_config.write_text(dummy_ci_config)

    headers = {
        "Content-Type": "application/json",
        "PRIVATE-TOKEN": "",
    }

    gitlab_response = {"status": "valid", "errors": [], "warnings": []}

    httpserver.expect_request("/api/v4/ci/lint", headers=headers).respond_with_json(gitlab_response)

    host, port = httpserver_listen_address

    runner = CliRunner()
    result = runner.invoke(cli, [str(ci_config), "-t", "", "-k", "-s", f"{host}:{port}"])

    expected_output = "Everything's fine.\n"

    assert result.exit_code == 0
    assert result.output == expected_output


def test_valid_pipeline_but_warnings_are_errors(
    tmp_path, httpserver, dummy_ci_config, httpserver_listen_address
):

    ci_config = tmp_path / GITLAB_CI_YAML
    ci_config.write_text(dummy_ci_config)

    headers = {
        "Content-Type": "application/json",
        "PRIVATE-TOKEN": "",
    }

    gitlab_response = {
        "status": "valid",
        "errors": [],
        "warnings": ["this is a warning"],
    }

    httpserver.expect_request("/api/v4/ci/lint", headers=headers).respond_with_json(gitlab_response)

    host, port = httpserver_listen_address

    runner = CliRunner()
    result = runner.invoke(cli, [str(ci_config), "-t", "", "-k", "-w", "-s", f"{host}:{port}"])

    expected_output = (
        "Check failed with warning(s).\n"
        "{\n"
        '  "status": "valid",\n'
        '  "errors": [],\n'
        '  "warnings": [\n'
        '    "this is a warning"\n'
        "  ]\n"
        "}\n"
    )

    assert result.exit_code == 1
    assert result.output == expected_output
