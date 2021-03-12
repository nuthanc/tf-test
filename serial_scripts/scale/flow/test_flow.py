from common.base import GenericTestBase
from tcutils.wrappers import preposttest_wrapper
import test
from compute_node_test import ComputeNodeFixture


class TestFlowScale(GenericTestBase):

    @classmethod
    def setUpClass(cls):
        super(TestFlowScale, cls).setUpClass()
        cls.get_compute_fixtures()
        cls.preconfig1()
        # cls.method2()

    @classmethod
    def tearDownClass(cls):
        super(TestFlowScale, cls).tearDownClass()

    @classmethod
    def get_compute_fixtures(cls):
        cls.compute_fixtures = []
        for name, ip in cls.connections.inputs.compute_info.items():
            cls.compute_fixtures.append(
                ComputeNodeFixture(cls.connections, ip))
            # Add physical interface to computes here

    @classmethod
    def set_flow_entries(cls):
        for compute_fixture in cls.compute_fixtures:
            compute_fixture.add_vrouter_module_params(
                {'vr_flow_entries': str(2 * 1024 * 1024)}, reload_vrouter=True)
            print(compute_fixture.read_vrouter_module_params())

    @classmethod
    def add_flow_cache_timeout(cls):
        # Add flow_cache_timeout in all the computes
        flow_timeout = 9999
        for cmp_fix in cls.compute_fixtures:
            cmp_fix.set_flow_aging_time(flow_timeout)

    @classmethod
    def preconfig1(cls):
        cls.set_flow_entries()
        cls.add_flow_cache_timeout()

        
    @classmethod
    def preconfig2(cls):
        pass

    @test.attr(type=['flow_scale'])
    @preposttest_wrapper
    def test_flow_scale(self):
        '''
        Description: Test to scale 1 million flows
         Test steps:
                1. 
         Pass criteria: 
         Maintainer : nuthanc@juniper.net 
        '''
        print('hola')

if __name__ == '__main__':
    TestFlowScale.setUpClass()