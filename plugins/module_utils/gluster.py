#!/usr/bin/python

# this file is derived from gluster's ansible collection's gluster_volume module
#   https://github.com/gluster/gluster-ansible-collection/blob/bc0982a24e85f3829ee19cd62da64e82601870a6/plugins/modules/gluster_volume.py


import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native, to_text


class GlusterVolumeHelper(object):
    _module: AnsibleModule = None
    _gluster_bin: str = ''

    def __init__(self, module: AnsibleModule):
        self._module = module
        self._gluster_bin = self._module.get_bin_path('gluster', True)

    def run_gluster(self, gargs: list, **kwargs):
        args = [self._gluster_bin, '--mode=script']
        args.extend(gargs)
        args = [to_text(item) for item in args]
        try:
            rc, out, err = self._module.run_command(args, **kwargs)
            if rc != 0:
                self._module.fail_json(msg='error running gluster (%s) command (rc=%d): %s' %
                                 (' '.join(args), rc, out or err), exception=traceback.format_exc())
        except Exception as e:
            self._module.fail_json(msg='error running gluster (%s) command: %s' % (' '.join(args),
                                                                             to_native(e)), exception=traceback.format_exc())
        return out

    def run_gluster_nofail(self, gargs: list, **kwargs):
        args = [self._gluster_bin]
        args.extend(gargs)
        args = [to_text(item) for item in args]
        rc, out, err = self._module.run_command(args, **kwargs)
        if rc != 0:
            return None
        return out

    def get_volumes(self):
        out = self.run_gluster(['volume', 'info'])

        volumes = {}
        volume = {}
        for row in out.split('\n'):
            if ': ' in row:
                key, value = row.split(': ')
                if key.lower() == 'volume name':
                    volume['name'] = value
                    volume['options'] = {}
                    volume['quota'] = False
                if key.lower() == 'volume id':
                    volume['id'] = value
                if key.lower() == 'status':
                    volume['status'] = value
                if key.lower() == 'transport-type':
                    volume['transport'] = value
                if value.lower().endswith(' (arbiter)'):
                    if 'arbiters' not in volume:
                        volume['arbiters'] = []
                    value = value[:-10]
                    volume['arbiters'].append(value)
                elif key.lower() == 'number of bricks':
                    volume['replicas'] = value[-1:]
                if key.lower() != 'bricks' and key.lower()[:5] == 'brick':
                    if 'bricks' not in volume:
                        volume['bricks'] = []
                    volume['bricks'].append(value)
                # Volume options
                if '.' in key:
                    if 'options' not in volume:
                        volume['options'] = {}
                    volume['options'][key] = value
                    if key == 'features.quota' and value == 'on':
                        volume['quota'] = True
            else:
                if row.lower() != 'bricks:' and row.lower() != 'options reconfigured:':
                    if len(volume) > 0:
                        volumes[volume['name']] = volume
                    volume = {}
        return volumes

    def start_volume(self, name):
        self.run_gluster(['volume', 'start', name])

    def stop_volume(self, name):
        self.run_gluster(['volume', 'stop', name])

    def delete_volume(self, name):
        self.run_gluster(['volume', 'delete', name])

    def create_volume(self, name: str, transport: str, hosts: list, bricks: list, force: bool):
        args = ['volume', 'create']
        args.append(name)
        args.append('replica')
        args.append(len(hosts) * len(bricks))
        args.append('transport')
        args.append(transport)
        for brick in bricks:
            for host in hosts:
                args.append(('%s:%s' % (host, brick)))
        if force:
            args.append('force')
        self.run_gluster(args)

    def add_bricks(self, name: str, new_bricks: list, replica: int, force: bool):
        args = ['volume', 'add-brick', name]
        args.append('replica')
        args.append(str(replica))
        args.extend(new_bricks)
        if force:
            args.append('force')
        self.run_gluster(args)

    def remove_bricks(self, name: str, removed_bricks: list, replica: int):
        args = ['volume', 'remove-brick', name]
        args.append('replica')
        args.append(str(replica))
        args.extend(removed_bricks)
        args.append('force')
        self.run_gluster(args)
