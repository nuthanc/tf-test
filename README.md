### k8s Upgrade

* In contrail_test_input.yaml and instances.yaml from Jenkins, add  
```sh
python3 -m testtools.run scripts.k8s_scripts.test_pod.TestPod.test_ping_between_two_pods

docker exec $TEST_DOCKER bash -c "kill -10 $RUN_TEST_PID"
```

```sh
bash -x run_tests.sh -m -U --k8s-upgrade
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

### Errors

* Check mylist
```sh
 [[ -n '' ]]
+ [[ ! -z '' ]]
+ '[' -z ']'
+ '[' '!' -z upgrade ']'
+ testrargs+=upgrade
+ export TAGS=upgrade
+ TAGS=upgrade
+ [[ ! -z upgrade ]]
+ run_tests
+ testr_init
+ '[' '!' -d .testrepository ']'
+ /usr/local/bin/testr init
+ find . -type f -name '*.pyc' -delete
+ export PYTHONPATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/contrail-test:/contrail-test/fixtures:/contrail-test/scripts
+ PYTHONPATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/contrail-test:/contrail-test/fixtures:/contrail-test/scripts
+ export OS_TEST_PATH=./scripts/
+ OS_TEST_PATH=./scripts/
+ export DO_XMPP_CHECK=1
+ DO_XMPP_CHECK=1
+ '[' '!' -d ./scripts/ ']'
+ '[' 1 -eq 1 ']'
+ '[' upgrade = '' ']'
+ run_tagged_tests_in_debug_mode
+ list_tagged_tests
+ /usr/local/bin/testr list-tests
+ grep upgrade
+ /usr/bin/python3 tools/parse_test_file.py mylist
+ IFS='
'
+ read -d '' -r -a lines
+ count=1
+ for i in '"${lines[@]}"'
+ result_xml=result1.xml
+ (( count++ ))
+ '[' 1 -eq 1 ']'
+ pids[$count]=2369
+ wait_till_child_process_state 2369 stop
+ local pid=2369
+ local state=stop
+ true
+ [[ -f /proc/2369/status ]]
+ exec /usr/bin/python3 -m subunit.run scripts.dsnat.test_dsnat.TestDSNAT.test_dsnat_with_different_forwarding_mode
```

```sh
exec /usr/bin/python3 -m subunit.run scripts.ecmp.test_ecmp.TestMultiInlineSVC.test_svc_fate_sharing_in_2_multi_inline_svc_chains_transparent_in_net_in_net_nat


+ [[ -f /proc/2387/status ]]
+ break
+ for i in '"${lines[@]}"'
+ result_xml=result3.xml
+ (( count++ ))
+ '[' 1 -eq 1 ']'
+ pids[$count]=2405
+ wait_till_child_process_state 2405 stop
+ local pid=2405
+ local state=stop
+ true
+ [[ -f /proc/2405/status ]]
+ exec /usr/bin/python3 -m subunit.run scripts.ecmp.test_ecmp.TestMultiInlineSVC.test_svc_fate_sharing_in_2_multi_inline_svc_chains_transparent_in_net_in_net_nat
+ /usr/local/bin/subunit2junitxml -f -o result3.xml
++ cat /proc/2405/task/2405/children
+ for cpid in '$(cat /proc/$pid/task/$pid/children)'
+ wait_till_process_state 2406 stop 0
+ local pid=2406
+ local state=stop
+ local wait=0
+ true
+ [[ -f /proc/2406/status ]]
++ grep State
++ cat /proc/2406/status
+ [[ State:	R (running) != *stop* ]]
+ '[' 0 -eq 1 ']'
+ return 1
+ for cpid in '$(cat /proc/$pid/task/$pid/children)'
+ wait_till_process_state 2408 stop 0
+ local pid=2408
+ local state=stop
+ local wait=0
+ true
+ [[ -f /proc/2408/status ]]
++ cat /proc/2408/status
++ grep State
+ [[ State:	R (running) != *stop* ]]
+ '[' 0 -eq 1 ']'
+ return 1
+ sleep 30
```