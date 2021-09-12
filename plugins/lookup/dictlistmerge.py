DOCUMENTATION = """
        lookup: dictlistmerge
        author: ahmadali shafiee <mail@ahmadalli.net>
        short_description: merges Dict<str, List> variables starting with some keyword
        description:
            - This lookup returns the result of merging some variables which start witch specific keyword
        options:
          _keys:
            description: one of more shared prefixes which all the variables should have in order to be merged
            required: True
        notes: []
"""
from ansible.errors import AnsibleError, AnsibleUndefinedVariable
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.six import string_types
from ansible.utils.display import Display

display = Display()


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        if variables is not None:
            self._templar.available_variables = variables
        myvars = getattr(self._templar, '_available_variables', {})

        var_names = []
        for term in terms:
            if not isinstance(term, string_types):
                raise AnsibleError('Invalid setting identifier, "{}" is not a string, its a {}'.format(
                    term, type(term).__name__))
            var_names.extend(
                [x for x in myvars.keys() if x.startswith(term)])

        if len(var_names) == 0:
            return []

        display.vvvv('these vars found: {}'.format(', '.join(var_names)))
        result = {}
        for var_name in var_names:
            try:
                var = myvars[var_name]
            except KeyError:
                try:
                    var = myvars['hostvars'][myvars['inventory_hostname']][var_name]
                except KeyError:
                    raise AnsibleUndefinedVariable(
                        'No variable found with this name: {}'.format(var_name))
            if var is None:
                continue

            if isinstance(var, dict):
                for key in var:
                    items = self._templar.template(var[key], fail_on_undefined=True)
                    if isinstance(items, list):
                        if not key in result:
                            result[key] = []
                        for item in items:
                            display.vvvv('adding {} from {}[{}] to the results'.format(
                                item, var_name, key))
                            result[key].append(self._templar.template(
                                item, fail_on_undefined=True))
                    else:
                        raise AnsibleError(
                            'dictionary items should be of type list. {}[{}] is of type {}'.format(var_name, key, type(items).__name__))
            else:
                raise AnsibleError(
                    'variables should be of type dict. {} is of type {}'.format(var_name, type(var).__name__))

        return result
