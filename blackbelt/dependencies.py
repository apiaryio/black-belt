import re
import os
import json
import tempfile
import subprocess
import itertools

import click


__all__ = ['check', 'parse_dep']


# https://github.com/davglass/license-checker#custom-format
LICENSE_CHECKER_FORMAT_KEYS = [
    'name', 'repository', 'dependencyPath', 'url', 'version', 'licenses',
    'licenseText', 'licenseModified', 'licenseFile', 'path',
]

# https://github.com/davglass/license-checker#custom-format
LICENSE_CHECKER_FORMAT = {}
for key in LICENSE_CHECKER_FORMAT_KEYS:
    LICENSE_CHECKER_FORMAT[key] = None

# https://confluence.oraclecorp.com/confluence/display/CORPARCH/Licenses+Eligible+for+Pre-Approval+-+Internal+and+Hosted+Use
# https://confluence.oraclecorp.com/confluence/display/CORPARCH/Licenses+Eligible+for+Pre-Approval+-+Distribution
LICENSES_DISTRIBUTED = [
    'ISC', 'MIT', 'BSD', 'Apache',
    'ISC*', 'MIT*', 'BSD*', 'Apache*'
]


def check(dep, list_path, licenses_path):
    """
    Checks the dependency for licenses and vulnerabilities before you can
    add it to the Third-Party Approval Process:

    #. Installs the dependency in a temporary directory
    #. Checks licenses
    #. Checks for PATENTS files (TODO)
    #. Provides you with:

        - The list of 4th party deps for the Technology Usage Note field
        - The contents of the Public License field
        - List of licenses not eligible for Pre-Approval
        - List of known vulnerabilities (TODO)

    Requirements:

    - npm install -g license-checker
    - npm install -g licensecheck (TODO: licensecheck --once --dev --tsv)
    - npm install -g nsp (TODO: nsp check)
    - npm install -g snyk && snyk auth (TODO: snyk test)
    """
    check_executables(['npm', 'license-checker'])

    click.echo('Analyzing the package...')
    with tempfile.TemporaryDirectory() as tmp_dir:
        run(['npm', 'install', dep], cwd=tmp_dir)
        licenses = license_checker(tmp_dir)

    pre_approval_verdict = get_pre_approval_verdict(licenses)
    details, fourth_party_licenses = separate_top_level_details(licenses, dep)

    click.echo('Creating the list of 4th party deps...')
    list_path.write(create_deps_list(fourth_party_licenses))
    click.echo('Creating the Public License field contents...')
    licenses_path.write(create_licenses_list(details, fourth_party_licenses))

    color = 'green' if pre_approval_verdict else 'red'
    click.secho('\n{name}@{version}'.format(**details), bold=True, fg=color)
    click.echo((
        'License: {licenses}\n'
        'Dependencies: {deps_count}\n'
        'Elligible for Pre-Approval: {pre_approval_verdict}'
    ).format(
        deps_count=len(fourth_party_licenses),
        pre_approval_verdict=pre_approval_verdict,
        **details,
    ))

    problematic_licenses = filter_problematic_licenses(licenses)
    if problematic_licenses:
        click.secho('\nProblematic Dependencies', bold=True, fg=color)
        click.echo(create_deps_list(problematic_licenses))


def get_pre_approval_verdict(licenses):
    return all(
        details['pre_approved'] for details in licenses.values()
    )


def create_deps_list(licenses):
    lines = []
    for dep, details in licenses.items():
        lines.append('{name} {version} ({licenses})'.format(**details))
    return '\n'.join(lines)


