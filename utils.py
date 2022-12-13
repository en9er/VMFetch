import os
import signal
import shutil
import time

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

    return ip[-1], plain_pass[-1]


def _fetch_console_log(jenkins_url) -> str:
    username, key = get_account_creds()
    print("Fetching jenkins data...")
    response = requests.post(jenkins_url, auth=(username, key))
    return response.text


def get_term_size():
    ts = shutil.get_terminal_size()
    return ts.lines, ts.columns


def connect_vm(jenkins_url):
    def sigwinch_passthrough(sig, data):
        if not connection.closed:
            connection.setwinsize(*get_term_size())

    AGENT_REGKEY = os.environ.get('AGENT_REGISTER_KEY')
    vm_ip, vm_pass = _get_vm_creds(jenkins_url)
    print(f"Connecting to {vm_ip} host")
    connection = None
    try:
        connection = pexpect.spawn('/bin/bash', ['-c', f'ssh root@{vm_ip}'])
        connection.expect(r".*(yes/no/[fingerprint])?")
        connection.sendline(f"yes")
        connection.expect(r".* password:")
    except Exception:
        # host is in known hosts
        connection.sendline(f'ssh-keygen -f "/home/$USER/.ssh/known_hosts" -R {vm_ip}')
        connection.sendline(f'ssh root@{vm_ip}')
        connection.expect(r".*(yes/no/[fingerprint])?")
        connection.sendline(f"yes")
        connection.expect(r".*Permanently added.*")
        connection.expect(r".* password:")

    connection.setwinsize(*get_term_size())
    signal.signal(signal.SIGWINCH, sigwinch_passthrough)
    connection.sendline(f"{vm_pass}")

    if AGENT_REGKEY:
        # for some reason agent on rebuilt vms is not registered
        connection.sendline(f"imunify360-agent register {AGENT_REGKEY}")
    connection.sendline(f"source /root/rpm_tests_venv/bin/activate")
    connection.sendline(f"cd /vagrant")
    connection.interact()
