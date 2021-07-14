### k8s Upgrade

* In contrail_test_input.yaml and instances.yaml from Jenkins, add  
```sh
python3 -m testtools.run scripts.k8s_scripts.test_pod.TestPod.test_ping_between_two_pods

docker exec $TEST_DOCKER bash -c "kill -10 $RUN_TEST_PID"
```

```sh
bash -x run_tests.sh -m -U -T k8s_upgrade

docker exec nuthan_test bash -c "ps -au | grep run_test | head -n 1" | awk -F ' ' '{print $2}' | grep -Eo '[0-9]{1,6}'

```