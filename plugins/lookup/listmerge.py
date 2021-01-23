DOCUMENTATION = """
        lookup: merger
        author: ahmadali shafiee <mail@ahmadalli.net>
        short_description: merges variable starting with some keyword
        description:
            - This lookup returns the result of merging some variables which start witch specific keyword
        options:
          _keys:
            description: one of more shared prefixes which all the variables should have in order to be merged
            required: True
        notes: []
"""
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
import copy

display = Display()


class LookupModule(LookupBase):

    def run(self, keys, variables=None, **kwargs):
        var_names = []
        for key in keys:
            var_names.extend(
                [x for x in variables.keys() if x.startswith(key)])

        if len(var_names) == 0:
            return None

        result = []
        for var_name in var_names:
            var = variables[var_name]
            if var is None:
                continue

            if isinstance(var, list):
                result.extend(var)
            else:
                raise AnsibleError(
                    'variables should be of type list. {} is of type {}'.format(var_names[0]))

        return result
