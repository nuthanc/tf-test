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
                cmd = '%s;%s;%s' % (echo_line, cd_vrouter, down_up)
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
                1. Add PHYSICAL_INTERFACE in vrouter env if absent
                2. Set flow entries to 1 million in vrouter module
                3. Increase flow timeout to high value like 9999
                4. Send traffic through hping3 changing the source port with each iteration
                5. Check for flow count in flow table
         Pass criteria: Flow count greater than 1 million
         Maintainer : nuthanc@juniper.net 
        '''
        destport = '++1000'
        count = 1024 * 1024
        interval = 'u1'
        cmd = "top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h"
        for compute_fixture in self.compute_fixtures:
            out = compute_fixture.execute_cmd(cmd, container=None)
            self.logger.info('vrouter agent memory usage: %s' % out)
        for baseport in range(5001, 5050):
            hping_h = Hping3(self.vn1_vm1_fixture,
                             self.vn1_vm2_fixture.vm_ip,
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
            flow_table = self.vn1_vm1_vrouter_fixture.get_flow_table()
            flow_count = flow_table.flow_count
            self.logger.info('Flow count: %s' % flow_count)
            if flow_count >= 1024 * 1000:
                break

        flow_table = self.vn1_vm1_vrouter_fixture.get_flow_table()
        flow_count = flow_table.flow_count
        self.logger.info('Flow count: %s' % flow_count)
        assert flow_count > 1000 * 1000, 'Flows less than 1 Million'
        cmd = "top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h"
        compute_fixture = self.compute_fixtures[0]
        out = compute_fixture.execute_cmd(cmd, container=None)
        self.logger.info('vrouter agent memory usage: %s' % out)
        self.memory_leak_checks()
        import pdb;pdb.set_trace()
        # Delete around 1000 flows
        # Check resident memory, it should decrease
        # Add 1000 flows
        # Resident memory should increase
        # Do delete and add around 3 times with required expectations
        # Leave the setup for 20 minutes, check the resident memory again
        self.logger.info('Flows greater than 1 Million')
    
    def memory_leak_checks(self):
        try: 
            compute_fixture = self.compute_fixtures[0]
            cmd = "top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h"
            res_mem_list = []
            for i in range(3):
                out = compute_fixture.execute_cmd(cmd, container=None)
                res_mem = out
                res_mem_list.append(res_mem)
                self.logger.info('Resident memory after %ss: %s' % (i*30, res_mem))
                time.sleep(30)
            l = len(res_mem_list)
            diff = res_mem_list[l-1] - res_mem_list[l-2]
            self.logger.info('Diff in last 2 resident memory: %s', diff)

            # Delete 10000 flows
            cmd = "for i in $(contrail-tools flow -l|grep ' <= >'|awk -F '<' '{print $1}'|head -n 10000); do contrail-tools flow -i $i; done"
            out = compute_fixture.execute_cmd(cmd, container=None)
            self.logger.info('Output of delete: %s' %out)
            import pdb;pdb.set_trace()
            cmd = "top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h"
            res_mem_list = []
            for i in range(3):
                out = compute_fixture.execute_cmd(cmd, container=None)
                res_mem = out
                res_mem_list.append(res_mem)
                self.logger.info('Resident memory after %ss: %s' % (i*30, res_mem))
                time.sleep(30)
            l = len(res_mem_list)
            diff = res_mem_list[l-1] - res_mem_list[l-2]
            self.logger.info('Diff in last 2 resident memory: %s', diff)
        except Exception as e:
            print('Exception:',e)
            import pdb;pdb.set_trace()

    # @test.attr(type=['flow_scale'])
    # @preposttest_wrapper
    # def test_flow_scale(self):
    #     gateway = self.vn1_fixture.vn_subnet_objs[0]['gateway_ip']


if __name__ == '__main__':
    TestFlowScale.setUpClass()
