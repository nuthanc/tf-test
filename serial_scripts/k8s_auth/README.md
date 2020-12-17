### Canonical JuJu Contrail CNI (K8S) Deployment Using Existing Keystone (CEM-13066)

* https://contrail-jws.atlassian.net/browse/CEM-13066
* Using keystone-auth to create k8s objects for Openstack Users

### To run tests
* Install kubectl and client-keystone-auth in juju server
* Configure keystone context to kubectl
* Clone tf-test to juju server and checkout to the branch required
* Test configuration in contrail_test_input needs to have juju_server as key
* The env_file contains the below environment variables
```sh
PYTHONPATH=/root/tf-test:/root/tf-test/fixtures
TEST_CONFIG_FILE=/root/tf-test/contrail_test_input.yaml
EMAIL_SUBJECT=Ubuntu-Keystone-sanity
MX_GW_TEST=1
PYTHON3=1
TEST_RUN_CMD=bash -x run_tests.sh -m -U -s -T auth
```
* Run test container with the below volumes
```sh
docker run --name nuthan_test --entrypoint /bin/bash --env-file /root/env_file -v /root/contrail_test_input.yaml:/root/tf-test/contrail_test_input.yaml -v /root/tf-test:/root/tf-test -v /root/.ssh:/root/.ssh --network=host -it bng-artifactory.juniper.net/contrail-nightly/contrail-test-test:2011.102
```