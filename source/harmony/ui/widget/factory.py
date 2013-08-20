# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.


class Factory(object):
    '''Manage constructing widgets for schemas.'''

    def __call__(self, schema, options=None):
        '''Return an appropriate widget for *schema*.'''
