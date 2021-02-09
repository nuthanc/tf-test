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
        cls.vsrx_image = cls.nova_h.get_image('vsrx')
        cls.flavor = cls.nova_h.get_flavor('contrail_flavor_2cpu')
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
        network = '27.7.57.0'
        mask = '29'
        parent_ip = '27.7.57.3'
        cidr = IPv4Network("17.97.0.0/16")
        # for sn in cidr.subnets(new_prefix=28):
        ips = []
        neighbor1_list = []
        neighbor2_list = []
        sub_intf_nets = []
        sub_intf_masks = []
        sub_mask = 20
        for sn in cidr.subnets(new_prefix=sub_mask):
            sub_intf_cidr = IPv4Network(sn)
            sub_intf_net = str(sub_intf_cidr.network_address)
            sub_intf_mask = sub_intf_cidr.prefixlen
            sub_intf_nets.append(sub_intf_net)
            sub_intf_masks.append(sub_intf_mask)
            for i,ip in enumerate(sub_intf_cidr):
                if i == 0:
                    continue
                elif i == 1:
                    neighbor1_list.append(ip)
                elif i == 2:
                    neighbor2_list.append(ip)
                elif i == 3:
                    ips.append(ip)
                else:
                    break
        local_as = 64500
        deploy_path = os.getenv('DEPLOYMENT_PATH',
                                '/contrail-test/serial_scripts/scale/')
        template_dir = deploy_path+"template/"
        env = Environment(loader=FileSystemLoader(template_dir))
        vsrx_temp = env.get_template("vsrx.yaml.j2")
        junos_temp = env.get_template("junos_config.txt.j2")
        filename1 = template_dir + "vsrx.yaml"
        filename2 = template_dir + "junos_config.txt"
        with open(filename1, 'w') as f:
            f.write(vsrx_temp.render(ips=ips, network=network,
                                     mask=mask, sub_intf_nets=sub_intf_nets, sub_intf_masks=sub_intf_masks))
        with open(filename2, 'w') as f:
            f.write(junos_temp.render(ips=ips, local_as=local_as,
                                      parent_ip=parent_ip, neighbor1_list=neighbor1_list, neighbor2_list=neighbor2_list, sub_mask=sub_mask))



if __name__ == '__main__':
    SubIntfScaleTest.load_template()
    SubIntfScaleTest.setUpClass()
    SubIntfScaleTest.tearDownClass()
