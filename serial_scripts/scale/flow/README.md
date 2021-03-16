### Test flows up to 1 Million

```sh
python3 serial_scripts/scale/flow/test_flow.py
python3 -m testtools.run serial_scripts.scale.flow.test_flow.TestFlowScale.test_flow_scale
```

### Helper notes to learn about hping

* https://github.com/tungstenfabric/tf-test/blob/master/tcutils/traffic_utils/hping_traffic.py

```sh
export MX_GW_TEST=0
python3 -m testtools.run serial_scripts.vrouter.test_flow_scenarios.TCPFlowEvictionTests.test_hping3_tcp_traffic_for_eviction
```

```sh
sudo timeout 5 hping3 30.0.0.1 -s 1000<increment port for every run> -p ++1000 --udp --count 100 -V
# Can reduce count to 10

sudo timeout 5 hping3 30.0.0.1 -s 1000<increment port for every run> -p ++2000 -S --count 10 -V --flood

# Sending only Sync message in TCP(-S)
# count: send 100 packets to the destination
# if flood is not there, the rate at which the packets are sent is very slow
```
* timeout 5: run command for 5s and return
* source port 1000 and incrementing the destination port(till 64K)
* In 5 seconds, it will create 60k flows or something
* Again running after changing the source port to 1001
* Just modifying source port and destination port

### Gleanings from test_hping3

```sh
sudo: nohup hping3  --syn   --destport 22  --baseport 1000  --count 1000  --interval u10000  1.84.150.68 1>/tmp/hping_ctest-random-65645227.log 2>/tmp/hping_ctest-random-65645227.result &  echo $! > /tmp/hping_ctest-random-65645227.pid
```
* Equivalence of Aswani's command
  * -s : --baseport
  * -p : --destport
  * -S : --syn (syn=True)
  * -V : --verbose

### Requirements

* VM
  * Ubuntu-traffic image with flavor m1.large or above
  * Atleast 4vcpus, 8GB Ram, 10G HD
* 2 test cases:
  * TCP flow
  * UDP flow

### My logs

```sh
nohup hping3  --syn   --destport ++1000  --baseport 1000  --count 10  --flood   122.222.216.68 1>/tmp/hping_ctest-random-13845363.log 2>/tmp/hping_ctest-random-13845363.result &  echo $! > /tmp/hping_ctest-random-13845363.pid
```