from __future__ import absolute_import
from base import BaseSolutionsTest
from common.heat.base import BaseHeatTest
from tcutils.wrappers import preposttest_wrapper
import test
from vn_test import *
from quantum_test import *
from policy_test import *
from vm_test import *
from vnc_api import vnc_api
from vnc_api.gen.resource_test import *
from heat_test import HeatStackFixture
from nova_test import *
import os
import yaml

af_test = 'dual'

class SubIntfScaleTest(BaseSolutionsTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(SubIntfScaleTest, cls).setUpClass()
        #Can update deployment path based on variable.
        cls.deploy_path=os.getenv('DEPLOYMENT_PATH',
                            'serial_scripts/solution/topology/mini_deployment/')
        cls.setup_vsrx()

    @classmethod
    def tearDownClass(cls):
        super(SubIntfScaleTest, cls).tearDownClass()

    @classmethod
    def setup_vsrx(cls):
        #Create vSRX with sub-interfaces
        cls.vsrx_template_file=cls.deploy_path+"template/vsrx.yaml"
        with open(cls.vsrx_template_file, 'r') as fd:
            cls.vsrx_template = yaml.load(fd, Loader=yaml.FullLoader)

        for each_resource in cls.vsrx_template['resources']:
            if 'personality' in cls.vsrx_template['resources']\
                                    [each_resource]['properties']:
                inject_file='/config/junos-config/configuration.txt'
                fp1=open(cls.vsrx_template['resources'][each_resource]\
                                ['properties']['personality'][inject_file]\
                                ['get_file'], 'r')
                data=fp1.read()
                cls.vsrx_template['resources'][each_resource]['properties']\
                    ['personality'][inject_file]=data
                fp1.close()

        cls.vsrx_stack = HeatStackFixture(
                                connections=cls.connections,
                                stack_name=cls.connections.project_name+'_vsrx_scale',
                                template=cls.vsrx_template,
                                timeout_mins=15)
        cls.vsrx_stack.setUp()
        import pdb;pdb.set_trace()

if __name__ == '__main__':
    SubIntfScaleTest.setUpClass()