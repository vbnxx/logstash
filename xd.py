"""import random
from datetime import datetime
import time
import requests


log_templates = [
    "%SYS-5-CONFIG_I: Configured from console by vty0 (192.168.1.10)",
    "%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to up",
    "%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/2, changed state to down",
    "%SEC_LOGIN-4-LOGIN_FAILED: Login failed from 192.168.1.50",
    "%SYS-2-MALLOCFAIL: Memory allocation failure - process OSPF",
    "%SPANTREE-6-PORTBLOCKED: Port 1/0/1 blocked by spanning tree",
    "%NTP-6-SYNC: Clock is synchronized to NTP server 192.168.1.100",
    "%SPANTREE-6-TOPOLOGY_CHANGE: STP topology change detected on VLAN 1",
    "%STP-5-PORTSTATE: GigabitEthernet0/1 changed state to forwarding",
    "%SPANTREE-6-ROOTCHANGE: Root bridge for VLAN 1 changed to 32768:00:1A:2B:3C:4D:5E",
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

"""

stp_info = """VLAN0001
  Spanning tree enabled protocol ieee
  Root ID    Priority    1
             Address     000B.BE52.05EA
             Cost        19
             Port        10(FastEthernet0/10)
             Hello Time  2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32769  (priority 32768 sys-id-ext 1)
             Address     0030.A380.D643
             Hello Time  2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  20

Interface        Role Sts Cost      Prio.Nbr Type
---------------- ---- --- --------- -------- --------------------------------
Fa0/3            Desg FWD 19        128.3    P2p
Fa0/2            Desg FWD 19        128.2    P2p
Fa0/10           Root FWD 19        128.10   P2p"""

cdp_info = """Capability Codes: R - Router, T - Trans Bridge, B - Source Route Bridge
                  S - Switch, H - Host, I - IGMP, r - Repeater, P - Phone
Device ID    Local Intrfce   Holdtme    Capability   Platform    Port ID
S2           Fas 0/6          142            S       2960        Fas 0/5
S3           Fas 0/10          125            S       2960        Fas 0/2"""



n1 = x.split('\n')
n = y.split('\n')[3:]
port = n1[5].strip().split()[1]
inte = "Fas0/1"
x1 = [('192.168.0.1','S1'),('192.168.0.2','S2'),('192.168.0.3','S3')]
for i in n:
    int1= ''.join(i.split()[1:3])
    if int1 ==inte:
        nextt = i.split()[0]
        print(nextt)
for h in x1:
    if h[1]==nextt:
        print(h[0])

class Switch:
    def __init__(self, sp_output: str, cdp_output: str):
        n1 = sp_output.split('\n')
        n = cdp_output.split('\n')[3:]
        self.port = n1[5].strip().split()[1]
        self.interface = "Fas0/1"
        x1 = [('192.168.0.1','S1'),('192.168.0.2','S2'),('192.168.0.3','S3')]
        for i in n:
            int1= ''.join(i.split()[1:3])
            if int1 ==inte:
                nextt = i.split()[0]
                print(nextt)
        for h in x1:
            if h[1]==nextt:
                print(h[0])

    
"""n = x.split('\n')
root_mac= n[3].strip()
port = n[5].strip().split()[1]
print("fas0/"+port[0:port.index('(')])
this_switch_mac = n[9].strip()
if root_mac!=this_switch_mac:
    pass"""



