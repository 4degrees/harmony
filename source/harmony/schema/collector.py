# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
from abc import ABCMeta, abstractmethod

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError('Could not import json or simplejson')


class Collector(object):
    '''Collect and return schemas.'''

    __metaclass__ = ABCMeta

    @abstractmethod
    def collect(self):
        '''Yield collected schemas.

        Each schema should be a Python dictionary.

        '''


class FilesystemCollector(Collector):

    def __init__(self, paths=None, recursive=True):
        '''Initialise with *paths* to search.

        If *recursive* is True then all subdirectories of *paths* will also be
        searched.

        '''
        self.paths = paths
        self.recursive = recursive
        if self.paths is None:
            self.paths = []
        super(FilesystemCollector, self).__init__()

    def collect(self):
        '''Yield collected schemas.'''
        for path in self.paths:
            for base, directories, filenames in os.walk(path):
                for filename in filenames:

                    _, extension = os.path.splitext(filename)
                    if extension != '.json':
                        continue

                    filepath = os.path.join(base, filename)
                    with open(filepath, 'r') as file_handler:
                        schema = json.load(file_handler)
                        yield schema

                if not self.recursive:
                    del directories[:]

