import time
import requests
import random
import ipaddress

def generate_logs(n):
    log_types = [('port_down', 'critical'), ('port_up', 'critical'), ("STP_root_port_change", 'critical'), ('authentication_success', 'info'),('authentication_failure', 'warning'), ('NTP time missmatch', 'critical'), ('Configuration changes with console', 'info'), ('Configuration changes with console', 'warning')]
    ip_addr = [('R1', "192.168.2.56"), ('S1', "192.168.2.57"), ('S2', '192.168.2.58'), ('S3', '192.168.2.59'), ('DHCP', '192.168.2.60'), ('PC1', '192.168.2.61')]
    logs = []
    for i in range(n):
        log_type = random.choice(log_types)
        host = random.choice(ip_addr)

        logs.append({
                'level': log_type[1],
                'type': log_type[0],
                'message': 'This is an example log',
                'host': host[0],
                'port': host[1]
        })

    return logs


logs = generate_logs(10)

for l in logs:
    requests.post("http://localhost:3999/log", json=l, verify=False)
    
    # using time to simulate activity
    time.sleep(random.randint(1, 4))

