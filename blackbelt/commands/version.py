import click

from blackbelt.version import (
    get_version
)


@click.group(invoke_without_command=True, help='Version')
def cli():
  print get_version()
