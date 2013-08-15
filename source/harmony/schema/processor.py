# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from abc import ABCMeta, abstractmethod


class Processor(object):
    '''Process schemas.'''

    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self, schemas):
        '''Process *schemas*
        :py:class:`collection <harmony.schema.collection.Collection>`.

        .. note::

            *schemas* are modified in place.

        '''

