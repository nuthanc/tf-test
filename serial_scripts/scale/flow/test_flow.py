from common.base import GenericTestBase
from tcutils.wrappers import preposttest_wrapper
import test
from compute_node_test import ComputeNodeFixture


class TestFlowScale(GenericTestBase):

    @classmethod
    def setUpClass(cls):
        super(TestFlowScale, cls).setUpClass()
        cls.get_compute_fixtures()
        cls.add_phy_intf_in_vrouter_env()
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
    def add_phy_intf_in_vrouter_env(cls):
        for compute_fixture in cls.compute_fixtures:
            intf = cls.inputs.inputs.host_data[compute_fixture.ip]['roles']['vrouter']['PHYSICAL_INTERFACE']
            line = "'PHYSICAL_INTERFACE=%s'" % intf
            file = '/etc/contrail/common_vrouter.env'
            cmd = "grep -F %s %s" % (line, file)
            output = compute_fixture.execute_cmd(cmd, container=None)

            if not output:
                echo_line = "echo %s >> %s" % (line, file)
                cd_vrouter = 'cd /etc/contrail/vrouter'
                down_up = 'docker-compose down && docker-compose up -d'
                cmd = '%s;%s;%s' %(echo_line, cd_vrouter, down_up)
                compute_fixture.execute_cmd(cmd, container=None)

    @classmethod
    def set_flow_entries(cls):
        for compute_fixture in cls.compute_fixtures:
            compute_fixture.add_vrouter_module_params(
                {'vr_flow_entries': str(1024 * 1024)}, reload_vrouter=True)
            print(compute_fixture.read_vrouter_module_params())

    @classmethod
    def add_flow_cache_timeout(cls):
        # Add flow_cache_timeout in all the computes
        flow_timeout = 9999
        for cmp_fix in cls.compute_fixtures:
            import pdb;pdb.set_trace()
            cmp_fix.set_flow_aging_time(flow_timeout)

    @classmethod
    def preconfig1(cls):
        # cls.set_flow_entries()
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
