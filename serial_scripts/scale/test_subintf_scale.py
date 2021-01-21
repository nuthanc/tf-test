from common.bgpaas.base import BaseBGPaaS
from tcutils.wrappers import preposttest_wrapper
from tcutils.util import *

class SubIntfScaleTest(BaseBGPaaS):

    @classmethod
    def setUpClass(cls):
        super(SubIntfScaleTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(SubIntfScaleTest, cls).tearDownClass()

    @preposttest_wrapper
    def test_subintf_scale(self):
        vn_name = get_random_name('scale_bgpaas_vn')
        vn_subnets = ['27.27.0.0/16']
        vn_fixture = self.create_vn(vn_name, vn_subnets)
        bgpaas_vm1 = self.create_vm(
            vn_fixture, 'bgpaas_vm1', image_name='ubuntu-bird')
        port1 = bgpaas_vm1.vmi_ids[bgpaas_vm1.vn_fq_name]
        assert bgpaas_vm1.wait_till_vm_is_up()
        address_families = ['inet', 'inet6']
        gw_ip = vn_fixture.get_subnets()[0]['gateway_ip']
        dns_ip = vn_fixture.get_subnets()[0]['dns_server_address']
        neighbors = [gw_ip, dns_ip]
        self.logger.info('Configuring BGP on the bird-vm')
        static_routes = [{"network": "0.0.0.0/0", "nexthop": "blackhole"}]
        autonomous_system = 63527
        cluster_local_autonomous_system = 64512
        bgpaas_fixture = self.create_bgpaas(
            bgpaas_shared=True, autonomous_system=autonomous_system,
            bgpaas_ip_address=bgpaas_vm1.vm_ip,
            local_autonomous_system=cluster_local_autonomous_system)
        self.attach_vmi_to_bgpaas(port1, bgpaas_fixture)
        self.config_bgp_on_bird(
            bgpaas_vm=bgpaas_vm1,
            local_ip=bgpaas_vm1.vm_ip,
            neighbors=neighbors,
            peer_as=cluster_local_autonomous_system,
            local_as=autonomous_system,
            static_routes=static_routes)
        ret = bgpaas_fixture.verify_in_control_node(bgpaas_vm1)
        if ret:
            self.logger.info("BGP Session is established with Control node")
        else:
            assert False, "BGP Session is not established with Control node"
        import pdb;pdb.set_trace()

    # def config_bgp_on_bird(self):
    #     pass

