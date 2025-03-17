import re
import json
from netmiko import BaseConnection, ConnectHandler, NetmikoTimeoutException
from requests_toolbelt import MultipartEncoder
import requests

#cisco webex room ID and token ID
ROOMID = "Y2lzY29zcGFyazovL3VybjpURUFNOmV1LWNlbnRyYWwtMV9rL1JPT00vZTBjYzlmMzAtZWRmZC0xMWVmLThhMDQtMDVhN2ZkMjgxODQ5"
TOKEN = "Bearer OTk1NTI4NDYtZjM3Ny00ZDY0LWI3ZDUtOGQ1ZjM0ZjRiMzM2MjdlMjA2ZTQtNjM3_PE93_bde28e3d-21ec-426e-b7f1-1c7280ca363f"

#cisco log sample
log = "Feb 19 15:37:37 S1 %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/2, changed state to down"
log_s = "Feb 19 15:37:37 S1 %SPANTREE-6-ROOTCHANGE: Root bridge for VLAN 1 changed to 32768:00:1A:2B:3C:4D:5E"
log_n = "Feb 19 15:37:37 S1 %NTP-6-SYNC: Clock is synchronized to NTP server 192.168.1.100",

def json_load(file):
    with open(file, 'r') as f:
        return json.load(f)

#this function creates connection to a specified device based on the IP address
def netmiko_connection(ip_addr: str) -> BaseConnection:
    ssh_connection = None
    try:
        ssh_connection = ConnectHandler(
            device_type = "cisco_ios",
            host = ip_addr,
            username = "cisco",
            password = "cisco123!",
            port = 22
        )
    except NetmikoTimeoutException:
        print("Could not connect to ip address: %s" % ip_addr)
    return ssh_connection

#this funtion retrieves IP address based on the hostname from the log 
def get_hostname(log: str) -> str:
    hostname = log.split(' ')[3]
    #opens a file which contains hostname to IP address mappings
    content = json_load('devices.json')
    for i in content:
        if hostname in i.values():
            return i['ip_address']

#this function retrieves interface from the log message
def find_interface(log: str) -> str:
    x = re.findall("Interface.+[1-24]", log)
    if x:
        interface = ''.join(x).strip().lower()
    return interface

#this function sends message to cisco webex
def send_message(message: str, receiver: str, authorization: str) -> dict:
    url = "https://webexapis.com/v1/messages"
    payload = MultipartEncoder({
            "roomId": receiver,
            "text": message})
    headers = {
        'Authorization': authorization,
        'Content-Type': payload.content_type
        }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

def mac_to_ip(log: str) -> str:
    mac = log.split(' ')[-1]
    #opens a file which contains hostname to IP address mappings
    content = json_load('devices.json')
    for i in content:
        if mac in i.values():
            return i['ip_address']

def load_topology() -> dict:
    content = json_load('devices.json')
    dic = {}

    for device in content:
        dic[device['hostname']] = device['ip_address']

    return dic


ip = mac_to_ip(log_s)
if not ip:
    switches = load_topology()
    curr_ip_address = switches['S1']
    while True:
        ssh_connection = netmiko_connection(curr_ip_address)
        stp_info = ssh_connection.send_command("show spanning-tree")
        sp_output = stp_info.split('\n')
        cost = sp_output[4].strip().split()[1]
        port = sp_output[5].strip().split()[1]
        next_interface = "Fas0/"+port[0:port.index('(')]
        next_interface1 = "Fa0/"+port[0:port.index('(')]
        if int(cost) in {2,4,19,100}:
            ssh_connection.enable()
            ssh_connection.send_config_set(["interface {}".format(next_interface1), "spanning-tree guard root"])
            break
        else:
            neighbors = ssh_connection.send_command("show cdp neighbors")
            neighbor_interfaces = neighbors.split('\n')[3:]
            for i in neighbor_interfaces:
                int1= ''.join(i.split()[1:3])
                if int1 == next_interface:
                    #returns the hostname of the switch it needs to connect next
                    hostname = i.split()[0]
                    curr_ip_address = switches[hostname]
else:
    content = json_load('devices.json')
    switches = [(device['ip_address'], device['bridge_priority']) for device in content if device["hostname"][0] == "S"]
    for device in switches:
       #creating connection to my VM router in the final version it will look: ssh_connection = netmiko_connection(ip_address)
        ssh_connection = netmiko_connection(device[0])
        stp_info = ssh_connection.send_command("show spanning-tree")
        n_bridge = re.search("Bridge.+(\d)").split()[3]
        if n_bridge != device[1]:
            ssh_connection.send_config_set(["spanning-tree vlan 1 priority {0}".format(device[1])])
            message = "Set STP priority back to {0} on {1}".format(device[1], device[0])
            send_message(message, ROOMID, TOKEN)
    



"""
int up/down

ip_addr = get_hostname(log)
interface = find_interface(log)
#creating connection to my VM router in the final version it will look: ssh_connection = netmiko_connection(ip_address)
ssh_connection = netmiko_connection("192.168.56.2")
ssh_connection.enable()
#sending set of commands to shutdown a specific interface in the final version  it will look: ssh_connection.send_config_set(["{}".format(interface), "shutdown"])
ssh_connection.send_config_set(["interface loopback1", "shutdown"])
#exiting config mode
ssh_connection.exit_config_mode()
#using show ip int brief, check whether the specified interfece actually went down; in the final version it will look: check_status = ssh_connection.send_command('show ip int brief | include {}'.format(interface))
check_status = ssh_connection.send_command('show ip int brief | include Loopback1')
#in case the interface didnt go down send message to cisco webex
if "down" in check_status: 
    error_message = "Could not turn down {0} on a device {1}".format(interface, ip_addr)
    send_message(error_message, ROOMID, TOKEN)"""

