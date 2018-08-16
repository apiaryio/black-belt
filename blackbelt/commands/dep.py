import os
import sys

import click
import requests

from blackbelt.dependencies import check as do_check, parse_dep


@click.group(help='Dependency management')
def cli():
    pass


def validate_dep(ctx, param, dep):
    try:
        if dep == '.': # check the current project_dir
            return (dep, '*')
        return parse_dep(dep)
    except Exception:
        raise click.BadParameter('The dependency format should be e.g. react@16.2')


@cli.command()
@click.argument('dep', callback=validate_dep)
@click.option('--dev/--no-dev', default=False,
              help='Whether to include dev dependencies.')
@click.option('--debug/--no-debug', default=False,
              help='Print debug information.')
@click.option('--list-path', type=click.File(mode='w'),
              default=lambda: os.path.join(os.getcwd(), 'list.txt'),
              help='Where to save the list of 4th party deps.')
@click.option('--licenses-path', type=click.File(mode='w'),
              default=lambda: os.path.join(os.getcwd(), 'licenses.txt'),
              help='Where to save the Public License field contents.')
def check(*args, **kwargs):
    if not do_check(*args, **kwargs):
        sys.exit(1)
