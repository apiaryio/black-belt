from paver.easy import *
from paver.setuputils import setup

options = environment.options

VERSION = '0.4.1'

setup(
    name='blackbelt',
    version=VERSION,
    description='Project automation the Apiary way',
    long_description="""Internal so far""",
    author='Lukas Linhart',
    author_email='lukas@apiary.io',
    url='http://github.com/apiaryio/black-belt',
    license='MIT',
    packages=['blackbelt'],
    install_requires=['requests', 'trello', 'PyGithub'],
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
        install_requires=[],
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
