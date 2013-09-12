# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from collections import Mapping

import jsonpointer


class ErrorTree(Mapping):
    '''Convert a list of error objects to a tree structure.'''

    def __init__(self, errors):
        '''Initialise tree from *errors* list.'''
        tree = {}
        for error in sorted(
            errors, key=lambda item: len(list(item.path)),
            reverse=True
        ):
            branch = tree

            path = list(error.path)

            path.insert(0, '__root__')

            if error.validator == 'required':
                # Required is set one level above so have to retrieve final
                # path segment.
                schema_path = '/' + '/'.join(map(str, error.schema_path))
                segment = jsonpointer.resolve_pointer(
                    error.schema, schema_path
                )
                path.append(segment)

            for segment in path[:-1]:
                branch = branch.setdefault(segment, {})

            if path[-1] in branch and isinstance(branch[path[-1]], Mapping):
                branch[path[-1]]['__self__'] = error.message
            else:
                branch[path[-1]] = error.message

        self._tree = tree.get('__root__', {})

    def __getitem__(self, key):
        '''Return item for *key*.'''
        return self._tree[key]

    def __len__(self):
        '''Return number of keys at root of tree.'''
        return len(self._tree)

    def __iter__(self):
        '''Return iterator over tree.'''
        return iter(self._tree)
