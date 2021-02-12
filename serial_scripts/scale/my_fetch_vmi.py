from vnc_api.vnc_api import *

vnc_lib = VncApi(api_server_host='10.204.216.103')
print(vnc_lib.virtual_machine_interface_read(id='9f15c311-08a6-4227-964c-0d5646eb59a1'))