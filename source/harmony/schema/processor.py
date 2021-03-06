# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import copy
import urlparse
from abc import ABCMeta, abstractmethod

import jsonpointer

from harmony.schema.validator import Validator


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


class ValidateProcessor(Processor):
    '''Check schemas are valid against specification.'''

    def __init__(self, validator_class=None):
        '''Initialise processor.

        *validator_class* indicates the validator to use for checking the
        schemas. Defaults to :py:class:`harmony.schema.validator.Validator`.

        '''
        self.validator_class = validator_class
        if self.validator_class is None:
            self.validator_class = Validator

        super(ValidateProcessor, self).__init__()

    def process(self, schemas):
        '''Process *schemas*
        :py:class:`collection <harmony.schema.collection.Collection>`.

        Raise SchemaError if any of the schemas are invalid.

        '''
        for schema in schemas:
            self.validator_class.check_schema(schema)


class MixinProcessor(Processor):
    '''Expand mixin references in schemas.'''

    def process(self, schemas):
        '''Process *schemas*
        :py:class:`collection <harmony.schema.collection.Collection>`.

        Expand 'mixin' references in schemas, essentially flattening the
        schemas.

        .. note::

            *schemas* will be modified in place.

        '''
        # Process schemas
        for schema in schemas:
            self._process(schema, schemas)

    def _process(self, fragment, schemas):
        '''Process a schema *fragment* against *schemas* collection.'''
        # Recurse into relevant fragments.
        # TODO: Can this reuse jsonschema code at all?
        properties = fragment.get('properties', {})
        for value in properties.values():
            if isinstance(value, dict):
                self._process(value, schemas)

        items = fragment.get('items', [])
        if isinstance(items, dict):
            items = [items]

        for item in items:
            if isinstance(item, dict):
                self._process(item, schemas)

        additional_items = fragment.get('additionalItems')
        if additional_items and isinstance(additional_items, dict):
            self._process(additional_items, schemas)

        # Process mixin directives
        mixins = fragment.pop('$mixin', None)
        if not mixins:
            return

        if isinstance(mixins, dict):
            mixins = [mixins]

        for entry in mixins:
            reference = entry.get('$ref')
            if not reference:
                raise KeyError('No $ref defined for mixin.')

            parts = urlparse.urlsplit(reference)
            if parts.scheme != 'harmony':
                # TODO: Support resolving other schemes. Perhaps reuse
                # jsonschema RefResolver.
                continue

            # Lookup referenced schema for mixin.
            mixin = schemas.get(reference)

            # Ensure mixin has also been processed.
            self._process(mixin, schemas)

            # Merge mixin into the referring fragment.
            self._merge(fragment, mixin, entry.get('hints', {}))

    def _merge(self, target, reference, hints):
        '''Merge *reference* dictionary into *target* dictionary using *hints*.

        *target* has precedence in the merge which follows the rules:

            * New keys in *reference* are added to *target*.
            * Keys already present in *target* are not overwritten.
            * When the same key exists in both and the value is a dictionary,
              the dictionaries are recursively merged.
            * When the same key exists in both and the value is an array,
              the arrays combined (avoiding duplicate entries).

        *hints* can be used to alter the merge. It should be a dictionary of
        {path: operation}. Operation may be one of:

            * preserve - Use the target value exclusively.
            * overwrite - Use the reference value exclusively.

        For example, to specify that the department array on the target should
        not be altered::

            {"/properties/department/enum": "preserve"}

        '''
        for key, value in reference.items():
            relevant_hint = hints.get('/{0}'.format(key))

            if relevant_hint == 'preserve':
                continue

            if not key in target or relevant_hint == 'overwrite':
                # Copy value to target
                target[key] = copy.deepcopy(value)

            else:
                # Recursive merge if both target and reference value are
                # dictionaries.
                if isinstance(value, dict) and isinstance(target[key], dict):

                    # Scope hints to nested only.
                    child_hints = {}
                    for path in hints:
                        if path.startswith('/{0}/'.format(key)):
                            child_hints[path[len(key) + 1:]] = hints[path]

                    self._merge(target[key], value, child_hints)

                # Combine arrays.
                if isinstance(value, list) and isinstance(target[key], list):

                    for entry in value:
                        if not entry in target[key]:
                            target[key].append(entry)

