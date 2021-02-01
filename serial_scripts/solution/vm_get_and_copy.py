cls.vepg_stack = HeatStackFixture(
    connections=cls.connections,
    stack_name=cls.connections.project_name+'_vepg',
    template=cls.vepg_template,
    timeout_mins=15)
cls.vepg_stack.setUp()

# Get VM details and setup vsrx
     op = cls.vepg_stack.heat_client_obj.stacks.get(
          cls.vepg_stack.stack_name).outputs
      vsfo_fix = dict()
       for output in op:
            key = output['output_key']
            for i in range(1, cls.NB_VSFO_CP_NODES+1):
                vsfo = "vsfo_%s_id" % (i)
                if key == vsfo:
                    vsfo_uuid = output['output_value']
                    vsfo_fix[i] = VMFixture(
                        connections=cls.connections, uuid=vsfo_uuid, image_name='VSFO-CP-IMAGE')
                    vsfo_fix[i].read()
                    vsfo_fix[i].verify_on_setup()
                i = i + 1

            for i in range(cls.NB_VSFO_CP_NODES+1, cls.NB_VSFO_CP_NODES + cls.NB_VSFO_UP_NODES+1):
                vsfo = "vsfo_%s_id" % (i)
                if key == vsfo:
                    vsfo_uuid = output['output_value']
                    vsfo_fix[i] = VMFixture(
                        connections=cls.connections, uuid=vsfo_uuid, image_name='VSFO-UP-IMAGE')
                    vsfo_fix[i].read()
                    vsfo_fix[i].verify_on_setup()
                i = i+1

            if key == "vrp_31_id":
                vrp31_uuid = output['output_value']
                vrp_31 = VMFixture(connections=cls.connections,
                                   uuid=vrp31_uuid, image_name='VRP-IMAGE')
                vrp_31.read()
                vrp_31.verify_on_setup()

            if key == "vrp_32_id":
                vrp32_uuid = output['output_value']
                vrp_32 = VMFixture(connections=cls.connections,
                                   uuid=vrp32_uuid, image_name='VRP-IMAGE')
                vrp_32.read()
                vrp_32.verify_on_setup()

        cls.vsfo_fix = vsfo_fix
        cls.vrp_31 = vrp_31
        cls.vrp_32 = vrp_32

    # Copy scale config files and apply config if scaled setup.
        if 'orange' in cls.deploy_path:
            for i in range(1, cls.NB_VSFO_CP_NODES + cls.NB_VSFO_UP_NODES+1):
                cls.vsfo_fix[i].vm_password = 'contrail123'
                file_name = cls.deploy_path+'vsrx_config/' +\
                    cls.vsfo_fix[i].vm_name.split('B2B-')[1].lower() +\
                    '_config.txt'
                cmd = 'sshpass -p \'%s\'' % (cls.vsfo_fix[i].vm_password)
                cmd = cmd+' scp -o StrictHostKeyChecking=no %s heat-admin@%s:/tmp/'\
                    % (file_name, cls.vsfo_fix[i].vm_node_ip)
                op = os.system(cmd)
                if op is not 0:
                    cls.logger.error("Failed to copy vsrx config file %s to %s"
                                     % (file_name, cls.vsfo_fix[i].vm_node_ip))
                file_name = '/tmp/'+cls.vsfo_fix[i].vm_name.split('B2B-')[1].lower() +\
                    '_config.txt'
                cmd = 'sshpass -p \'%s\' ssh -o StrictHostKeyChecking=no heat-admin@%s \
                     sshpass -p \'%s\' scp -o StrictHostKeyChecking=no -o \
                     UserKnownHostsFile=/dev/null %s root@%s:/tmp/'\
                     % (cls.vsfo_fix[i].vm_password, cls.vsfo_fix[i].vm_node_ip,
                        cls.vsfo_fix[i].vm_password, file_name,
                        cls.vsfo_fix[i].local_ip)
                op = os.system(cmd)
                if op is not 0:
                    cls.logger.error("Failed to copy vsrx config file %s to %s"
                                     % (file_name, cls.vsfo_fix[i].local_ip))
                cmd = 'sshpass -p \'%s\' ssh -o StrictHostKeyChecking=no heat-admin@%s \
                     sshpass -p \'%s\' ssh -o StrictHostKeyChecking=no -o \
                     UserKnownHostsFile=/dev/null \
                     root@%s \'sh /config/junos-config/commit_config.sh\' '\
                     % (cls.vsfo_fix[i].vm_password, cls.vsfo_fix[i].vm_node_ip,
                        cls.vsfo_fix[i].vm_password, cls.vsfo_fix[i].local_ip)
                op = os.popen(cmd).read()
                if 'commit complete' not in op:
                    cls.logger.error("Failed to commit vsrx config on %s"
                                     % (cls.vsfo_fix[i].vm_name))
