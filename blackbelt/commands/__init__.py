# This seems to be strangely needed by click.
# FIXME: You don't really need to __init__ noise there

import click


@click.group()
def cli():
    pass
