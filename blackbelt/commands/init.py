import os

import click

from blackbelt.configure import configure_blackbelt


@click.group(invoke_without_command=True, help="""Initialize application for usage. Invoke this command first.""")
def cli():
    configure_blackbelt()

