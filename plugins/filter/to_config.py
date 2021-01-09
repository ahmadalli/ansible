#!/usr/bin/python
import json
from numbers import Number


def to_config(*args) -> str:
    source = args[0]
    if isinstance(source, dict):
        items = []
        for k, v in source.items():
            items.append('{} = {}'.format(k, to_config(v)))
        return '[\n  {}\n]'.format(str.join(',\n  ', items))
    if isinstance(source, list):
        raise Exception('cannot convert array {} to config'.format(
            json.dumps(source)))
    if isinstance(source, Number) or isinstance(source, str):
        return json.dumps(source)
    raise Exception(
        'cannot convert source {} to config'.format(json.dumps(source)))


class FilterModule(object):
    ''' Query filter '''

    def filters(self):
        return {
            'to_config': to_config
        }
