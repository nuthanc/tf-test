### k8s Upgrade

* In contrail_test_input.yaml and instances.yaml from Jenkins, add  
```sh
python3 -m testtools.run scripts.k8s_scripts.test_pod.TestPod.test_ping_between_two_pods

docker exec $TEST_DOCKER bash -c "kill -10 $RUN_TEST_PID"
```

```sh
bash -x run_tests.sh -m -U --k8s_upgrade
2021-07-14 06:33:04,114 - INFO - UPGRADE: test_ping_between_two_pods[1541]: Stopping self

docker exec nuthan_test bash -c "ps -aux"
docker exec nuthan_test bash -c "ps -au | grep run_test | head -n 1" | awk -F ' ' '{print $2}' | grep -Eo '[0-9]{1,6}'
docker exec nuthan_test bash -c "ps -q 1136 -o state --no-headers"

TEST_DOCKER=`docker ps --format '{{.Names}}' | grep test`
echo "Test Docker Name:- $TEST_DOCKER"
RUN_TEST_PID=`docker exec $TEST_DOCKER bash -c "ps -au | grep run_test | head -n 1" | awk -F ' ' '{print $2}' | grep -Eo '[0-9]{1,6}'`
echo "PID of run_test parent process running inside the test docker:- $RUN_TEST_PID"
docker exec $TEST_DOCKER bash -c "kill -10 $RUN_TEST_PID"
echo "Reached end of trigger_upgrade_tests."
```

### Working logs

* Check test_ping.log
```sh
# Logs after wait
docker exec $TEST_DOCKER bash -c "ps -ef"
UID        PID  PPID  C STIME TTY          TIME CMD
root         1     0  0 Jul13 pts/0    00:00:00 /bin/bash
root       169     1  0 06:24 ?        00:00:00 ssh-agent
root      1541     1  0 06:32 pts/0    00:00:04 /usr/bin/python3 -m subunit.run discover -t ./ ./scripts/ --load-list /tmp/tmpkun10cqs
root      1615     0  0 06:40 pts/1    00:00:00 bash
root      1699     0  0 07:08 pts/3    00:00:00 bash
root      4226     1  0 11:54 pts/0    00:00:00 bash -x run_tests.sh -m -U --k8s_upgrade
root      4632  4226  0 11:54 pts/0    00:00:00 bash -x run_tests.sh -m -U --k8s_upgrade
root      4633  4632  2 11:54 pts/0    00:00:04 /usr/bin/python3 -m subunit.run scripts.k8s_scripts.test_pod.TestPod.test_ping_between_two_pods
root      4635  4632  0 11:54 pts/0    00:00:00 /usr/bin/python3 /usr/local/bin/subunit2junitxml -f -o result1.xml
root      4662  4226  0 11:55 pts/0    00:00:00 bash -x run_tests.sh -m -U --k8s_upgrade
root      4663  4662  3 11:55 pts/0    00:00:04 /usr/bin/python3 -m subunit.run scripts.k8s_scripts.test_pod.TestPodVNIsolated.test_ping_between_two_pods
root      4664  4662  0 11:55 pts/0    00:00:00 /usr/bin/python3 /usr/local/bin/subunit2junitxml -f -o result2.xml
root      4692     0  2 11:57 ?        00:00:00 ps -ef
```

```sh
[root@nodea4 contrail-test]# cat mylist
scripts.k8s_scripts.test_pod.TestPod.test_ping_between_two_pods
scripts.k8s_scripts.test_pod.TestPodVNIsolated.test_ping_between_two_pods
```

### Explanation

* 0 is true in bash and everything else like 1 is false
* wait_till_child_process_state of "bash -x run_tests.sh -m -U --k8s_upgrade" becomes stopped
* wait_till_process_state is checking for when child processes(4633 amd 4635) become Stopped state
* I think in run_tagged_tests_in_debug_mode, exec of python subunit creates a new process of bash ...k8s_upgrade and children python3 subunit ...two_pods