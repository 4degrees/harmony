# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from abc import ABCMeta, abstractmethod


class Collector(object):
    '''Collect and return schemas.'''

    __metaclass__ = ABCMeta

    @abstractmethod
    def collect(self):
        '''Yield collected schemas.

        Each schema should be a Python dictionary.

        '''

