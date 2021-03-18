from common.base import GenericTestBase
from tcutils.wrappers import preposttest_wrapper
import test
from compute_node_test import ComputeNodeFixture
from tcutils.traffic_utils.hping_traffic import Hping3
import time

class TestFlowScale(GenericTestBase):

    @classmethod
    def setUpClass(cls):
        super(TestFlowScale, cls).setUpClass()
        cls.get_compute_fixtures()
        # cls.add_phy_intf_in_vrouter_env()
        # cls.preconfig()

    @classmethod
    def tearDownClass(cls):
        super(TestFlowScale, cls).tearDownClass()

    def setUp(self):
        super(TestFlowScale, self).setUp()
        self.vn1_fixture = self.create_only_vn()
        self.vn1_vm1_fixture = self.create_vm(self.vn1_fixture)
        self.vn1_vm2_fixture = self.create_vm(self.vn1_fixture)
        self.vn1_vm1_fixture.wait_till_vm_is_up()
        self.vn1_vm2_fixture.wait_till_vm_is_up()
        self.vn1_vm1_vrouter_fixture = self.useFixture(ComputeNodeFixture(
            self.connections,
            self.vn1_vm1_fixture.vm_node_ip))

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
    def set_flow_entries(cls, flow_entries):
        for compute_fixture in cls.compute_fixtures:
            compute_fixture.add_vrouter_module_params(
                {'vr_flow_entries': str(flow_entries)}, reload_vrouter=True)
            print(compute_fixture.read_vrouter_module_params())

    @classmethod
    def add_flow_cache_timeout(cls, flow_timeout):
        # Add flow_cache_timeout in all the computes
        for cmp_fix in cls.compute_fixtures:
            cmp_fix.set_flow_aging_time(flow_timeout)

    @classmethod
    def preconfig(cls):
        flow_entries = 1024 * 1024
        flow_timeout = 9999
        cls.set_flow_entries(flow_entries)
        cls.add_flow_cache_timeout(flow_timeout)

        
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
        # Create flows using hping
        destport = '++1000'
        baseport = '1000'
        count = 1024 * 1024
        interval = 'u100'
        hping_h = Hping3(self.vn1_vm1_fixture,
                         self.vn1_vm2_fixture.vm_ip,
                         udp=True,
                         destport=destport,
                         baseport=baseport,
                         count=count,
                         interval=interval)
        hping_h.start(wait=True)
        # time.sleep(5)
        (stats, hping_log) = hping_h.stop()
        # time.sleep(5)
        self.logger.debug('Hping3 log : %s' % (hping_log))
        self.logger.info('Stats: %s'%(stats))

        flow_table = self.vn1_vm1_vrouter_fixture.get_flow_table()
        flow_count = flow_table.flow_count
        self.logger.info('Flow count: %s' % flow_count)
        import pdb
        pdb.set_trace()
        for baseport in range(5000, 5011): 
            hping_h = Hping3(self.vn1_vm1_fixture, self.vn1_vm2_fixture.vm_ip, udp=True, keep=True, destport=destport, baseport=baseport, count=count, interval=interval)
            hping_h.start(wait=True)
            (stats, hping_log) = hping_h.stop()
        
        flow_table = self.vn1_vm1_vrouter_fixture.get_flow_table()
        flow_count = flow_table.flow_count
        self.logger.info('Flow count: %s' % flow_count)
        assert flow_count > 1000 * 1000, 'Flows less than 1 Million'

if __name__ == '__main__':
    TestFlowScale.setUpClass()

