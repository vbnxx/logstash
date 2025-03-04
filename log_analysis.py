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
    with open('devices.json', 'r') as file:
        content = json.load(file)
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
    send_message(error_message, ROOMID, TOKEN)
