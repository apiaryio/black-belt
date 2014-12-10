from click.core import Command
from click.decorators import _make_command


def command(name=None, cls=None, **attributes):
    if cls is None:
        cls = Command

    def decorator(function):
        cmd = _make_command(function, name, attributes, cls)
        cmd.__doc__ = function.__doc__
        return cmd
    return decorator
