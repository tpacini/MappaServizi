import nfstream
import json
import socket 
from signal import signal, SIGINT

n_flows = 0
anomalies = 0
n_other_flows = 0
anomalies_list = []
device_ip =  "10.42.0.130"
my_streamer = nfstream.NFStreamer(source="wlp1s0",
    snapshot_length=1600,
    idle_timeout=120,
    active_timeout=1800,
    udps=None)

# Load the list of protocols used by the analyzed device
with open('export_apps.json', 'r') as fd:
    apps = json.load(fd)

def reverse_dns(addr):
    try:
        return socket.gethostbyaddr(addr)[0]
    except IOError:
        return addr

def check_app_flow(app_name):
    if app_name in apps:
        return 0
    else:
         return 1

def handler(signal_received, frame):
    total_flows = str(n_flows)+"/"+str(n_flows+n_other_flows)
    print("|---- Flows({}/total): {} Anomalies: {} ----|".format(device_ip, total_flows, anomalies))
    print("|---- Unknown protocols: ")
    print(anomalies_list, " ----|")
    exit(0)

if __name__ == "__main__":
    # When SIGINT is received, activate the handler
    signal(SIGINT, handler)

    for flow in my_streamer:
        src_ip   = reverse_dns(flow.src_ip) 
        dst_ip   = reverse_dns(flow.dst_ip)
        app_name = flow.application_name
        
        # Take the flows with source ip equal to the analyzed device ip
        if src_ip != device_ip: 
            n_other_flows += 1
            continue
        else:
            n_flows += 1

        # The protocol "app_name" has never been used by the machine, anomaly.
        if check_app_flow(app_name):
            print("{0:2d}. Anomaly detected: {1:15s} --> {2:15s} , {3:15s}".format(anomalies, src_ip, dst_ip, app_name))
            anomalies += 1
            anomalies_list.append(app_name) 

#dare informazioni su ip e gestire associazione ip-applicazione  (il dispositivo potrebbe parlare anche con ip locali),
#ovviamente la mappa dei servizi non si può fare su host remoti che cambiano continuamente ma si può fare con host locali