# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import copy


def merge(target, reference):
    '''Merge *reference* dictionary into *target* dictionary.

    *target* has precedence in the merge which follows the rules:

        * New keys in *reference* are added to *target*.
        * Keys already present in *target* are not overwritten.
        * When the same key exists in both and the value is a dictionary, the
          dictionaries are also merged.

    '''
    for key, value in reference.items():

        if not key in target:
            # Copy value to target
            target[key] = copy.deepcopy(value)

        else:
            # Merge if both target and reference value is a dictionary
            if isinstance(value, dict) and isinstance(target[key], dict):
                merge(target[key], value)

