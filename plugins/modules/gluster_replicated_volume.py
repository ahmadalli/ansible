#!/usr/bin/python

# this file is derived from gluster's ansible collection's gluster_volume module
#   https://github.com/gluster/gluster-ansible-collection/blob/bc0982a24e85f3829ee19cd62da64e82601870a6/plugins/modules/gluster_volume.py

import platform
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ahmadalli.ansible.plugins.module_utils.gluster import GlusterVolumeHelper


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True, aliases=['volume']),
            state=dict(type='str', required=True, choices=[
                       'absent', 'started', 'stopped', 'present']),
            cluster=dict(type='list'),
            host=dict(type='str'),
            transport=dict(type='str', default='tcp', choices=[
                           'tcp', 'rdma', 'tcp,rdma']),
            bricks=dict(type='list', aliases=['brick']),
            start_on_create=dict(type='bool', default=True),
            force=dict(type='bool', default=False),
        ),
    )

    changed = False

    action = module.params['state']
    volume_name = module.params['name']
    cluster = module.params['cluster']
    brick_paths = module.params['bricks']
    transport = module.params['transport']
    hostname = module.params['host']
    start_on_create = module.boolean(module.params['start_on_create'])
    force = module.boolean(module.params['force'])

    if not hostname:
        hostname = platform.node()

    # Clean up if last element is empty. Consider that yml can look like this:
    #   cluster="{% for host in groups['glusterfs'] %}{{ hostvars[host]['private_ip'] }},{% endfor %}"
    if cluster is not None and len(cluster) > 1 and cluster[-1] == '':
        cluster = cluster[0:-1]

    if cluster is None:
        cluster = []

    if brick_paths is None:
        brick_paths = []

    helper = GlusterVolumeHelper(module)

    volumes = helper.get_volumes()

    if action == 'absent':
        if volume_name in volumes:
            if volumes[volume_name]['status'].lower() != 'stopped':
                helper.stop_volume(volume_name)
            helper.delete_volume(volume_name)
            changed = True

    if action == 'present':
        # create if it doesn't exist
        if volume_name not in volumes:
            helper.create_volume(volume_name, transport,
                                 cluster, brick_paths, force)
            volumes = helper.get_volumes()
            changed = True

        if volume_name in volumes:
            if volumes[volume_name]['status'].lower() != 'started' and start_on_create:
                helper.start_volume(volume_name)
                changed = True

            # switch bricks
            new_bricks = []
            removed_bricks = []
            all_bricks = []
            bricks_in_volume = volumes[volume_name]['bricks']

            for node in cluster:
                for brick_path in brick_paths:
                    brick = '%s:%s' % (node, brick_path)
                    all_bricks.append(brick)
                    if brick not in bricks_in_volume:
                        new_bricks.append(brick)

            if not new_bricks and len(all_bricks) > 0 and len(all_bricks) < len(bricks_in_volume):
                for brick in bricks_in_volume:
                    if brick not in all_bricks:
                        removed_bricks.append(brick)

            if new_bricks:
                helper.add_bricks(volume_name, new_bricks,
                                  len(all_bricks), force)
                changed = True

            if removed_bricks:
                helper.remove_bricks(
                    volume_name, removed_bricks, len(all_bricks))
                changed = True
        else:
            module.fail_json(msg='failed to create volume %s' % volume_name)

    if action != 'absent' and volume_name not in volumes:
        module.fail_json(msg='volume not found %s' % volume_name)

    if action == 'started':
        if volumes[volume_name]['status'].lower() != 'started':
            helper.start_volume(volume_name)
            changed = True

    if action == 'stopped':
        if volumes[volume_name]['status'].lower() != 'stopped':
            helper.stop_volume(volume_name)
            changed = True

    facts = {}
    facts['glusterfs'] = {'volumes': volumes}

    module.exit_json(changed=changed, ansible_facts=facts)

if __name__ == '__main__':
    main()
