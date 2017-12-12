import os

import click

from blackbelt.dependencies import check as do_check, run, parse_dep


@click.group(help='Dependency management')
def cli():
    pass


def validate_dep(ctx, param, dep):
    try:
        dep_name, dep_version = parse_dep(dep)
    except Exception:
        raise click.BadParameter('The dependency format should be e.g. react@16.2')
    else:
        if dep_version == 'latest':
            dep_version = run(['npm', 'view', dep_name, 'version'])
        return (dep_name, dep_version)


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
    do_check(*args, **kwargs)
