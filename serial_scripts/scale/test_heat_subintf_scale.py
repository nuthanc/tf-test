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
from ipaddress import IPv4Network


class SubIntfScaleTest(BaseScaleTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(SubIntfScaleTest, cls).setUpClass()
        #Can update deployment path based on variable.
        cls.template_path = os.getenv('DEPLOYMENT_PATH',
                                    'serial_scripts/scale/template')
        cls.setup_vsrx()

    @classmethod
    def tearDownClass(cls):
        cls.vsrx_stack.cleanUp()
        super(SubIntfScaleTest, cls).tearDownClass()
        

    @classmethod
    def setup_vsrx(cls):
        cls.nova_h.get_image('vsrx')
        cls.nova_h.get_flavor('contrail_flavor_2cpu')
        cls.vsrx_template = f'{cls.template_path}/vsrx.yaml'
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
        file1 = f'/contrail-test/{cls.template_path}/junos_config.txt'
        file2 = f'/contrail-test/{cls.template_path}/config.sh'
        vsrx.copy_file_to_vm(localfile=file1, dstdir='/root')
        vsrx.copy_file_to_vm(localfile=file2, dstdir='/root')
        cls.inputs.run_cmd_on_server(vsrx.vm_node_ip, 'yum install -y sshpass')
        cmd = 'sshpass -p \'%s\' ssh -o StrictHostKeyChecking=no root@%s \
                     sshpass -p \'%s\' ssh -o StrictHostKeyChecking=no -o \
                     UserKnownHostsFile=/dev/null \
                     root@%s \'sh /root/config.sh\' '\
                     % (vsrx.vm_password, vsrx.vm_node_ip,
                        vsrx.vm_password, vsrx.local_ip)
        op = os.popen(cmd).read()
        import pdb;pdb.set_trace()
        
    @classmethod
    def generate_network_objects(cls, num):
        cls.parent_ip = '27.7.57.3'
        cidr = IPv4Network("17.27.0.0/16")
        # for sn in cidr.subnets(new_prefix=28):
        cls.ips = []
        cls.neighbor1_list = []
        cls.neighbor2_list = []
        cls.sub_intf_nets = []
        cls.sub_intf_masks = []
        cls.sub_mask = 28
        cls.local_as = 64500
        for n, sn in enumerate(cidr.subnets(new_prefix=sub_mask)):
            if n == num:
                break
            sub_intf_cidr = IPv4Network(sn)
            sub_intf_net = str(sub_intf_cidr.network_address)
            sub_intf_mask = sub_intf_cidr.prefixlen
            cls.sub_intf_nets.append(sub_intf_net)
            cls.sub_intf_masks.append(sub_intf_mask)
            for i,ip in enumerate(sub_intf_cidr):
                if i == 0:
                    continue
                elif i == 1:
                    cls.neighbor1_list.append(ip)
                elif i == 2:
                    cls.neighbor2_list.append(ip)
                elif i == 3:
                    cls.ips.append(ip)
                else:
                    break
        
    @classmethod
    def load_template(cls):
        num = 10
        cls.generate_network_objects(num)
        env = Environment(loader=FileSystemLoader(cls.template_path))
        vsrx_temp = env.get_template("vsrx.yaml.j2")
        junos_temp = env.get_template("junos_config.txt.j2")

        # Need to have multiple sub files
        sub_intf_file = f'{cls.template_path}/sub_intf.yaml'
        junos_file = f'{cls.template_path}/junos_config.txt'
        with open(sub_intf_file, 'w') as f:
            f.write(vsrx_temp.render(ips=cls.ips, network=cls.port_network,
                                     mask=cls.port_net_mask, sub_intf_nets=cls.sub_intf_nets, sub_intf_masks=cls.sub_intf_masks))
        with open(junos_file, 'w') as f:
            f.write(junos_temp.render(ips=cls.ips, local_as=cls.local_as,
                                      parent_ip=cls.parent_ip, neighbor1_list=cls.neighbor1_list, neighbor2_list=cls.neighbor2_list, sub_mask=cls.sub_mask))



if __name__ == '__main__':
    SubIntfScaleTest.load_template()
    SubIntfScaleTest.setUpClass()
    SubIntfScaleTest.tearDownClass()
