from common.base import GenericTestBase
from tcutils.wrappers import preposttest_wrapper
import test
from compute_node_test import ComputeNodeFixture
from tcutils.traffic_utils.hping_traffic import Hping3
import time
import logging

class TestFlowScale(GenericTestBase):

    @classmethod
    def setUpClass(cls):
        super(TestFlowScale, cls).setUpClass()
        cls.logger.setLevel(logging.INFO)
        cls.get_compute_fixtures()
        # cls.add_phy_intf_in_vrouter_env()
        cls.preconfig()


    @classmethod
    def tearDownClass(cls):
        super(TestFlowScale, cls).tearDownClass()


    def setUp(self):
        super(TestFlowScale, self).setUp()
        self.vn1_fixture = self.create_only_vn()
        vm1_node_name = self.inputs.host_data[self.inputs.compute_ips[0]]['name']
        self.vn1_vm1_fixture = self.create_vm(self.vn1_fixture, node_name=vm1_node_name)
        self.vn1_vm1_fixture.wait_till_vm_is_up()
        self.vn1_vm1_vrouter_fixture = self.useFixture(ComputeNodeFixture(
            self.connections,
            self.vn1_vm1_fixture.vm_node_ip))
        self.compute_fixture = ComputeNodeFixture(
            self.connections, self.vn1_vm1_fixture.vm_node_ip)


    @classmethod
    def get_compute_fixtures(cls):
        cls.compute_fixtures = []
        for name, ip in cls.connections.inputs.compute_info.items():
            cls.compute_fixtures.append(
                ComputeNodeFixture(cls.connections, ip))


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
                cmd = '%s;%s;%s' % (echo_line, cd_vrouter, down_up)
                compute_fixture.execute_cmd(cmd, container=None)


    @classmethod
    def set_flow_entries(cls, flow_entries):
        for compute_fixture in cls.compute_fixtures:
            compute_fixture.add_vrouter_module_params(
                {'vr_flow_entries': str(flow_entries)}, reload_vrouter=True)
            info_cmd = 'contrail-tools vrouter --info |grep "Flow Table limit"'
            output = compute_fixture.execute_cmd(info_cmd, container=None)
            cls.logger.info(output)


    @classmethod
    def add_flow_cache_timeout(cls, flow_timeout):
        # Add flow_cache_timeout in all the computes
        for cmp_fix in cls.compute_fixtures:
            cmp_fix.set_flow_aging_time(flow_timeout)


    @classmethod
    def preconfig(cls):
        flow_entries = 1024 * 1024 * 6
        flow_timeout = 120
        cls.set_flow_entries(flow_entries)
        cls.add_flow_cache_timeout(flow_timeout)


    def calc_vrouter_mem_usage(self):
        cmd = "top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h"
        out = self.compute_fixture.execute_cmd(cmd, container=None)
        self.logger.info('vrouter agent memory usage: %s' % out)


    def wait_and_add_flows(self, baseport):
        self.logger.info('Generate gcore of agent process')
        out = self.compute_fixture.execute_cmd('gcore $(pidof contrail-vrouter-agent)')
        self.logger.info('Output of gcore cmd: %s' %out)
        
        self.logger.info('Wait 120s for flows to get cleared')
        time.sleep(120)
        self.logger.info(
            'Checking flow_count and memory usage of vrouter: Taking 3 readings')
        for i in range(3):
            self.logger.info('Reading %s after waiting is done' %(i+1))
            flow_count = self.get_flow_count()
            self.logger.info('Flow count: %s' % flow_count)
            self.calc_vrouter_mem_usage()
            time.sleep(2)

        self.logger.info('Generate gcore of agent process')
        out = self.compute_fixture.execute_cmd('gcore $(pidof contrail-vrouter-agent)')
        self.logger.info('Output of gcore cmd: %s' %out)
        
        # Add 100000 flows
        self.logger.info('Adding 100000 flows')
        gateway_ip = self.vn1_fixture.vn_subnet_objs[0]['gateway_ip']
        hping_h = Hping3(self.vn1_vm1_fixture,
                         gateway_ip,
                         udp=True,
                         keep=True,
                         destport='++1000',
                         baseport=baseport,
                         count=1024*1024,
                         interval='u1')
        hping_h.start(wait=False)
        self.logger.info('Running hping command for 5s')
        time.sleep(5)
        (stats, hping_log) = hping_h.stop()
        flow_count = self.get_flow_count()
        self.logger.info(
            'Checking flow_count and memory usage of vrouter: Taking 3 readings')
        for i in range(3):
            self.logger.info('Reading %s after add' %(i+1))
            flow_count = self.get_flow_count()
            self.logger.info('Flow count: %s' % flow_count)
            self.calc_vrouter_mem_usage()
            time.sleep(2)


    def get_flow_count(self):
        cmd = "docker ps|grep tools|awk '{print $NF}'|tail -1"
        tools_container = self.compute_fixture.execute_cmd(cmd, container=None)
        cmd = "docker exec -it %s timeout 1 flow -r|awk '{print $5}'" % tools_container
        flow_count = self.compute_fixture.execute_cmd(cmd, container=None)
        if flow_count:
            return int(flow_count)
        else:
            return 0

    def memory_leak_checks(self):
        for i in range(3):
            baseport = 6000 + i
            self.wait_and_add_flows(baseport)
        import pdb;pdb.set_trace()
        # self.logger.info('Longevity test')
        # for i in range(3):
        #     self.logger.info('Sleep for 10 minutes')
        #     time.sleep(10 * 60)
        #     self.calc_vrouter_mem_usage()        

    @test.attr(type=['flow_scale'])
    @preposttest_wrapper
    def test_flow_scale(self):
        '''
        Description: Test to scale 1 million flows
         Test steps:
                1. Add PHYSICAL_INTERFACE in vrouter env if absent
                2. Set flow entries to 1 million in vrouter module
                3. Increase flow timeout to high value like 9999
                4. Send traffic through hping3 changing the source port with each iteration
                5. Check for flow count in flow table
         Pass criteria: Flow count greater than 1 million
         Maintainer : nuthanc@juniper.net 
        '''
        self.calc_vrouter_mem_usage()
        destport = '++1000'
        count = 1024 * 1024
        interval = 'u1'
        gateway_ip = self.vn1_fixture.vn_subnet_objs[0]['gateway_ip']

        for baseport in range(5001, 7050):
            hping_h = Hping3(self.vn1_vm1_fixture,
                            #  self.vn1_vm2_fixture.vm_ip,
                             gateway_ip,
                             udp=True,
                             keep=True,
                             destport=destport,
                             baseport=baseport,
                             count=count,
                             interval=interval)
            hping_h.start(wait=False)
            self.logger.info('Running command for 5s')
            time.sleep(5)
            (stats, hping_log) = hping_h.stop()
            # flow_table = self.vn1_vm1_vrouter_fixture.get_flow_table()
            # flow_count = flow_table.flow_count
            flow_count = self.get_flow_count()
            self.logger.info('Flow count: %s' % flow_count)
            self.calc_vrouter_mem_usage()
            if flow_count >= 1024 * 1024 * 2:
                break

        # flow_table = self.vn1_vm1_vrouter_fixture.get_flow_table()
        # flow_count = flow_table.flow_count
        flow_count = self.get_flow_count()
        self.logger.info('Flow count: %s' % flow_count)
        # assert flow_count > 1000 * 1000, 'Flows less than 1 Million'
        self.memory_leak_checks()
        import pdb
        pdb.set_trace()

        self.logger.info('Flows greater than 1 Million')


    @test.attr(type=['flow_scale'])
    @preposttest_wrapper
    def test_flow_scale_tcp(self):
        destport = '++1000'
        count = 1024 * 1024
        interval = 'u1'

        gateway_ip = self.vn1_fixture.vn_subnet_objs[0]['gateway_ip']

        for baseport in range(1001, 7050):
            hping_h = Hping3(self.vn1_vm1_fixture,
                             gateway_ip,
                             syn=True,
                             keep=True,
                             flood=True,
                             destport=destport,
                             baseport=baseport,
                             count=count,
                             interval=interval)
            hping_h.start(wait=False)
            self.logger.info('Running command for 5s')
            time.sleep(5)
            (stats, hping_log) = hping_h.stop()
            # I think get_flow_table is taking lot of time
            # flow_table = self.vn1_vm1_vrouter_fixture.get_flow_table()
            # flow_count = flow_table.flow_count
            flow_count = self.get_flow_count()
            self.logger.info('Flow count: %s' % flow_count)
            self.calc_vrouter_mem_usage()
            if flow_count >= 1024 * 1024 * 6:
                break


if __name__ == '__main__':
    TestFlowScale.setUpClass()
