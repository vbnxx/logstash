import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import netmiko

def netmiko_connection(ip_addr):
    username = input("Username: ")
    password = input("Password: ")
    ssh_con = {
        "device_type": "cisco_ios",
        "host": ip_addr,
        "username": username,
        "password": password,
        "port": 22

    }
    return ssh_con

HOSTNAME='localhost'
PORT=3999

def shut_port(host, port):
    # send an action here to the library
    print('Shuting down a port action on "%s:%s".' % (host, port))

def up_port(host, port):
    # send an action here to the library
    print('Truning a port up on "%s:%s".' % (host, port))

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
    'up_port' : shut_port,
    'down_port': up_port,
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
    #miko = netmiko_connection("192.168.56.2")
    try:
        print('Server awaiting requests at http://%s:%s.' % (HOSTNAME, PORT))
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
