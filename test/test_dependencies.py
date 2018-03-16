from nose.tools import assert_equal

from blackbelt.dependencies import (
    parse_dep,
    parse_license_text,
)


class TestDependencyNameParsing(object):

    def test_no_version(self):
        assert_equal(parse_dep('react'), ('react', 'latest'))

    def test_at_separator(self):
        assert_equal(parse_dep('react@16.2'), ('react', '16.2'))

    def test_equals_separator(self):
        assert_equal(parse_dep('react==16.2'), ('react', '16.2'))


class TestLicenseTextParsing(object):

    def test_basic(self):
        assert_equal(parse_license_text('''
            Copyright 2009-2014 Contributors. All rights reserved.

            Permission is hereby granted,
            free of charge...

            ...paragraph
        '''), (
            'Copyright 2009-2014 Contributors. All rights reserved.',
            'Permission is hereby granted, free of charge...\n\n...paragraph',
        ))

    def test_heading(self):
        assert_equal(parse_license_text('''
            MIT License

            Copyright (c) 2013-present, Facebook, Inc.

            Permission is hereby granted,
            free of charge...

            ...paragraph
        '''), (
            'Copyright (c) 2013-present, Facebook, Inc.',
            'Permission is hereby granted, free of charge...\n\n...paragraph',
        ))

    def test_rubbish(self):
        assert_equal(parse_license_text('''
            # Black Belt

            Black belt is collection of scripts, tools and guidelines used for developing projects The Apiary Way.

            ## Installation & Usage

            Please refer to [The Black Belt Documentation](http://black-belt.readthedocs.org/).
        '''), (
            None,
            None,
        ))

    def test_apache(self):
        apache = '''
                                Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

            TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

            1. Definitions.

                "License" shall mean the terms and conditions for use, reproduction,
                and distribution as defined by Sections 1 through 9 of this document.

                "Licensor" shall mean the copyright owner or entity authorized by
                the copyright owner that is granting the License.

                ...
                "Source" form shall mean the preferred form for making modifications,
                ...
        '''
        assert_equal(parse_license_text(apache), (None, apache.strip()))

    def test_empty(self):
        assert_equal(parse_license_text(''), (
            None,
            None,
        ))

    def test_none(self):
        assert_equal(parse_license_text(None), (
            None,
            None,
        ))
