import configparser
import os
from pathlib import Path

import click

from gitlabci_checker import __version__
from gitlabci_checker.helpers import (
    parse_url,
    read_pipeline_config_file,
    send_lint_request,
)


@click.version_option(__version__, "-v", "--version", message=__version__)
@click.help_option("-h", "--help")
@click.argument("filename", nargs=1, type=click.Path())
@click.command(no_args_is_help=True)
@click.pass_context
def cli(ctx: click.Context, filename: Path) -> None:
    """Check if your gitlab-ci pipeline compiles correctly."""

    config = configparser.ConfigParser()
    try:
        config.read(".git/config")
    except KeyError:
        click.echo("This is not a git repository.")

    origin_url = config['remote "origin"'].get("url")
    gitlab_hostname = parse_url(origin_url)

    pipeline_definition = read_pipeline_config_file(filename)

    lint_endpoint = f"https://{gitlab_hostname}/api/v4/ci/lint"

    response = send_lint_request(
        lint_endpoint, pipeline_definition, os.environ.get("GITLAB_ACCESS_TOKEN", "")
    )
    click.echo(response)
