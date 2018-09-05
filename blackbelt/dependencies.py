# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import os
import json
import shutil
import tempfile
import subprocess
import itertools
import operator

import click


__all__ = ['check', 'parse_dep']


# https://github.com/davglass/license-checker#custom-format
LICENSE_CHECKER_FORMAT_KEYS = [
    'name', 'repository', 'dependencyPath', 'url', 'version', 'licenses',
    'licenseText', 'licenseModified', 'licenseFile', 'path',
]

# https://github.com/davglass/license-checker#custom-format
LICENSE_CHECKER_FORMAT = {key: None for key in LICENSE_CHECKER_FORMAT_KEYS}

# Search Oracle wiki for 'Licenses Eligible for Pre-Approval - Distribution'
# List of official license codes: https://spdx.org/licenses/
LICENSES_DISTRIBUTED = [
    'Apache', 'Apache-1.1', 'Apache-2.0', '0BSD', 'BSD', 'BSD-2-Clause',
    'BSD-3-Clause', 'ISC', 'MIT', 'PHP-3.0', 'UPL', 'UPL-1.0', 'ZPL-2.0',
    'Unlicense', 'Python-2.0', 'FreeBSD', 'Apache License, Version 2.0',
]
LICENSES_DISTRIBUTED += [license + '*' for license in LICENSES_DISTRIBUTED]

MISSING_COPYRIGHT_NOTICE_WARNING = '!!! MISSING COPYRIGHT NOTICE !!!'
MISSING_LICENSE_TEXT_WARNING = '!!! MISSING LICENSE !!!'


def check(dep, list_path, licenses_path, dev=False, debug=False):
    """
    Checks the dependency for licenses and vulnerabilities before you can
    add it to the Third-Party Approval Process:

    #. Installs the dependency in a temporary directory
    #. Checks licenses
    #. Checks for ``PATENTS`` files (TODO)
    #. Provides you with:

        - The list of 4th party deps for the Technology Usage Note field
        - The contents of the Public License field
        - List of packages not eligible for Pre-Approval
        - List of known vulnerabilities (TODO)

    Example::

        bb dep check react@16.2

    Requirements:

    - ``npm install -g license-checker``
    - ``npm install -g licensecheck`` (TODO: ``licensecheck --once --dev --tsv``)
    - ``npm install -g nsp`` (TODO: ``nsp check``)
    - ``npm install -g snyk && snyk auth`` (TODO: ``snyk test``)
    """
    ensure_executables(['npm', 'license-checker'])

    dep_name, dep_version = dep
    click.echo('Analyzing the package `{0}{1}` ...'.format(dep_name, '' if dep_version is None else '@' + dep_version))

    if dep_version is None: # check in the supplied project_dir
        project_dir = dep_name
        package_json = os.path.join(project_dir, 'package.json')
        with open(package_json) as f:
            package_data = json.load(f)
        dep_name = package_data['name'];
        licenses = license_checker(project_dir)
        package_tree = get_package_tree(project_dir)
    else:
        # check the supplied npm dep_name@dep_version module by installing it first
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                install(dep_name, dep_version, tmp_dir, dev=dev)
            except Exception as e:
                if debug:
                    raise
                raise click.BadParameter('The npm package could not be installed')
            licenses = license_checker(tmp_dir)
            package_tree = get_package_tree(tmp_dir)

    pre_approval_verdict = get_pre_approval_verdict(licenses)
    details, fourth_party_licenses = separate_top_level_details(licenses, dep_name)

    click.echo('Creating the list of 4th party deps... {}'.format(list_path.name))
    list_path.write(create_deps_list(fourth_party_licenses))
    click.echo('Creating the Public License field contents... {}'.format(licenses_path.name))
    licenses_path.write(create_licenses_list(details, fourth_party_licenses))

    color = 'green' if pre_approval_verdict else 'red'
    click.secho('\n{name}@{version}'.format(**details), bold=True, fg=color)
    click.echo((
        'License: {licenses}\n'
        'Copyright Notice: {copyright_notice}\n'
        'Dependencies: {dependencies}\n'
        'Eligible for Pre-Approval: {pre_approval_verdict}\n\n'
        'Description: {description}\n'
        'Package: https://npmjs.com/package/{name}\n'
        'Repo: {repo}\n'
    ).format(
        licenses=details['licenses'],
        copyright_notice=details['copyright_notice'],
        dependencies=len(fourth_party_licenses),
        pre_approval_verdict=pre_approval_verdict,
        description=details.get('description') or 'N/A',
        name=details['name'],
        repo=details.get('repo') or 'N/A',
    ))

    problematic_licenses = [
        details for details in licenses
        if details['not_pre_approved_reasons']
    ]
    if problematic_licenses:
        heading = '\nProblematic Licenses: {0}'.format(len(problematic_licenses))
        click.secho(heading, bold=True, fg=color)
        missing = False

        for details in problematic_licenses:
            reasons = ', '.join(details['not_pre_approved_reasons'])
            missing = missing or 'missing' in reasons

            line = click.style('{name}@{version} ({licenses})'.format(**details), bold=True)
            click.echo('{0} - {1}'.format(line, reasons))

            if debug:
                click.echo(' ・ npm: https://www.npmjs.com/package/{0}'.format(details['name']))
                if details.get('repo'):
                    click.echo(' ・ repo: {0}'.format(details['repo']))
                if details.get('license_file'):
                    click.echo(' ・ license file: {0}'.format(details['license_file']))

                breadcrumbs = get_package_breadcrumbs(package_tree, details['name'], details['version'])
                if len(breadcrumbs) > 0:
                    for breadcrumb in breadcrumbs:
                        click.echo(' ・ found in dependency path: {}'.format(' > '.join(breadcrumb)))

        if missing:
            click.echo(
                '\nBad luck! Before adding the dependency to the approval '
                'process you need to manually go through the dependencies, '
                'get the missing info and complete the generated files '
                'with it.'
            )
        if not debug:
            click.echo('\nProTip: You can use --debug to print more details.')
    return pre_approval_verdict


