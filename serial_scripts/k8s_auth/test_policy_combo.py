from common.k8s.base import BaseK8sTest
from tcutils.kubernetes.auth.example_user import ExampleUser
from tcutils.kubernetes.auth.resource_util import ResourceUtil
from common.contrail_test_init import ContrailTestInit
from tcutils.kubernetes.auth import create_policy
from tcutils.wrappers import preposttest_wrapper


class TestPolicyCombo(BaseK8sTest):
    @classmethod
    def setUpClass(cls):
        # Create the required users, projects and domains
        cmd = 'kubectl config use-context juju-context'
        cti_obj = ContrailTestInit(input_file='contrail_test_input.yaml')
        cti_obj.run_cmd_on_server(server_ip=cti_obj.juju_server, username='root', password='c0ntrail123',
                                  issue_cmd=cmd)
        super(TestPolicyCombo, cls).setUpClass()
        # MSG Need to use existing resources to create Openstack objects, but first see what create_all is doing
        cls.admin = ExampleUser.admin()
        cls.admin.create_all(user_name='userD', password='c0ntrail123', role='Member',
                             project_name='userD_project', domain_name='userD_domain')
        cls.admin.create_all(user_name='userA', password='c0ntrail123', role='Member',
                             project_name='userA_project', domain_name='userA_domain')
        cls.admin.create_all(user_name='userB', password='c0ntrail123', role='Member',
                             project_name='userB_project', domain_name='userB_domain')
        cls.admin.create_all(user_name='userC', password='c0ntrail123', role='Member',
                             project_name='userC_project', domain_name='userC_domain')

        cmd = "kubectl create ns nuthan; kubectl create ns kirthan"
        out = cls.inputs.run_cmd_on_server(server_ip='192.168.7.29', username='root', password='c0ntrail123',
                                           issue_cmd=cmd)
        print(out)
        admin_policy = create_policy.get_admin_policy()
        userA_policy = create_policy.get_userA_policy()
        userB_policy = create_policy.get_userB_policy()
        userC_policy = create_policy.get_userC_policy()
        userD_policy = create_policy.get_userD_policy()
        policies = [admin_policy, userA_policy,
                    userB_policy, userC_policy, userD_policy]
        filename = create_policy.insert_policies_in_template_file(
            policies, 'all_in_one_policy.yaml')
        create_policy.apply_policies_and_check_in_config_map(
            policies, filename, cls.inputs)

    def parallel_cleanup(self):
        cmd = 'kubectl config use-context juju-context'
        self.inputs.run_cmd_on_server(server_ip=self.inputs.juju_server, username='root', password='c0ntrail123',
                                      issue_cmd=cmd)
        try:
            namespace = self.namespace
        except: 
            namespace = 'default'
        for resource in self.resource_expectation:
            ResourceUtil.exec_kubectl_cmd_on_file(verb='delete', template_file=ResourceUtil.templates[resource], namespace=namespace)

    @preposttest_wrapper
    def test_only_pods_and_deployments_create(self):
        '''
        For userA user, only create pods and deployments and nothing else
        '''
        print("\n"+self.id())
        print("For userA user, only create pods and deployments and nothing else")
        self.stackrc_dict = {
            'user_name': 'userA',
            'password': 'c0ntrail123',
            'project_name': 'userA_project',
            'domain_name': 'userA_domain',
            'auth_url': self.__class__.admin.auth_url
        }
        # MSG Replace every resource_expectation_list with just resource_expectation
        # resource_expectation_list = ['pod-expected', 'deployment-expected', 'service', 'namespace',
        #                              'network_attachment_definition', 'network_policy', 'ingress', 'daemonset']
        self.resource_expectation = {'pod': True, 'deployment': True}
        ResourceUtil.perform_operations(
            stackrc_dict=self.stackrc_dict, resource_expectation=self.resource_expectation)

    @preposttest_wrapper
    def test_only_pods_and_deployments_delete(self):
        '''
        For userB user, only delete pods and deployments and nothing else
        '''
        print("\n"+self.id())
        print("\nFor userB user, only delete pods and deployments and nothing else")
        self.stackrc_dict = {
            'user_name': 'userB',
            'password': 'c0ntrail123',
            'project_name': 'userB_project',
            'domain_name': 'userB_domain',
            'auth_url': self.__class__.admin.auth_url
        }
        # resource_expectation_list = ['pod-expected', 'deployment-expected', 'service', 'namespace',
        #                              'network_attachment_definition', 'network_policy', 'ingress', 'daemonset']
        self.resource_expectation = {'pod': True, 'deployment': True}
        ResourceUtil.perform_operations(
            stackrc_dict=self.stackrc_dict, resource_expectation=self.resource_expectation)

    @preposttest_wrapper
    def test_only_service_in_zomsrc_ns(self):
        '''
        For userC user, create service in zomsrc namespace and nothing else should work
        '''
        self.stackrc_dict = {
            'user_name': 'userC',
            'password': 'c0ntrail123',
            'project_name': 'userC_project',
            'domain_name': 'userC_domain',
            'auth_url': self.__class__.admin.auth_url
        }
        # resource_expectation_list = ['pod', 'deployment', 'service-expected', 'namespace',
        #                              'network_attachment_definition', 'network_policy', 'ingress', 'daemonset']
        self.resource_expectation = {'service': True}
        ResourceUtil.perform_operations(
            stackrc_dict=self.stackrc_dict, resource_expectation=self.resource_expectation)
        ResourceUtil.perform_operations(
            stackrc_dict=self.stackrc_dict, resource_expectation=self.resource_expectation, namespace='zomsrc')

    @preposttest_wrapper
    def test_only_pods_deployments_services_in_easy_ns(self):
        '''
        For userD user, any operation on pods, deployments and services but only in easy namespace
        '''
        self.stackrc_dict = {
            'user_name': 'userD',
            'password': 'c0ntrail123',
            'project_name': 'userD_project',
            'domain_name': 'userD_domain',
            'auth_url': self.__class__.admin.auth_url
        }
        
        self.resource_expectation = {
            'pod': True, 'deployment': True, 'service': True, 'namespace': True}
        self.namespace = 'easy'
        ResourceUtil.perform_operations(
            resource_expecation=self.resource_expectation, stackrc_dict=self.stackrc_dict)
        ResourceUtil.perform_operations(
            stackrc_dict=self.stackrc_dict, resource_expectation=self.resource_expectation, namespace=self.namespace)
