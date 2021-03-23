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
* ssh, telnet and icmp tcp will work
* Cause **session needs to be established** for the flow to stay, **otherwise** it will get **evicted**

### Sudhee's suggestion

* Flows delete -> Memory usage
* Flows add -> memory usage
* send traffic or leave for 20 minutes -> check changes in memory
* Start
```sh
top -b -n 1 -p $(pidof contrail-vrouter-agent); free -h
2021-03-22 13:16:14,262 - DEBUG - Output : top - 18:46:14 up 32 min,  1 user,  load average: 0.23, 0.19, 0.15^M
Tasks:   1 total,   0 running,   1 sleeping,   0 stopped,   0 zombie^M
%Cpu(s):  0.0 us,  0.0 sy,  0.0 ni,100.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st^M
KiB Mem : 26385580+total, 25413961+free,  8899740 used,   816448 buff/cache^M
KiB Swap:        0 total,        0 free,        0 used. 25412299+avail Mem ^M
^M
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND^M
 6598 root      20   0  720048 511824 352456 S   0.0  0.2   1:30.59 contrail-vroute^M
              total        used        free      shared  buff/cache   available^M
Mem:           251G        8.5G        242G         10M        797M        242G^M
```

* End
```sh
2021-03-22 17:24:57,960 - DEBUG - [10.204.216.99]: Running cmd : top -b -n 1 -p $(pidof contrail-vrouter-agent); free -h
2021-03-22 17:24:58,345 - DEBUG - Output : top - 22:54:58 up  4:41,  1 user,  load average: 0.53, 0.65, 0.70^M
Tasks:   1 total,   0 running,   1 sleeping,   0 stopped,   0 zombie^M
%Cpu(s):  0.3 us,  0.3 sy,  0.0 ni, 99.3 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st^M
KiB Mem : 26385580+total, 24859401+free, 14399368 used,   862428 buff/cache^M
KiB Swap:        0 total,        0 free,        0 used. 24862192+avail Mem ^M
^M
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND^M
 6595 root      20   0 6170824   5.7g 353192 S  20.0  2.3 249:26.69 contrail-vroute^M
              total        used        free      shared  buff/cache   available^M
Mem:           251G         13G        237G         10M        842M        237G^M
```

### New recording

* UDP flow count timings with 1us interval
  * 100,000 : 30s
  * 200,000 : 1m
  * 300,000 : 3m
  * 500,000 : 5m
  * 600,000 : 8m
  * 700,000 : 10m
  * 900,000 : 15m
  * 1,000,000: 20m
```sh
# Start
### Test flows up to 1 Million
DEBUG - [10.204.216.98]: Running cmd : top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h
2021-03-23 07:01:30,882 - DEBUG - Output : top - 12:31:30 up 18:18,  1 user,  load average: 0.34, 0.30, 0.25
Tasks:   1 total,   0 running,   1 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.0 us,  0.0 sy,  0.0 ni,100.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem : 26385580+total, 24964195+free, 13919112 used,   294732 buff/cache
KiB Swap:        0 total,        0 free,        0 used. 24912532+avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 6598 root      20   0 5676208   5.2g 353232 S  13.3  2.1 179:01.98 contrail-vroute
5471116
              total        used        free      shared  buff/cache   available
Mem:           251G         13G        238G         10M        287M        237G
Swap:            0B          0B          0B

DEBUG - [10.204.216.99]: Running cmd : top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h
2021-03-23 07:01:31,249 - DEBUG - Output : top - 12:31:31 up 18:17,  2 users,  load average: 0.30, 0.40, 0.53
Tasks:   1 total,   0 running,   1 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.2 us,  0.2 sy,  0.0 ni, 99.7 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem : 26385580+total, 24833764+free, 15236712 used,   281448 buff/cache
KiB Swap:        0 total,        0 free,        0 used. 24781398+avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 6595 root      20   0 6170824   5.7g 353288 S  13.3  2.3 371:09.07 contrail-vroute
5938604
              total        used        free      shared  buff/cache   available
Mem:           251G         14G        236G         10M        274M        236G
Swap:            0B          0B          0B
```

