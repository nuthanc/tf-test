from __future__ import absolute_import
from base import BaseScaleTest
from common.heat.base import BaseHeatTest
from tcutils.wrappers import preposttest_wrapper
import test
from vnc_api import vnc_api
from vnc_api.gen.resource_test import *
from heat_test import HeatStackFixture
from nova_test import *
from vm_test import *
from jinja2 import Environment, FileSystemLoader
import yaml


class SubIntfScaleTest(BaseScaleTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(SubIntfScaleTest, cls).setUpClass()
        #Can update deployment path based on variable.
        cls.deploy_path = os.getenv('DEPLOYMENT_PATH',
                                    'serial_scripts/scale/')
        cls.setup_vsrx()

    @classmethod
    def tearDownClass(cls):
        cls.vsrx_stack.cleanUp()
        super(SubIntfScaleTest, cls).tearDownClass()
        

    @classmethod
    def setup_vsrx(cls):
        #Create vSRX with sub-interfaces
        cls.vsrx_template_file = cls.deploy_path+"template/vsrx.yaml"
        with open(cls.vsrx_template_file, 'r') as fd:
            cls.vsrx_template = yaml.load(fd, Loader=yaml.FullLoader)

        cls.vsrx_stack = HeatStackFixture(
            connections=cls.connections,
            stack_name=cls.connections.project_name+'_vsrx_scale',
            template=cls.vsrx_template,
            timeout_mins=15)
        cls.vsrx_stack.setUp()
        op = cls.vsrx_stack.heat_client_obj.stacks.get(
            cls.vsrx_stack.stack_name).outputs
        vsrx_id = op[0]['output_value']
        vsrx = VMFixture(connections=cls.connections, uuid=vsrx_id, image_name='vsrx')
        vsrx.read()
        vsrx.verify_on_setup()
        vsrx.vm_password = 'c0ntrail123'
        file1 = f'/contrail-test/{cls.deploy_path}template/junos_config.txt'
        file2 = f'/contrail-test/{cls.deploy_path}template/config.sh'
        vsrx.copy_file_to_vm(localfile=file1, dstdir='/root')
        vsrx.copy_file_to_vm(localfile=file2, dstdir='/root')
        cmd = 'sshpass -p \'%s\' ssh -o StrictHostKeyChecking=no root@%s \
                     sshpass -p \'%s\' ssh -o StrictHostKeyChecking=no -o \
                     UserKnownHostsFile=/dev/null \
                     root@%s \'sh /root/config.sh\' '\
                     % (vsrx.vm_password, vsrx.vm_node_ip,
                        vsrx.vm_password, vsrx.local_ip)
        op = os.popen(cmd).read()
        import pdb;pdb.set_trace()
        if 'commit complete' not in op:
            cls.logger.error("Failed to commit vsrx config on %s"
                             % (vsrx.vm_name))

    @staticmethod
    def load_template():
        from ipaddress import IPv4Network
        # cidr = IPv4Network("27.27.0.0/16")
        cidr = IPv4Network("27.37.47.0/28")
        network = str(cidr.network_address)
        mask = cidr.prefixlen
        parent_ip = ''
        neighbors = []
        local_as = 64500
        ips = []
        for i, ip in enumerate(cidr):
            # Skipping 3 address in the beginning, 1 for gw, 1 for dns, 1 for parent port
            if i < 4 or i == cidr.num_addresses - 1:
                if i == 1 or i == 2:
                    neighbors.append(ip)
                if i == 3:
                    parent_ip = ip
                continue
            ips.append(ip)
        deploy_path = os.getenv('DEPLOYMENT_PATH',
                                '/contrail-test/serial_scripts/scale/')
        template_dir = deploy_path+"template/"
        env = Environment(loader=FileSystemLoader(template_dir))
        vsrx_temp = env.get_template("vsrx.yaml.j2")
        junos_temp = env.get_template("junos_config.txt.j2")
        filename1 = template_dir + "vsrx.yaml"
        filename2 = template_dir + "junos_config.txt"
        with open(filename1, 'w') as f:
            f.write(vsrx_temp.render(ips=ips, network=network, mask=mask))
        with open(filename2, 'w') as f:
            f.write(junos_temp.render(ips=ips, local_as=local_as,
                                      parent_ip=parent_ip, neighbor1=neighbors[0], neighbor2=neighbors[1]))



if __name__ == '__main__':
    SubIntfScaleTest.load_template()
    SubIntfScaleTest.setUpClass()
    SubIntfScaleTest.tearDownClass()
