import configparser
import os
from pathlib import Path

import click

from gitlabci_checker import __version__
from gitlabci_checker.helpers import (
    parse_gitlab_response,
    parse_url,
    read_pipeline_config_file,
    send_lint_request,
)


@click.version_option(__version__, "-v", "--version", message=__version__)
@click.help_option("-h", "--help")
@click.option(
    "-g",
    "--git-config",
    type=bool,
    required=False,
    is_flag=True,
    default=False,
    help="Let the url in 'remote \"origin\"' in .git/config decide the gitlab server.",
)
@click.option(
    "-s",
    "--gitlab-server",
    type=str,
    required=True,
    default="gitlab.com",
    help="The Gitlab server hostname.",
)
@click.option(
    "-t",
    "--token",
    type=str,
    required=True,
    default=os.environ.get("GITLAB_ACCESS_TOKEN", ""),
    help="Your Gitlab access token: by default the content of GITLAB_TOKEN is used.",
)
@click.argument("filename", nargs=1, type=click.Path())
@click.command(no_args_is_help=True)
@click.pass_context
def cli(
    ctx: click.Context,
    filename: Path,
    git_config: bool,
    gitlab_server: str,
    token: str,
) -> None:
    """Check if your gitlab-ci pipeline compiles correctly."""
    ctx.ensure_object(dict)

    if git_config:
        config = configparser.ConfigParser()
        try:
            config.read(".git/config")
        except KeyError:
            click.echo("This is not a git repository.")
            ctx.exit(1)

        origin_url = config['remote "origin"'].get("url")
        gitlab_server = parse_url(origin_url)

    try:
        pipeline_definition = read_pipeline_config_file(filename)
    except OSError:
        click.echo(f"{filename} not found.")
        ctx.exit(1)

    lint_endpoint = f"https://{gitlab_server}/api/v4/ci/lint"

    response = send_lint_request(lint_endpoint, pipeline_definition, token)

    lint_results, error = parse_gitlab_response(response)
    
    if error:
        click.echo(error)
    else: 
        click.echo(lint_results)
