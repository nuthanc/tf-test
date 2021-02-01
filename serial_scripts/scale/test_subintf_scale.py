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

    # @preposttest_wrapper
    # def test_subintf_scale_bird(self):
    #     vn_name = get_random_name('scale_bgpaas_vn')
    #     vn_subnets = ['27.37.0.0/16']
    #     vn_fixture = self.create_vn(vn_name, vn_subnets)
    #     subnet_objects = vn_fixture.get_subnets()
    #     port1 = vn_fixture.create_port(
    #         vn_fixture.vn_id, subnet_id=subnet_objects[0]['id'], ip_address='27.37.47.57')
    #     bgpaas_vm1 = self.create_vm(
    #         vn_fixture, 'bgpaas_vm1', image_name='ubuntu-bird', port_ids=[port1['id']])
    #     port1 = bgpaas_vm1.vmi_ids[bgpaas_vm1.vn_fq_name]
    #     assert bgpaas_vm1.wait_till_vm_is_up()
    #     address_families = ['inet', 'inet6']
    #     gw_ip = vn_fixture.get_subnets()[0]['gateway_ip']
    #     dns_ip = vn_fixture.get_subnets()[0]['dns_server_address']
    #     neighbors = [gw_ip, dns_ip]
    #     self.logger.info('Configuring BGP on the bird-vm')
    #     static_routes = [{"network": "0.0.0.0/0", "nexthop": "blackhole"}]
    #     autonomous_system = 63527
    #     cluster_local_autonomous_system = 64512
    #     bgpaas_fixture = self.create_bgpaas(
    #         bgpaas_shared=True, autonomous_system=autonomous_system,
    #         bgpaas_ip_address=bgpaas_vm1.vm_ip,
    #         local_autonomous_system=cluster_local_autonomous_system)
    #     self.attach_vmi_to_bgpaas(port1, bgpaas_fixture)
    #     self.config_bgp_on_bird(
    #         bgpaas_vm=bgpaas_vm1,
    #         local_ip=bgpaas_vm1.vm_ip,
    #         neighbors=neighbors,
    #         peer_as=cluster_local_autonomous_system,
    #         local_as=autonomous_system,
    #         static_routes=static_routes)
    #     ret = bgpaas_fixture.verify_in_control_node(bgpaas_vm1)
    #     if ret:
    #         self.logger.info("BGP Session is established with Control node")
    #     else:
    #         assert False, "BGP Session is not established with Control node"
    #     import pdb;pdb.set_trace()


    @preposttest_wrapper
    def test_subintf_scale(self):
        vn_name = get_random_name('scale_bgpaas_vn')
        vn_subnets = ['97.27.0.0/16']
        vn_fixture = self.create_vn(vn_name, vn_subnets)
        
        bgpaas_vm1 = self.create_vm(vn_fixture, 'bgpaas_vm1',
                                    image_name='vsrx')
        test_vm = self.create_vm(vn_fixture, 'test_vm',
                                 image_name='ubuntu-traffic')
        for i in range(5):
            bgpaas_vm1_state = bgpaas_vm1.wait_till_vm_is_up()
            if bgpaas_vm1_state:
               break
        autonomous_system1 = 64297
        bgpaas_fixture1 = self.create_bgpaas(
            bgpaas_shared=True, autonomous_system=autonomous_system1, bgpaas_ip_address=bgpaas_vm1.vm_ip)
        port1 = bgpaas_vm1.vmi_ids[bgpaas_vm1.vn_fq_name]
        address_families = ['inet', 'inet6']
        gw_ip = vn_fixture.get_subnets()[0]['gateway_ip']
        dns_ip = vn_fixture.get_subnets()[0]['dns_server_address']
        neighbors = [gw_ip, dns_ip]
        self.config_bgp_on_vsrx(src_vm=test_vm, dst_vm=bgpaas_vm1, bgp_ip=bgpaas_vm1.vm_ip, lo_ip=bgpaas_vm1.vm_ip,
                                address_families=address_families, autonomous_system=autonomous_system1, neighbors=neighbors, bfd_enabled=False)
        self.attach_vmi_to_bgpaas(port1, bgpaas_fixture1)
        self.addCleanup(self.detach_vmi_from_bgpaas,
                        port1, bgpaas_fixture1)
        ret = bgpaas_fixture1.verify_in_control_node(bgpaas_vm1)
        if ret:
            self.logger.info(
                "bgpaas_vm1: BGPaaS Session seen in the control-node")
        else:
            assert False, "bgpaas_vm1: BGPaaS Session not seen in the control-node"
        import pdb;pdb.set_trace()

# auto eth0.2
# iface eth0.2 inet static
# address 27.37.47.60/16


# auto eth1
# iface eth1 inet static
# address 27.37.47.59/16

# auto eth1.2
# iface eth1.2 inet static
# address 27.37.47.60/16

# ip link add link eth0 name eth0.2 type vlan id 2
# ip link set dev eth0.2 up
# ip addr add 27.37.47.60/16 dev eth0.2
