### Test flows up to 1 Million

```sh
python3 serial_scripts/scale/flow/test_flow.py
python3 -m testtools.run serial_scripts.scale.flow.test_flow.TestFlowScale.test_flow_scale
```

### Hping3 

* https://linux.die.net/man/8/hping3

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
sudo timeout 5 hping3 216.111.78.132 -s 1000 -p ++2000 -S --count 10 -V --flood
hping3  --syn   --destport ++1000  --baseport 1000  --count 10  --flood   216.111.78.132
hping3  --syn   --destport ++1000  --baseport 1000  --count 10  --flood   216.111.78.129
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

### hping3 tcp traffic test case

```sh
'hping3  --syn   --destport 22  --baseport 1000  --count 1000  --interval u10000  54.241.53.68 1>/tmp/hping_ctest-random-23513339.log 2>/tmp/hping_ctest-random-23513339.result'
```
* Commands that gave output
```sh
hping3  --syn   --destport 22  --baseport 1004  --count 5  --interval u10000  54.241.53.68

HPING 54.241.53.68 (eth0 54.241.53.68): S set, 40 headers + 0 data bytes
len=44 ip=54.241.53.68 ttl=64 DF id=0 sport=22 flags=SA seq=0 win=14600 rtt=1.7 ms
len=44 ip=54.241.53.68 ttl=64 DF id=0 sport=22 flags=SA seq=1 win=14600 rtt=1.4 ms
len=44 ip=54.241.53.68 ttl=64 DF id=0 sport=22 flags=SA seq=2 win=14600 rtt=1.4 ms
len=44 ip=54.241.53.68 ttl=64 DF id=0 sport=22 flags=SA seq=3 win=14600 rtt=1.4 ms
len=44 ip=54.241.53.68 ttl=64 DF id=0 sport=22 flags=SA seq=4 win=14600 rtt=1.4 ms

--- 54.241.53.68 hping statistic ---
5 packets transmitted, 5 packets received, 0% packet loss
round-trip min/avg/max = 1.4/1.5/1.7 ms
```
* interval: default is to wait one second between each packet
  * u10000. Hping will send 10 packets for second
```sh
hping3  --syn   --destport 1000  --baseport 1009  --count 5  --interval u10000  54.241.53.68
HPING 54.241.53.68 (eth0 54.241.53.68): S set, 40 headers + 0 data bytes
len=40 ip=54.241.53.68 ttl=64 DF id=0 sport=1000 flags=RA seq=0 win=0 rtt=2.0 ms
len=40 ip=54.241.53.68 ttl=64 DF id=0 sport=1000 flags=RA seq=1 win=0 rtt=1.5 ms
len=40 ip=54.241.53.68 ttl=64 DF id=0 sport=1000 flags=RA seq=2 win=0 rtt=1.4 ms
len=40 ip=54.241.53.68 ttl=64 DF id=0 sport=1000 flags=RA seq=3 win=0 rtt=1.4 ms
len=40 ip=54.241.53.68 ttl=64 DF id=0 sport=1000 flags=RA seq=4 win=0 rtt=1.5 ms

--- 54.241.53.68 hping statistic ---
5 packets transmitted, 5 packets received, 0% packet loss
round-trip min/avg/max = 1.4/1.6/2.0 ms
```
* 68 is another VM and not the gateway

```sh
hping3  --syn   --destport ++1000  --baseport 1025  --count 5  --interval u10000  54.241.53.68
HPING 54.241.53.68 (eth0 54.241.53.68): S set, 40 headers + 0 data bytes
len=40 ip=54.241.53.68 ttl=64 DF id=0 sport=1000 flags=RA seq=0 win=0 rtt=2.0 ms
len=40 ip=54.241.53.68 ttl=64 DF id=0 sport=1001 flags=RA seq=1 win=0 rtt=1.5 ms
len=40 ip=54.241.53.68 ttl=64 DF id=0 sport=1002 flags=RA seq=2 win=0 rtt=1.5 ms
len=40 ip=54.241.53.68 ttl=64 DF id=0 sport=1003 flags=RA seq=3 win=0 rtt=1.6 ms
len=40 ip=54.241.53.68 ttl=64 DF id=0 sport=1004 flags=RA seq=4 win=0 rtt=1.4 ms

--- 54.241.53.68 hping statistic ---
5 packets transmitted, 5 packets received, 0% packet loss
```

```sh
hping3  --udp   --destport ++5000  --baseport 1196  --count 10  --interval u10000  54.241.53.68
HPING 54.241.53.68 (eth0 54.241.53.68): udp mode set, 28 headers + 0 data bytes
ICMP Port Unreachable from ip=54.241.53.68 get hostname...
--- 54.241.53.68 hping statistic ---
10 packets transmitted, 0 packets received, 100% packet loss
round-trip min/avg/max = 0.0/0.0/0.0 ms
```
* Flows do get created for the above even though it says packet loss

### Important observations

* Upon sending tcp traffic, there is more flows created in destination vm's node
* There is no flow created at all in the source vm's node when tcp traffic is sent
* With udp traffic, flows are seen on source vm's node