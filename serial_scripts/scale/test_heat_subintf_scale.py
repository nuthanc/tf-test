from __future__ import absolute_import
from base import BaseScaleTest
from common.heat.base import BaseHeatTest
from tcutils.wrappers import preposttest_wrapper
import test
from vnc_api import vnc_api
from vnc_api.gen.resource_test import *
from heat_test import HeatStackFixture
from nova_test import *
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
        super(SubIntfScaleTest, cls).tearDownClass()
        cls.vsrx_stack.cleanUp()

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
        import pdb
        pdb.set_trace()

    @staticmethod
    def load_template():
        from ipaddress import IPv4Network
        # cidr = IPv4Network("27.27.0.0/16")
        cidr = IPv4Network("27.27.0.0/28")
        network = str(cidr.network_address)
        mask = cidr.prefixlen
        ips = []
        for i, ip in enumerate(cidr):
            # Skipping 3 address in the beginning, 1 for gw, 1 for dns, 1 for parent port
            if i < 4 or i == cidr.num_addresses - 1:
                continue
            ips.append(ip)
        deploy_path = os.getenv('DEPLOYMENT_PATH',
                                '/contrail-test/serial_scripts/scale/')
        template_dir = deploy_path+"template/"
        env = Environment(loader=FileSystemLoader(template_dir))
        vsrx_temp = env.get_template("vsrx.yaml.j2")
        filename = template_dir + "vsrx.yaml"
        with open(filename, 'w') as f:
            f.write(vsrx_temp.render(ips=ips, network=network, mask=mask))



if __name__ == '__main__':
    SubIntfScaleTest.load_template()
    SubIntfScaleTest.setUpClass()
    SubIntfScaleTest.tearDownClass()
