import click

from blackbelt.deployment import (
    deploy_production
)


@click.group(invoke_without_command=True, help="""
    Deploy master to production
    """)
def cli():
    deploy_production()
