# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.


class HarmonyError(Exception):
    '''Raise when a general Harmony error occurs.'''


class SchemaConflictError(HarmonyError):
    '''Raise when a schema conflict occurs.'''


class PublisherError(HarmonyError):
    '''Raise when a general publisher error occurs.'''
