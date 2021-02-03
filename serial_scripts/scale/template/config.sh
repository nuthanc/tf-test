echo "configure
delete interfaces ge-0/0/0 unit 0 dhcp
load merge /root/junos_config.txt
run show configuration security | display set | save security_orig_conf
delete security
set security policies from-zone trust to-zone trust policy default-pol match source-address any
set security policies from-zone trust to-zone trust policy default-pol match destination-address any
set security policies from-zone trust to-zone trust policy default-pol match application any
set security policies from-zone trust to-zone trust policy default-pol then permit
set security zones security-zone trust interface ge-0/0/0.0 host-inbound-traffic system-services all
set security zones security-zone trust interface ge-0/0/0.0 host-inbound-traffic protocols all
commit" | /usr/sbin/cli