import click

from blackbelt.deployment import (
    rollback_production
)


@click.group(invoke_without_command=True, help="""
    Rollback latest version from production environments (prod, pre, qa)
    """)
def cli():
    rollback_production()
