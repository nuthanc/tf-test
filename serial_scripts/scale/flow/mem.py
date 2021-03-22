from subprocess import check_output
import os
import psutil
import paramiko

process = psutil.Process(os.getpid())
print(process.memory_info().rss)


def execute_cmds_on_remote(
        ip,
        cmd_list,
        stackrc_file=None,
        username='root',
        password='c0ntrail123'):
    output = ""
    error = ""
    client = paramiko.SSHClient()
    try:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=username, password=password)
    except BaseException:
        print("[!] Cannot connect to the SSH Server")
        exit()

    for cmd in cmd_list:
        if stackrc_file is not None:
            source_stackrc = 'source %s' % stackrc_file
            cmd = f"{source_stackrc};{cmd}"
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
    client.close()
    return output, error


cmd_list = ['top -b -n 1 -p $(pidof contrail-vrouter-agent)']
print(execute_cmds_on_remote(ip='10.204.216.99', cmd_list=cmd_list))
