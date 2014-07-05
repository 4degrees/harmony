# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
import re

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    '''Pytest command.'''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        '''Import pytest and run.'''
        import pytest
        errno = pytest.main(self.test_args)
        raise SystemExit(errno)


with open(os.path.join(
    os.path.dirname(__file__), 'source', 'harmony', '_version.py'
)) as _version_file:
    _version = re.match(
        r'.*__version__ = \'(.*?)\'', _version_file.read(), re.DOTALL
    ).group(1)


setup(
    name='Harmony',
    version=_version,
    description='Asset management schema framework.',
    long_description=open('README.rst').read(),
    keywords='asset management, schema',
    url='https://github.com/4degrees/harmony',
    author='Martin Pengelly-Phillips',
    author_email='martin@4degrees.ltd.uk',
    license='Apache License (2.0)',
    packages=[
        'harmony',
    ],
    package_dir={
        '': 'source'
    },
    install_requires=[
        'jsonschema >= 2.3.0, < 3',
        'jsonpointer >= 1.3, < 2',
        'PySide >= 1.1.1, < 2',
        'Riffle >= 0.1.0, <2'
    ],
    tests_require=[
        'pytest >= 2.3.5, < 3'
    ],
    cmdclass={
        'test': PyTest
    },
    zip_safe=False
)

