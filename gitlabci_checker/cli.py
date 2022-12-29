import click

from gitlabci_checker import __version__


@click.version_option(__version__, "-v", "--version", message=__version__)
@click.help_option("-h", "--help")
@click.command(no_args_is_help=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Check if your gitlab-ci pipeline compiles correctly."""
    pass
