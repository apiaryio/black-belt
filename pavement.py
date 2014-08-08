from paver.easy import *
from paver.setuputils import setup

options = environment.options

from blackbelt.version import VERSION

NAME = 'blackbelt'
requires = ['click', 'requests', 'trello', 'PyGithub']


setup(
    name=NAME,
    version=VERSION,
    description='Project automation the Apiary way',
    long_description="""Internal so far""",
    author='Lukas Linhart',
    author_email='lukas@apiary.io',
    url='http://github.com/apiaryio/black-belt',
    license='MIT',
    packages=[NAME, NAME+'.apis', NAME+'.commands'],
    install_requires=requires,
    tests_require=['nose', 'virtualenv'],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Environment :: Console",
        "Topic :: Documentation",
        "Topic :: Utilities",
        "Topic :: Software Development :: Build Tools",
    ]
)

if paver.setuputils.has_setuptools:
    old_sdist = "setuptools.command.sdist"
    options.setup.update(dict(
        install_requires=requires,
        test_suite='nose.collector',
        zip_safe=False,
        entry_points="""
[console_scripts]
bb = blackbelt.tasks:main
"""
    ))
else:
    old_sdist = "distutils.command.sdist"
    options.setup.scripts = ['distutils_scripts/bb']

options.setup.package_data = paver.setuputils.find_package_data("blackbelt", package="blackbelt",
                                                only_in_packages=False)


@task
@consume_args
def bump(args):
    version = map(int, VERSION.split('.')[0:3])

    if len(args) > 0 and args[0] == 'major':
        version[1] += 1
    else:
        version[2] += 1

    version = map(str, version)

    module_content = "VERSION='%s'\n" % '.'.join(version)

    # bump version in blackbelt
    with open(path('blackbelt/version.py'), 'w') as f:
        f.write(module_content)

    # bump version in sphinx
    conf = []
    with open(path('docs/source/conf.py'), 'r') as f:
        for line in f.readlines():
            if line.startswith('version = '):
                line = "version = '%s'\n" % '.'.join(version[0:2])
            elif line.startswith('release = '):
                line = "release = '%s'\n" % '.'.join(version[0:3])

            conf.append(line)

    with open(path('docs/source/conf.py'), 'w') as f:
        f.writelines(conf)


@task
def release():
    sh("git tag -s '%(name)s-%(version)s' -m 'Version bump to %(version)s'" % {'name': NAME, 'version': VERSION})
    sh("git push --tags")
    sh("python setup.py register sdist upload")
