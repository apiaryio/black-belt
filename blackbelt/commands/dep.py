import os

import click

from blackbelt.dependencies import check as do_check, parse_dep


@click.group(help='Dependency management')
def cli():
    pass


def validate_dep(ctx, param, dep):
    try:
        package_name, package_version = parse_dep(dep)
    except Exception:
        raise click.BadParameter('The dependency format should be e.g. react@16.2')
    else:
        if package_version == 'latest':
            raise click.BadParameter('Dependency must have a version number, e.g. react@16.2')
        return '{0}@{1}'.format(package_name, package_version)


@cli.command()
@click.argument('dep', callback=validate_dep)
@click.option('--dev/--no-dev', default=False,
              help='Whether to include dev dependencies.')
@click.option('--list-path', type=click.File(mode='w'),
              default=lambda: os.path.join(os.getcwd(), 'list.txt'),
              help='Where to save the list of 4th party deps.')
@click.option('--licenses-path', type=click.File(mode='w'),
              default=lambda: os.path.join(os.getcwd(), 'licenses.txt'),
              help='Where to save the Public License field contents.')
def check(*args, **kwargs):
    do_check(*args, **kwargs)