# See https://confluence.oraclecorp.com/confluence/display/CORPARCH/Third-Party+Approval+FAQ
# and search for following questions:
#
# - What information is required in the Public License field?
# - What's the best way to format all the information in the Public
#   License field?
# - If there are multiple dependencies licensed under the same terms,
#   do I need to repeat those terms for every dependency?
def create_licenses_list(top_level_details, fourth_party_licenses):
    sections = []

    sections.append(top_level_details['copyright_notice'])
    sections.append(top_level_details['license_text'])

    def key_fn(details):
        return details['license_text']

    licenses = sorted(fourth_party_licenses.values(), key=key_fn)
    identical_license_groups = itertools.groupby(licenses, key_fn)

    for license_text, details_list in identical_license_groups:
        details_list = list(details_list)
        if len(details_list) == 1:
            section = (
                '{name} {version} ({licenses})\n'
                '{copyright_notice}\n'
                '{license_text}'
            ).format(**details_list[0])
            sections.append(section)
        else:
            for details in details_list:
                section = (
                    '{name} {version} ({licenses})\n'
                    '{copyright_notice}'
                ).format(**details)
                sections.append(section)

            section = ''.join([
                '{name} {version}\n'.format(**details)
                for details in details_list
            ]) + '\n' + license_text
            sections.append(section)

    separator = '\n---------separator---------\n'
    return separator.join(sections) + separator


def separate_top_level_details(licenses, top_level_dep):
    top_level_details = None
    fourth_party_licenses = {}

    for dep, details in licenses.items():
        if dep.startswith(top_level_dep):
            top_level_details = details
        else:
            fourth_party_licenses[dep] = details

    return (top_level_details, fourth_party_licenses)


def filter_problematic_licenses(licenses):
    problematic_licenses = {}

    for dep, details in licenses.items():
        if not details['pre_approved']:
            problematic_licenses[dep] = details

    return problematic_licenses


def license_checker(project_dir):
    format_file = os.path.join(project_dir, 'format.json')
    with open(format_file, 'w') as f:
        json.dump(LICENSE_CHECKER_FORMAT, f)

    args = ['--unknown', '--json', '--customPath', format_file]
    output = run(['license-checker'] + args, cwd=project_dir)

    data = {}
    for package, details in json.loads(output).items():
        copyright_notice, license_text = parse_license_text(details.get('licenseText'))
        data[package] = {
            'name': details.get('name'),
            'version': details.get('version'),
            'license_text': license_text,
            'copyright_notice': copyright_notice,
            'licenses': details.get('licenses').lstrip('(').rstrip(')'),
            'pre_approved': details.get('licenses') in LICENSES_DISTRIBUTED,
        }
    return data


def check_executables(executables):
    for executable in executables:
        try:
            # check=False, because some programs return non-zero status when
            # they print --version output
            run([executable, '--version'], check=False, silent=True)
        except FileNotFoundError:
            if executable == 'npm':
                msg = "'npm' is needed, but it's not installed."
                click.echo(msg, err=True)
                raise click.Abort()
            else:
                confirm = (
                    "'{0}' is needed, but it's not installed. "
                    "Install by 'npm install -g {0}'?"
                )
                click.confirm(confirm.format(executable), abort=True)
                run(['npm', 'install', '-g', executable])


# Unfortunately, we cannot use subprocess.run(), because BB still supports Py2
def run(args, silent=False, cwd=None, check=True):
    kwargs = {'cwd': cwd}
    try:
        with open(os.devnull, 'w') as devnull:
            if silent:
                kwargs['stdout'] = devnull
                kwargs['stderr'] = devnull
                return subprocess.check_call(args, **kwargs)
            else:
                kwargs['stderr'] = devnull
                return subprocess.check_output(args, **kwargs)
    except subprocess.CalledProcessError:
        if check:
            raise


def parse_dep(dep):
    split_result = re.split(r'==|@', dep)
    try:
        return (split_result[0], split_result[1])
    except IndexError:
        return (split_result[0], 'latest')


def parse_license_text(text):
    copyright_notice = None
    license_text = None

    for line in (text or '').splitlines():
        if re.search(r'copyright|\(c\)|©', line, re.I):
            copyright_notice = line.strip()
            break

    if copyright_notice:
        license_text = text.split(copyright_notice)[1]
        license_text = license_text.strip()
        license_text = re.sub(r' +', ' ', license_text)
        license_text = re.sub(r' ?(\r\n|\n)+ ?', remove_newlines_keep_paragraps, license_text)

    return (copyright_notice, license_text)


def remove_newlines_keep_paragraps(match):
    newlines = re.findall(r'\r\n|\n', match.group(0))
    if len(newlines) > 1:
        return ''.join(newlines[:2])
    return ' '
