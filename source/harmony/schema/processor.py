# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import copy
import urlparse
from abc import ABCMeta, abstractmethod

from harmony.schema.validator import validator_for


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
        schemas. If not specified, an appropriate validator will be chosen for
        each schema checked.

        '''
        self.validator_class = validator_class
        super(ValidateProcessor, self).__init__()

    def process(self, schemas):
        '''Process *schemas*
        :py:class:`collection <harmony.schema.collection.Collection>`.

        Raise SchemaError if any of the schemas are invalid.

        '''
        for schema in schemas:
            # Pick appropriate validator if none specified.
            validator_class = self.validator_class
            if validator_class is None:
                validator_class = validator_for(schema)

            validator_class.check_schema(schema)


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
        for item in items:
            if isinstance(item, dict):
                self._process(item, schemas)

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
            self._merge(fragment, mixin)

    def _merge(self, target, reference):
        '''Merge *reference* dictionary into *target* dictionary.

        *target* has precedence in the merge which follows the rules:

            * New keys in *reference* are added to *target*.
            * Keys already present in *target* are not overwritten.
            * When the same key exists in both and the value is a dictionary,
              the dictionaries are also merged.

        '''
        for key, value in reference.items():

            if not key in target:
                # Copy value to target
                target[key] = copy.deepcopy(value)

            else:
                # Merge if both target and reference value is a dictionary
                if isinstance(value, dict) and isinstance(target[key], dict):
                    self._merge(target[key], value)
