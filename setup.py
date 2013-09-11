# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
import re

from setuptools.command.test import test as TestCommand
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


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
    dependency_links=[
        'https://github.com/Julian/jsonschema/tarball/292a256b918af1e567982bb801c427cf4ca5b9fe#egg-jsonschema-2.0.1a'
    ],
    install_requires=[
        'jsonschema >= 2.0.1',
        'jsonpointer >= 1.0',
        'PySide >= 1.1.1'
    ],
    tests_require=['pytest >= 2.3.5'],
    cmdclass={
        'test': PyTest
    },
    zip_safe=False
)

