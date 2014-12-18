import click

from blackbelt.deployment import (
    deploy_staging
)


@click.group(invoke_without_command=True, help="""
    Deploy current branch to staging
    """)
def cli():
    deploy_staging()
