# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError('Could not import json or simplejson')

import jsonschema.validators
from jsonschema import draft4_format_checker as format_checker


# Custom validators
def _required(validator, required, instance, schema):
    '''Validate 'required' properties.'''
    if not validator.is_type(instance, 'object'):
        return

    for index, requirement in enumerate(required):
        if requirement not in instance:
            error = jsonschema.ValidationError(
                '{0!r} is a required property'.format(requirement)
            )
            error.schema_path.append(index)
            yield error


# Construct validator as extension of Json Schema Draft 4.
_Validator = jsonschema.validators.extend(
    validator=jsonschema.validators.Draft4Validator,
    validators={
        'required': _required
    }
)

# Ensure appropriate meta schema set.
meta_schema_path = os.path.join(os.path.dirname(__file__), 'meta.json')
with open(meta_schema_path, 'r') as file_handler:
    meta_schema = json.load(file_handler)

_Validator.META_SCHEMA = meta_schema


class Validator(_Validator):
    '''Schema validator.'''

    def __init__(self, *args, **kw):
        '''Initialise validator.'''
        super(Validator, self).__init__(*args, **kw)
        if self.format_checker is None:
            self.format_checker = jsonschema.draft4_format_checker
