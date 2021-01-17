#!/usr/bin/python
import json
from ansible.errors import AnsibleError


class FilterModule(object):
    ''' Query filter '''

    def filters(self):
        return {
            'to_netplan': self.to_netplan
        }

    def to_netplan(*args) -> dict:
        s = args[0]
        links = args[1]
        if not isinstance(links, list):
            raise AnsibleError('the input must be an array of network links')

        config = {
            'network': {
                'version': 2,
                'ethernets': {},
                'bridges': {}
            }
        }

        ethernets = config['network']['ethernets']
        bridges = config['network']['bridges']

        bridge_interfaces = set()
        non_bridge_interfaces = set()

        for link in links:
            if 'interface' in link:
                ethernets[link['interface']] = {}

            target = None

            if 'bridge' in link and 'name' in link['bridge'] and link['bridge']['name']:
                if link['bridge']['name'] not in bridges:
                    bridges[link['bridge']['name']] = {}
                bridge = bridges[link['bridge']['name']]
                if 'interfaces' not in bridge:
                    bridge['interfaces'] = []
                if 'interface' in link:
                    if link['interface'] in non_bridge_interfaces:
                        raise AnsibleError(
                            'interface {} in link {} cannot be linked to bridge since it has static ip configurations'
                            .format(link['interface'], json.dumps(link)))
                    bridge_interfaces.add(link['interface'])
                    bridge['interfaces'].append(link['interface'])
                    ethernets[link['interface']]['dhcp4'] = False
                    ethernets[link['interface']]['dhcp6'] = False
                if 'parameters' in link['bridge']:
                    bridge['parameters'] = {}
                    if 'stp' in link['bridge']['parameters'] and isinstance(link['bridge']['parameters']['stp'], bool):
                        bridge['parameters']['stp'] = link['bridge']['parameters']['stp']
                    if 'forward_delay' in link['bridge']['parameters'] and isinstance(link['bridge']['parameters']['forward_delay'], int):
                        bridge['parameters']['forward_delay'] = link['bridge']['parameters']['forward_delay']
                target = bridge
            else:
                if link['interface'] in bridge_interfaces:
                    raise AnsibleError(
                        'interface {} in link {} cannot be have static ip configurations since it\'s linked to a bridge'
                        .format(link['interface'], json.dumps(link)))
                non_bridge_interfaces.add(link['interface'])
                target = ethernets[link['interface']]

            if not 'addresses' in target:
                target['addresses'] = []
            if 'addresses' in link:
                target['addresses'].extend(link['addresses'])
            if 'gateway' in link:
                target['gateway4'] = link['gateway']
            if 'nameservers' in link and len(link['nameservers']) > 0:
                target['nameservers'] = link['nameservers']
            target['dhcp4'] = False
            target['dhcp6'] = False

        return config
