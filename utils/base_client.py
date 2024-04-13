import os

from dotenv import load_dotenv, find_dotenv
from paramiko import SSHClient
from paramiko import SSHException

_ = load_dotenv((find_dotenv()))


class BaseACIClient:
    """
    This class is for interacting with the Cisco ACI API
    """

    def __init__(self):
        self.apic = os.getenv('APIC')
        self.apic_username = os.getenv('APIC_USERNAME')
        self.apic_password = os.getenv('APIC_PASSWORD')
        self.ssh_client = None
        self.cmd_output = None

    def initiate_ssh_session(self):
        self.ssh_client = SSHClient()
        print("Initializing SSH Session...")
        self.ssh_client.load_system_host_keys()
        self.ssh_client.connect(hostname=self.apic, port=2222, username=self.apic_username, password=self.apic_password)
        return self.ssh_client

    def send_cmd(self, cmd):
        # print(f"Sending cmd: {cmd}")
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
            self.cmd_output = stdout.read().decode()
        except SSHException:
            self.close_session()
        return self.cmd_output

    def close_session(self):
        return self.ssh_client.close()
