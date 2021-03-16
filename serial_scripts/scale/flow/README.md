### Test flows up to 1 Million

```sh
python3 serial_scripts/scale/flow/test_flow.py
```

### Helper files to learn about hping

```sh
export MX_GW_TEST=0
python3 -m testtools.run serial_scripts.vrouter.test_flow_scenarios.TCPFlowEvictionTests.test_hping3_tcp_traffic_for_eviction
```