def install(dep_name, dep_version, project_dir, dev=False):
    click.echo('Getting dependencies...')
    dep = '{0}@{1}'.format(dep_name, dep_version)

    package_json = os.path.join(project_dir, 'package.json')
    if not os.path.exists(package_json):
        # Create package.json - It is required to be able to run `npm ls`
        with open(package_json, 'w') as fp:
            fp.write('{"name": "black-belt"}')

    run(['npm', 'install', '--save', dep], cwd=project_dir)
    if dev:
        click.echo('Getting dev dependencies...')
        shutil.copy(
            os.path.join(project_dir, 'node_modules', dep_name, 'package.json'),
            os.path.join(project_dir),
        )

        package_json = os.path.join(project_dir, 'package.json')
        with open(package_json) as f:
            package_data = json.load(f)

        package_data_just_deps = {}
        for key, value in package_data.items():
            if 'dependencies' in key.lower():
                package_data_just_deps[key] = value
        with open(package_json, 'w') as f:
            json.dump(package_data_just_deps, f)

        run(['npm', 'install'], cwd=project_dir)


def get_pre_approval_verdict(licenses):
    return all(not details['not_pre_approved_reasons'] for details in licenses)


def create_deps_list(licenses):
    return '\n'.join([
        '{name}@{version} ({licenses})'.format(**details)
        for details in licenses
    ])


# See the internal FAQ and search for following questions:
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

    key_fn = operator.itemgetter('license_text')
    licenses = sorted(fourth_party_licenses, key=key_fn)
    identical_license_groups = itertools.groupby(licenses, key_fn)

    for license_text, details_list in identical_license_groups:
        details_list = list(details_list)
        if len(details_list) == 1:
            section = (
                '{name}@{version} ({licenses})\n'
                '{copyright_notice}\n'
                '{license_text}'
            ).format(**details_list[0])
            sections.append(section)
        else:
            for details in details_list:
                section = (
                    '{name}@{version} ({licenses})\n'
                    '{copyright_notice}'
                ).format(**details)
                sections.append(section)

            section = ''.join([
                '{name}@{version}\n'.format(**details)
                for details in details_list
            ]) + '\n' + license_text
            sections.append(section)

    separator = '\n---------separator---------\n'
    return separator.join(sections) + separator


def separate_top_level_details(licenses, dep_name):
    dep_details = None
    fourth_party_licenses = []

    for details in licenses:
        if details['name'] == dep_name:
            dep_details = details
        else:
            fourth_party_licenses.append(details)

    return (dep_details, fourth_party_licenses)


def license_checker(project_dir):
    format_file = os.path.join(project_dir, 'format.json')
    with open(format_file, 'w') as f:
        json.dump(LICENSE_CHECKER_FORMAT, f)

    args = ['--unknown', '--json', '--customPath', format_file]
    output = run(['license-checker'] + args, cwd=project_dir)

    licenses = []
    for details in json.loads(output).values():
        with open(os.path.join(details['path'], 'package.json')) as f:
            pkg_data = json.load(f)

        copyright_notice, license_text = parse_license_text(details.get('licenseText'))
        license_names = parse_license_names(details.get('licenses'))

        details = {
            'name': details['name'],
            'version': details['version'],
            'description': pkg_data.get('description'),
            'repo': details.get('repository'),
            'license_file': parse_license_filename(details['name'], details.get('licenseFile')),
            'copyright_notice': copyright_notice or create_copyright_notice(pkg_data) or MISSING_COPYRIGHT_NOTICE_WARNING,
            'license_text': license_text or MISSING_LICENSE_TEXT_WARNING,
            'licenses': license_names,
        }
        details['not_pre_approved_reasons'] = check_pre_approval_elligibility(details)

        licenses.append(details)
    return licenses


def get_package_tree(project_dir):
    """
    Returns the "tree" of the package and its dependencies in
    the NPM ls json format.
    """
    output = run(['npm', 'ls', '--json'], cwd=project_dir, check=False)
    return json.loads(output)


