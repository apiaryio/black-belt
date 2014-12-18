import os

import click

from blackbelt.configure import configure_blackbelt


@click.group(invoke_without_command=True, help="""Deploy to staging""")
def cli():
    configure_blackbelt()

