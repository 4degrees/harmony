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
            paths = os.environ.get('HARMONY_SCHEMA_PATH', '').split(os.pathsep)
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

