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

    @classmethod
    def set_flow_entries(cls):
        for compute_fixture in cls.compute_fixtures:
            compute_fixture.setup_vrouter_module_params(
                {'vr_flow_entries': str(1024 * 1024)})
            print(compute_fixture.read_vrouter_module_params)

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
