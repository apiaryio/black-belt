import re
from subprocess import check_output


"""
I wrap functionality for interacting with the local git instance.

I rely on git being available in PATH, and I rely on standard command line
interface.

When reporting bugs, please do be rigorous in saying what shell, pty/tty you've
used and please provide all environment variables as well as locale settings.
"""


def get_github_repo():
    return check_output(['git', 'config', '--get', 'remote.origin.url']).strip()


def get_remote_repo_info(github_repo_info):
    match = re.match(r".*github.com(:|\/)(?P<owner>[a-zA-Z\_\-]+)/{1}(?P<name>[a-zA-Z\-\_]+)\.git$", github_repo_info)
    if not match:
        raise ValueError("Cannot parse repo info. Bad remote?")
    return match.groupdict()


def get_current_branch():
    return check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()


def get_current_sha():
    return check_output(['git', 'rev-parse', 'HEAD']).strip()


def merge(sha, message):
    """ Merge given SHA into the master and return merge commit SHA """

    if get_current_branch() != 'master':
        check_output(['git', 'checkout', 'master'])

    check_output(['git', 'pull'])

    check_output(['git', 'merge', sha, '-m', message])

    check_output(['git', 'push', 'origin', 'master'])

    return get_current_sha()
