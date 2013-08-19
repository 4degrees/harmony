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
Validator = jsonschema.validators.extend(
    validator=jsonschema.validators.Draft4Validator,
    validators={
        'required': _required
    }
)

# Ensure appropriate meta schema set.
meta_schema_path = os.path.join(os.path.dirname(__file__), 'meta.json')
with open(meta_schema_path, 'r') as file_handler:
    meta_schema = json.load(file_handler)

Validator.META_SCHEMA = meta_schema