def get_package_breadcrumbs(package_tree, name, version):
    """
    Takes a npm ls JSON tree and looks up the paths to the given
    dependency (name and version).

    Returns an array of paths. Where a path is an array of
    dependencies leading to the given dependency in the tree.

        >>> get_package_breadcrumbs(tree, 'minim', '1.0.0')
        [
            ['fury-adapter-swagger@1.0.0'],
            ['fury@2.0.0'],
            ['apielements@0.1.0', 'fury@2.0.0']
        ]
    """

    def traverse_dependencies(dependencies, path):
        """
        Inline function to be called recursively to check for dependency and
        pass down the path to further dependencies.
        """

        results = []

        for dependency_name in dependencies:
            dependency = dependencies[dependency_name]

            if dependency_name == name and dependency.get('version') == version:
                # Found dependency in path
                results.append(path)
                continue

            if 'dependencies' in dependency:
                # Traverse dependency dependencies
                sub_dependencies = dependency['dependencies']
                path_component = '{}@{}'.format(dependency_name, dependency['version'])
                results += traverse_dependencies(sub_dependencies, path + [path_component])

        return results

    return traverse_dependencies(package_tree['dependencies'], [])


def ensure_executables(executables):
    for executable in executables:
        try:
            # check=False, because some programs return non-zero status when
            # they print --version output
            run([executable, '--version'], check=False)
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
def run(args, cwd=None, check=True):
    kwargs = {'cwd': cwd}
    try:
        with open(os.devnull, 'w') as devnull:
            kwargs['stderr'] = devnull
            output = subprocess.check_output(args, **kwargs)
    except subprocess.CalledProcessError as e:
        if check:
            raise
        else:
            return e.stdout.decode().strip()
    else:
        return output.decode().strip()


def parse_license_names(value):
    try:
        return value.lstrip('(').rstrip(')')
    except AttributeError:
        # Someone is using the deprecated 'licenses' field, we got a list.
        # Since we have no idea whether these licenses should be written
        # with OR, AND, ... let's join it by commas.
        #
        # See also https://docs.npmjs.com/files/package.json#license
        return ', '.join(filter(None, value))


def parse_license_text(text):
    license_text = (text or '').strip()
    copyright_notice = detect_copyright_notice(license_text, require_year=True)

    # If the license doesn't contain any of the following words, it's suspicius
    # and should be classified as "rubbish" (sometimes the license-checker picks
    # up a README file without any real license text).
    license_text_lc = license_text.lower()
    if (
        'software' not in license_text_lc and
        'copyright' not in license_text_lc and
        'license' not in license_text_lc
    ):
        return (None, None)

    if 'Apache License' in license_text:
        return (copyright_notice, license_text)

    copyright_notice = detect_copyright_notice(license_text)
    if copyright_notice:
        license_text = text.split(copyright_notice)[1]
        license_text = license_text.strip()
        license_text = re.sub(r' +', ' ', license_text)
        license_text = re.sub(r' ?(\r\n|\n)+ ?', remove_newlines_keep_paragraps, license_text)
    return (copyright_notice, license_text)


def detect_copyright_notice(copyright_text, require_year=False):
    for line in copyright_text.splitlines():
        line = line.strip()
        if re.search(r'copyright|\(c\)|©', line, re.I):
            if not require_year:
                return line
            elif re.search(r'\d{4}', line):
                return line
    return None


def create_copyright_notice(pkg_data):
    author = pkg_data.get('author')
    if not author:
        return None
    try:
        copyright_notice = 'Copyright (c) {name}'.format(name=author['name'])
        if author.get('email'):
            copyright_notice += ' <{email}>'.format(email=author['email'])
        return copyright_notice
    except (KeyError, AttributeError):
        return None


def remove_newlines_keep_paragraps(match):
    newlines = re.findall(r'\r\n|\n', match.group(0))
    if len(newlines) > 1:
        return ''.join(newlines[:2])
    return ' '


def parse_license_filename(dep_name, path):
    if path:
        try:
            return path.split('node_modules')[1].lstrip('/')
        except IndexError:
            return path
    return None


def check_pre_approval_elligibility(details):
    reasons = []
    if not details['licenses'] in LICENSES_DISTRIBUTED:
        reasons.append('license not pre-approved')
    if details['copyright_notice'] == MISSING_COPYRIGHT_NOTICE_WARNING:
        reasons.append('missing copyright notice')
    if details['license_text'] == MISSING_LICENSE_TEXT_WARNING:
        reasons.append('missing full license text')
    return reasons


def parse_dep(dep):
    split_result = re.split(r'==|@', dep)
    if split_result[0] != '':
        try:
            return (split_result[0], split_result[1])
        except IndexError:
            return (split_result[0], 'latest')
    else:
        try:
            return ('@' + split_result[1], split_result[2])
        except IndexError:
            return ('@' + split_result[1], 'latest')
