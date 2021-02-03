echo "configure
delete interfaces ge-0/0/0 unit 0 family inet dhcp
run show configuration security | display set | save security_orig_conf
delete security
load merge /root/junos_config.txt
commit" | /usr/sbin/cli