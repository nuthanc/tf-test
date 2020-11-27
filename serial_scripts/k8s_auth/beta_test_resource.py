# from common.k8s.base import BaseK8sTest
from tcutils.kubernetes.auth import create_policy
from tcutils.kubernetes.auth.example_user import ExampleUser
from tcutils.kubernetes.auth.resource_util import ResourceUtil
import os


# If nothing is mentioned in the resource verbs, then all operations are permitted for that particular resource
# If no match is provided, then it is admin_policy with everything enabled in resource

# MSG Check this restart sceanario
class BetaTestResource():
    def all_operations_for_admin_project_domain_with_kube_manager_restart(self):
        stackrc_dict = ResourceUtil.admin_stackrc()
        resource_expectation_list = ['pod-expected', 'deployment-expected', 'service-expected', 'namespace-expected',
                                     'network_attachment_definition-expected', 'network_policy-expected', 'ingress-expected', 'daemonset-expected']
        ResourceUtil.create_policy_and_perform_operations(
            resource_expectation_list=resource_expectation_list, stackrc_dict=stackrc_dict)
        handle = BaseK8sTest()
        handle.restart_kube_manager()
        resource_expectation_list = ['pod-expected', 'deployment-expected', 'service-expected', 'namespace-expected',
                                     'network_attachment_definition-expected', 'network_policy-expected', 'ingress-expected', 'daemonset-expected']
        ResourceUtil.create_policy_and_perform_operations(
            resource_expectation_list=resource_expectation_list, stackrc_dict=stackrc_dict)

    def all_operations_for_admin_project_domain_with_agent_restart(self):
        stackrc_dict = ResourceUtil.admin_stackrc()
        resource_expectation_list = ['pod-expected', 'deployment-expected', 'service-expected', 'namespace-expected',
                                     'network_attachment_definition-expected', 'network_policy-expected', 'ingress-expected', 'daemonset-expected']
        ResourceUtil.create_policy_and_perform_operations(
            resource_expectation_list=resource_expectation_list, stackrc_dict=stackrc_dict)
        self.restart_vrouter_agent()
        resource_expectation_list = ['pod-expected', 'deployment-expected', 'service-expected', 'namespace-expected',
                                     'network_attachment_definition-expected', 'network_policy-expected', 'ingress-expected', 'daemonset-expected']
        ResourceUtil.create_policy_and_perform_operations(
            resource_expectation_list=resource_expectation_list, stackrc_dict=stackrc_dict)

    def all_operations_for_custom_user_project_domain_with_kube_manager_restart(self):
        match, stackrc_dict = ResourceUtil.create_test_user_openstack_objects_and_return_match_list_and_stackrc_dict()
        resource_expectation_list = ['pod-expected', 'deployment-expected', 'service-expected', 'namespace-expected',
                                     'network_attachment_definition-expected', 'network_policy-expected', 'ingress-expected', 'daemonset-expected']
        ResourceUtil.create_policy_and_perform_operations(
            match=match, resource_expectation_list=resource_expectation_list, stackrc_dict=stackrc_dict)
        self.restart_kube_manager()
        resource_expectation_list = ['pod-expected', 'deployment-expected', 'service-expected', 'namespace-expected',
                                     'network_attachment_definition-expected', 'network_policy-expected', 'ingress-expected', 'daemonset-expected']
        ResourceUtil.create_policy_and_perform_operations(
            match=match, resource_expectation_list=resource_expectation_list, stackrc_dict=stackrc_dict)

    def all_operations_for_custom_user_project_domain_with_agent_restart(self):
        match, stackrc_dict = ResourceUtil.create_test_user_openstack_objects_and_return_match_list_and_stackrc_dict()
        resource_expectation_list = ['pod-expected', 'deployment-expected', 'service-expected', 'namespace-expected',
                                     'network_attachment_definition-expected', 'network_policy-expected', 'ingress-expected', 'daemonset-expected']
        ResourceUtil.create_policy_and_perform_operations(
            match=match, resource_expectation_list=resource_expectation_list, stackrc_dict=stackrc_dict)
        self.restart_vrouter_agent()
        resource_expectation_list = ['pod-expected', 'deployment-expected', 'service-expected', 'namespace-expected',
                                     'network_attachment_definition-expected', 'network_policy-expected', 'ingress-expected', 'daemonset-expected']
        ResourceUtil.create_policy_and_perform_operations(
            match=match, resource_expectation_list=resource_expectation_list, stackrc_dict=stackrc_dict)

    def pod_with_all_operations_for_custom_user_project_domain_with_kube_manager_restart(self):
        # import pdb;pdb.set_trace()
        resource = {'resources': ['pods']}
        match, stackrc_dict = ResourceUtil.create_test_user_openstack_objects_and_return_match_list_and_stackrc_dict()
        resource_expectation_list = ['pod-expected', 'deployment', 'service', 'namespace',
                                     'network_attachment_definition', 'network_policy', 'ingress', 'daemonset']
        ResourceUtil.create_policy_and_perform_operations(
            resource=resource, match=match, stackrc_dict=stackrc_dict, resource_expectation_list=resource_expectation_list)
        self.restart_kube_manager()
        ResourceUtil.create_policy_and_perform_operations(
            resource=resource, match=match, stackrc_dict=stackrc_dict, resource_expectation_list=resource_expectation_list)

    def pod_with_all_operations_for_custom_user_project_domain_with_agent_restart(self):
        # import pdb;pdb.set_trace()
        resource = {'resources': ['pods']}
        match, stackrc_dict = ResourceUtil.create_test_user_openstack_objects_and_return_match_list_and_stackrc_dict()
        resource_expectation_list = ['pod-expected', 'deployment', 'service', 'namespace',
                                     'network_attachment_definition', 'network_policy', 'ingress', 'daemonset']
        ResourceUtil.create_policy_and_perform_operations(
            resource=resource, match=match, stackrc_dict=stackrc_dict, resource_expectation_list=resource_expectation_list)
        self.restart_vrouter_agent()
        ResourceUtil.create_policy_and_perform_operations(
            resource=resource, match=match, stackrc_dict=stackrc_dict, resource_expectation_list=resource_expectation_list)

# b = BetaTestResource()
# b.all_operations_for_admin_project_domain_with_kube_manager_restart()




ResourceUtil.execute_cmds_on_remote(
    '192.168.7.29', ['sudo docker restart contrailkubernetesmaster_kubemanager_1'])
