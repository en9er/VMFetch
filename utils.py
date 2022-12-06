import pexpect
import requests
import re
from vmfconfig import get_account_creds


def _get_vm_creds(jenkins_url):
    log = _fetch_console_log(jenkins_url)
    ip = re.findall(r'HostName (.*)', log)
    plain_pass = re.findall(r'PLAIN_PASSWD.: (.*)', log)
    if not ip or not plain_pass:
        print("VM ip or password not found")
        exit(-1)

    return ip[0], plain_pass[0]


def _fetch_console_log(jenkins_url) -> str:
    username, key = get_account_creds()
    print("Fetching jenkins data...")
    response = requests.post(jenkins_url, auth=(username, key))
    return response.text


def connect_vm(jenkins_url):
    vm_ip, vm_pass = _get_vm_creds(jenkins_url)
    connection = pexpect.spawn('/bin/bash', ['-c', f'ssh root@{vm_ip}'])
    connection.expect(r".*(yes/no/[fingerprint])?")
    connection.sendline(f"yes")
    connection.expect(r".*password:")
    connection.sendline(f"{vm_pass}")
    connection.sendline(f"source /root/rpm_tests_venv/bin/activate")
    connection.sendline(f"cd /vagrant")
    connection.interact()
