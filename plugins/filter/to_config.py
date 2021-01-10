#!/usr/bin/python
import json
from numbers import Number
from ansible.errors import AnsibleError


class FilterModule(object):
    ''' Query filter '''

    def filters(self):
        return {
            'to_config': self.to_config
        }

    def to_config(*args) -> str:
        s = args[0]
        source = args[1]
        if isinstance(source, dict):
            items = []
            for k, v in source.items():
                items.append('{} = {}'.format(k, s.to_config(v)))
            return '[\n  {}\n]'.format(str.join(',\n  ', items))
        if isinstance(source, list):
            raise AnsibleError('cannot convert array {} to config'.format(
                json.dumps(source)))
        if isinstance(source, Number) or isinstance(source, str):
            return json.dumps(source)
        raise AnsibleError(
            'cannot convert source {} to config'.format(json.dumps(source)))