```sh
# End
Flow count: 1048668
2021-03-23 07:31:08,358 - DEBUG - [10.204.216.98]: Running cmd : top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h
2021-03-23 07:31:08,734 - DEBUG - Output : top - 13:01:08 up 18:47,  1 user,  load average: 0.58, 0.70, 0.64
Tasks:   1 total,   0 running,   1 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.3 us,  0.2 sy,  0.0 ni, 99.5 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem : 26385580+total, 24961878+free, 13911856 used,   325164 buff/cache
KiB Swap:        0 total,        0 free,        0 used. 24913270+avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 6598 root      20   0 5676208   5.2g 353236 S  26.7  2.1 192:05.05 contrail-vroute
5474496
              total        used        free      shared  buff/cache   available
Mem:           251G         13G        238G         10M        317M        237G
Swap:            0B          0B          0B


DEBUG - [10.204.216.98]: Running cmd : top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h
2021-03-23 07:31:09,120 - DEBUG - Output : top - 13:01:09 up 18:47,  1 user,  load average: 0.58, 0.70, 0.64
Tasks:   1 total,   0 running,   1 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.3 us,  0.2 sy,  0.0 ni, 99.5 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem : 26385580+total, 24961561+free, 13915016 used,   325164 buff/cache
KiB Swap:        0 total,        0 free,        0 used. 24912953+avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 6598 root      20   0 5676208   5.2g 353236 S  20.0  2.1 192:05.14 contrail-vroute
5474496
              total        used        free      shared  buff/cache   available
Mem:           251G         13G        238G         10M        317M        237G
Swap:            0B          0B          0B

DEBUG - [10.204.216.98]: Running cmd : top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h
2021-03-23 07:31:39,461 - DEBUG - Output : top - 13:01:39 up 18:48,  1 user,  load average: 0.70, 0.72, 0.64
Tasks:   1 total,   0 running,   1 sleeping,   0 stopped,   0 zombie
%Cpu(s):  1.5 us,  0.3 sy,  0.0 ni, 98.2 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem : 26385580+total, 24961574+free, 13914836 used,   325228 buff/cache
KiB Swap:        0 total,        0 free,        0 used. 24912969+avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 6598 root      20   0 5676208   5.2g 353236 S  66.7  2.1 192:15.73 contrail-vroute
5474496
              total        used        free      shared  buff/cache   available
Mem:           251G         13G        238G         10M        317M        237G
Swap:            0B          0B          0B

DEBUG - [10.204.216.98]: Running cmd : top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h
2021-03-23 07:32:09,803 - DEBUG - Output : top - 13:02:09 up 18:48,  1 user,  load average: 0.90, 0.76, 0.66
Tasks:   1 total,   0 running,   1 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.3 us,  0.2 sy,  0.0 ni, 99.5 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem : 26385580+total, 24961756+free, 13912936 used,   325304 buff/cache
KiB Swap:        0 total,        0 free,        0 used. 24913160+avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 6598 root      20   0 5676208   5.2g 353236 S  20.0  2.1 192:26.24 contrail-vroute
5474496
              total        used        free      shared  buff/cache   available
Mem:           251G         13G        238G         10M        317M        237G
Swap:            0B          0B          0B

DEBUG - [10.204.216.98]: Running cmd : top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h
2021-03-23 09:24:47,726 - DEBUG - Output : top - 14:54:47 up 20:41,  1 user,  load average: 0.22, 0.22, 0.22
Tasks:   1 total,   0 running,   1 sleeping,   0 stopped,   0 zombie
%Cpu(s):  1.6 us,  1.8 sy,  0.0 ni, 96.5 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem : 26385580+total, 24960019+free, 13920904 used,   334708 buff/cache
KiB Swap:        0 total,        0 free,        0 used. 24912353+avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 6598 root      20   0 5676208   5.2g 353700 S  26.7  2.1 230:22.19 contrail-vroute
5474960
              total        used        free      shared  buff/cache   available
Mem:           251G         13G        238G         10M        326M        237G
Swap:            0B          0B          0B

DEBUG - [10.204.216.98]: Running cmd : top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h
2021-03-23 09:24:47,726 - DEBUG - Output : top - 14:54:47 up 20:41,  1 user,  load average: 0.22, 0.22, 0.22
Tasks:   1 total,   0 running,   1 sleeping,   0 stopped,   0 zombie
%Cpu(s):  1.6 us,  1.8 sy,  0.0 ni, 96.5 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem : 26385580+total, 24960019+free, 13920904 used,   334708 buff/cache
KiB Swap:        0 total,        0 free,        0 used. 24912353+avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 6598 root      20   0 5676208   5.2g 353700 S  26.7  2.1 230:22.19 contrail-vroute
5474960
              total        used        free      shared  buff/cache   available
Mem:           251G         13G        238G         10M        326M        237G
Swap:            0B          0B          0B


DEBUG - [10.204.216.98]: Running cmd : top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h
2021-03-23 09:25:18,066 - DEBUG - Output : top - 14:55:18 up 20:41,  1 user,  load average: 0.14, 0.20, 0.21
Tasks:   1 total,   0 running,   1 sleeping,   0 stopped,   0 zombie
%Cpu(s):  1.3 us,  2.0 sy,  0.0 ni, 96.7 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem : 26385580+total, 24959990+free, 13921140 used,   334752 buff/cache
KiB Swap:        0 total,        0 free,        0 used. 24912329+avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 6598 root      20   0 5676208   5.2g 353700 S  33.3  2.1 230:32.29 contrail-vroute
5474960
              total        used        free      shared  buff/cache   available
Mem:           251G         13G        238G         10M        326M        237G
Swap:            0B          0B          0B


DEBUG - [10.204.216.98]: Running cmd : top -b -n 1 -p $(pidof contrail-vrouter-agent);cat /proc/$(pidof contrail-vrouter-agent)/status | grep VmRSS | awk '{print $2}'; free -h
2021-03-23 09:25:48,416 - DEBUG - Output : top - 14:55:48 up 20:42,  1 user,  load average: 0.08, 0.18, 0.21
Tasks:   1 total,   0 running,   1 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.5 us,  0.2 sy,  0.0 ni, 99.3 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem : 26385580+total, 24960072+free, 13920284 used,   334800 buff/cache
KiB Swap:        0 total,        0 free,        0 used. 24912412+avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 6598 root      20   0 5676208   5.2g 353700 S  33.3  2.1 230:42.50 contrail-vroute
5474960
              total        used        free      shared  buff/cache   available
Mem:           251G         13G        238G         10M        326M        237G
Swap:            0B          0B          0B
```