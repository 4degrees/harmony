# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os

from harmony.schema.collection import Collection
from harmony.schema.collector import FilesystemCollector
from harmony.schema.processor import MixinProcessor, ValidateProcessor
from harmony.schema.validator import Validator


class Session(object):
    '''A configuration of the various components in a standard way.'''

    #: The default schema search path.
    DEFAULT_SCHEMA_PATH = os.path.join(
        os.path.dirname(__file__), '..', '..', 'resource', 'schema'
    )

    def __init__(self, collector=None, processors=None, validator_class=None):
        '''Initialise session.

        *collector* is used to collect schemas for use in the session and
        should conform to the :py:class:`~harmony.schema.collector.Collector`
        interface. Defaults to a
        :py:class:`~harmony.schema.collector.FileSystemCollector` using the
        environment variable :envvar:`HARMONY_SCHEMA_PATH` to discover schemas.

        *processors* specifies a list of
        :py:class:`~harmony.schema.processor.Processor` instances that will
        post-process any discovered schemas. If not specified will default to
        [:py:class:`~harmony.schema.processor.ValidateProcessor`,
         :py:class:`~harmony.schema.processor.MixinProcessor`].

        *validator_class* should be the class to use for validation of schemas
        and instances. Defaults to
        :py:class:`harmony.schema.validator.Validator`.

        '''
        self.schemas = Collection()

        self.collector = collector
        if self.collector is None:
            paths = os.environ.get(
                'HARMONY_SCHEMA_PATH', self.DEFAULT_SCHEMA_PATH
            ).split(os.pathsep)
            self.collector = FilesystemCollector(paths)

        self.validator_class = validator_class
        if self.validator_class is None:
            self.validator_class = Validator

        self.processors = processors
        if self.processors is None:
            self.processors = [
                ValidateProcessor(self.validator_class), MixinProcessor()
            ]

        self.refresh()

    def refresh(self):
        '''Discover schemas and add to local collection.

        .. note::

            Collection will be processed with self.processors.

        '''
        self.schemas.clear()
        for schema in self.collector.collect():
            self.schemas.add(schema)

        for processor in self.processors:
            processor.process(self.schemas)

    def instantiate(self, schema, data=None):
        '''Instantiate *schema* with initial *data*.

        *schema* may be either a registered schema id or a schema object.

        Only required properties with default values will be used from the
        schema to construct the instance. Any values in *data* will take
        precedence over those in the schema.

        '''
        if isinstance(schema, basestring):
            schema = self.schemas.get(schema)

        if data is None:
            data = {}

        return self._instantiate(schema, data)

    def _instantiate(self, schema, data):
        '''Construct an instance of *schema* using initial *data*.'''
        required_properties = schema.get('required', [])

        for key, value in schema.get('properties').items():
            required = key in required_properties
            datatype = value.get('type')

            if not required:
                # Don't recursively process non-required non-objects.
                if datatype != 'object':
                    continue

                # Don't recursively process objects that are not required if
                # the object does not already exist on the instance.
                if key not in data:
                    continue

            if datatype == 'object':
                # Recursively process objects.
                data.setdefault(key, {})
                self._instantiate(value, data[key])

            else:
                # Set default values.
                default = value.get('default')
                if default:
                    data.setdefault(key, default)

        return data

    def validate(self, instance, additional_schemas=None):
        '''Validate *instance*.

        If *additional_schemas* is supplied, will also validate against those.
        Each schema may be either a registered schema id or a schema object.

        Return any errors as a list of objects containing full diagnostic
        information.

        '''
        # Validate against base system requirements.
        errors = self._validate(instance, ['harmony:/base'])
        if errors:
            return errors

        # Validate against specified harmony schema.
        errors = self._validate(instance, [instance['harmony_type']])
        if errors:
            return errors

        # Validate against additional schemas if required.
        errors = self._validate(instance, additional_schemas)
        return errors

    def _validate(self, instance, schemas):
        '''Validate *instance* against *schemas*.

        Each schema may be either a registered schema id or a schema object.

        Return any errors as a list of objects containing full diagnostic
        information.

        '''
        errors = []
        for schema in schemas:
            if isinstance(schema, basestring):
                schema = self.schemas.get(schema)

            validator = self.validator_class(schema)
            validator_errors = list(validator.iter_errors(instance))
            for error in validator_errors:
                error.schema = schema

            errors.extend(validator_errors)

        return errors

