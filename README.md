# Sub-intf scale automation using Ritam's scripts

* Scaling repo link: https://github.com/nuthanc/scaling/blob/sub_intf/README.md
* Changes for this:
  * serial_scripts/solution/test_orange_solution.py
  * serial_scripts/solution/topology/mini_deployment/template/vsrx.yaml
```sh
python3 serial_scripts/solution/test_orange_solution.py
```
```py
@classmethod
    def setup_vsrx(cls):
        #Create vSRX with sub-interfaces
        cls.vsrx_template_file=cls.deploy_path+"template/vsrx.yaml"
        with open(cls.vsrx_template_file, 'r') as fd:
            cls.vsrx_template = yaml.load(fd, Loader=yaml.FullLoader)

        for each_resource in cls.vsrx_template['resources']:
            if 'personality' in cls.vsrx_template['resources']\
                                    [each_resource]['properties']:
                inject_file='/config/junos-config/configuration.txt'
                fp1=open(cls.vsrx_template['resources'][each_resource]\
                                ['properties']['personality'][inject_file]\
                                ['get_file'], 'r')
                data=fp1.read()
                cls.vsrx_template['resources'][each_resource]['properties']\
                    ['personality'][inject_file]=data
                fp1.close()

        cls.vsrx_stack = HeatStackFixture(
                                connections=cls.connections,
                                stack_name=cls.connections.project_name+'_vsrx_scale',
                                template=cls.vsrx_template,
                                timeout_mins=15)
        cls.vsrx_stack.setUp()
```