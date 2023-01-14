import json
import os
from pathlib import Path

import click

from gitlabci_checker import __version__
from gitlabci_checker.helpers import (
    parse_gitlab_response,
    read_pipeline_config_file,
    send_lint_request,
)


@click.option(
    "-w",
    "--warnings-are-errors",
    type=bool,
    required=False,
    is_flag=True,
    default=False,
    help="Force the failure if warnings are found.",
)
@click.option(
    "-k",
    "--insecure",
    type=bool,
    required=False,
    is_flag=True,
    default=False,
    help="Use insecure connection (http).",
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
    default=os.environ.get("GITLAB_TOKEN", ""),
    help="Your Gitlab access token: by default the content of the GITLAB_TOKEN variable is used.",
)
@click.version_option(__version__, "-v", "--version", message=__version__)
@click.help_option("-h", "--help")
@click.argument("filename", nargs=1, type=click.Path())
@click.command(no_args_is_help=True)
@click.pass_context
def cli(
    ctx: click.Context,
    filename: Path,
    gitlab_server: str,
    token: str,
    warnings_are_errors: bool,
    insecure: bool,
) -> None:
    """Check if your gitlab-ci pipeline compiles correctly."""
    ctx.ensure_object(dict)

    try:
        pipeline_definition = read_pipeline_config_file(filename)
    except OSError:
        click.secho(message=f"{filename} not found.", fg="red", bold=True, nl=True)
        ctx.exit(1)

    lint_endpoint = f"https://{gitlab_server}/api/v4/ci/lint"
    if insecure:
        lint_endpoint = f"http://{gitlab_server}/api/v4/ci/lint"

    response = send_lint_request(lint_endpoint, pipeline_definition, token)

    lint_results, error = parse_gitlab_response(response)

    if not lint_results and not error:
        error_message = (
            "Check failed due to a connection error:\n"
            "make sure you're connected to the internet or the the Gitlab address is correct."
        )
        click.secho(
            message=error_message,
            fg="red",
            bold=True,
            nl=True,
        )
        ctx.exit(1)
    elif error:
        click.secho(
            message="Check failed with the following error:",
            fg="red",
            bold=True,
            nl=True,
        )
        out = json.dumps(error, indent=2)
        click.secho(message=out, fg="red", bold=False, nl=True)
        ctx.exit(1)
    else:
        if (
            lint_results["status"] == "valid"
            and lint_results["warnings"]
            and warnings_are_errors
        ):
            click.secho(
                message="Check failed with warning(s).", fg="yellow", bold=True, nl=True
            )
            out = json.dumps(lint_results, indent=2)
            click.secho(message=out, fg="yellow", bold=False, nl=True)
            ctx.exit(1)
        elif lint_results["status"] == "valid":
            click.secho(message="Everything's fine.", fg="green", bold=True, nl=True)
            ctx.exit(0)
        else:
            click.secho(
                message="Check failed with error(s).", fg="red", bold=True, nl=True
            )
            out = json.dumps(lint_results, indent=2)
            click.secho(message=out, fg="red", bold=False, nl=True)
            ctx.exit(1)
