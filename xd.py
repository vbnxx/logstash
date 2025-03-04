import random
from datetime import datetime
import time
import requests


log_templates = [
    "%SYS-5-CONFIG_I: Configured from console by vty0 (192.168.1.10)",
    "%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to up",
    "%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/2, changed state to down",
    "%SEC_LOGIN-4-LOGIN_FAILED: Login failed from 192.168.1.50",
    "%SYS-2-MALLOCFAIL: Memory allocation failure - process OSPF",
    "%SPANTREE-6-PORTBLOCKED: Port 1/0/1 blocked by spanning tree"
]

def generate_log():
    timestamp = datetime.now().strftime("%b %d %H:%M:%S")
    hostname = "S1"
    log_entry = f"{timestamp} {hostname} {random.choice(log_templates)}"
    return log_entry

# Generate 10 logs


while True:
    #requests.post("http://localhost:9200", data=generate_log(), verify=False)
    print(generate_log())
    # using time to simulate activity
    time.sleep(random.randint(1, 4))

