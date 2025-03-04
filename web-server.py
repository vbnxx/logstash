import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from netmiko import BaseConnection, ConnectHandler, NetmikoTimeoutException
import re
from requests_toolbelt import MultipartEncoder
import requests

HOSTNAME='localhost'
PORT=3999
ROOMID = "Y2lzY29zcGFyazovL3VybjpURUFNOmV1LWNlbnRyYWwtMV9rL1JPT00vZTBjYzlmMzAtZWRmZC0xMWVmLThhMDQtMDVhN2ZkMjgxODQ5"
TOKEN = "Bearer MTY3MDhmYTMtOWUyYS00MzJmLTkwZDAtYTFjZTFkMzUwM2MzNjdmNjE1ZTEtYzBk_PE93_bde28e3d-21ec-426e-b7f1-1c7280ca363f"

def netmiko_connection(ip_address: str) -> BaseConnection:
    ssh_connection = None
    try:
        ssh_connection = ConnectHandler(
            device_type = "cisco_ios",
            host = ip_address,
            username = "cisco",
            password = "cisco123!",
            port = 22
        )
    except NetmikoTimeoutException:
        print("Could not connect to ip address: %s" % ip_address)
    return ssh_connection

def get_hostname(log: str) -> str:
    hostname = log.split(' ')[3]
    with open('devices.json', 'r') as file:
        content = json.load(file)
        for i in content:
            if hostname in i.values():
                return i['ip_address']

def get_interface(log: str) -> str:
    x = re.findall("Interface.+[1-24]", log)
    if x:
        interface = ''.join(x).strip().lower()
    return interface

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

def shut_int(log):
    ip_address = get_hostname(log)
    interface = get_interface(log)
    ssh_connection = netmiko_connection(ip_address)
    ssh_connection.enable()
    ssh_connection.send_config_set(["{}".format(interface), "shutdown"])
    ssh_connection.exit_config_mode()
    check_status = ssh_connection.send_command('show ip int brief | include {}'.format(interface))
    if "down" not in check_status: 
        error_message = "Could not turn down {0} on a device {1}".format(interface, ip_address)
        send_message(error_message, ROOMID, TOKEN)
    else:
        print('Shuting down "%s".' % (interface))

def up_int(log):
    ip_address = get_hostname(log)
    interface = get_interface(log)
    ssh_connection = netmiko_connection(ip_address)
    ssh_connection.enable()
    ssh_connection.send_config_set(["{}".format(interface), "no shutdown"])
    ssh_connection.exit_config_mode()
    check_status = ssh_connection.send_command('show ip int brief | include Loopback1')
    if "down" not in check_status: 
        error_message = "Could not turn up {0} on a device {1}".format(interface, ip_address)
        send_message(error_message, ROOMID, TOKEN)
    else:
        print('Turning up  "%s".' % (interface))

def STP_config(host, port):
    # send an action here to the library
    print('Restoring STP config on "%s:%s".' % (host, port))

def NTP(host, port):
    # send an action here to the library
    print('Reseting the time on a NTP server "%s:%s".' % (host, port))

def DHCP(host, port):
    # send an action here to the library
    print('Reseting the time on a DHCP server "%s:%s".' % (host, port))

events_and_actions = {
    'state to up' : shut_int,
    'state to down': up_int,
    'STP' : STP_config,
    'NTP' : NTP,
    'DHCP' : DHCP
}

class WebServer(BaseHTTPRequestHandler):
    def response_with(self, status, message):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()  
        self.wfile.write(json.dumps({'message': message}).encode('utf-8'))

    def do_POST(self):
        try:
            if self.path == "/log":
                content_length = int(self.headers.get('Content-Length'))  # Get the size of the data
                request_body = self.rfile.read(content_length)  # Read the body
                log = json.loads(request_body.decode('utf-8'))

                if log['level'] == 'critical':
                    if log['type'] in events_and_actions:
                        action = events_and_actions[log['type']]
                        print('Critical log type "%s" acknowledged. Preforming action "%s"' % (log['type'], action.__name__))
                        action(log['host'], log['port'])
                    else:
                        print('Critical log type "%s" not supported. Ignoring...' % log['type'])
                else:
                        print('Log type "%s" processed...' % log['type'])

                self.response_with(201, 'Log received successfully')
            else:
                self.response_with(404, 'Not found.')

        except Exception as e:
            print(e)
            self.response_with(500, 'Internal Server Error')

if __name__ == '__main__':
    webServer = HTTPServer((HOSTNAME, PORT), WebServer)

    try:
        print('Server awaiting requests at http://%s:%s.' % (HOSTNAME, PORT))
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
