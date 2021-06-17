import nfstream
import json
import sys
import getopt
from signal import signal, SIGINT
# from flows_capture import ....


flows_counter  = 0   # number of analyzed flows
report         = {}  # dictionary used for the final report
outlier_report = {}  # dictionary used for the final report (outlier)

# Load the services map used as a reference to detect anomalies
with open('export.json', 'r') as fd:
    services_map = json.load(fd)

# Parse command-line arguments
def parse_cmdline_args(argv):
    interface = "null"

    # No arguments/flag in input
    if len(argv) == 0:
        print("Usage: detect_anomalies.py -i <interface>")
        sys.exit()

    try:
        opts, args = getopt.getopt(argv, "hi:", ["help=", "interface="])
    except getopt.GetoptError:
        print("Error")
        sys.exit(2)
    
    # Parsing arguments
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print("Usage: detect_anomalies.py -i <interface>")
            sys.exit()
        elif opt in ['-i', '--interface']:
            interface = arg

    if interface == "null":
        print("Usage: detect_anomalies.py -i <interface>")
        sys.exit()

    return interface

# Check if addr is a local or remote address
def check_address(addr):
    parts = addr.split(".")
    # Convert string to int
    for i in range(0, len(parts)):
        parts[i] = int(parts[i])
    
    # local address 10.0.0.0 - 10.255.255.255
    if parts[0] == 10:
        return addr
    # local address 172.16.0.0 - 172.31.255.255
    elif (parts[0] == 172) and (parts[1] >= 16) and (parts[1] <= 31):
        return addr
    # local address 192.168.0.0 - 192.168.255.55
    elif (parts[0] == 192) and (parts[1] == 168):
        return addr
    else:
        return "remote"

# Based on source ip, destination ip and application name of the flow, check if 
# the flow is an anomaly on the network
def check_flow(src_ip, dst_ip, app_name):
    resp = "{0:15s} --> {1:15s} , {2:20s} | ".format(src_ip, dst_ip, app_name)
    err = ""

    # src_ip never seen in the network
    if src_ip in services_map.keys():
        # src_ip has alreay contacted dst_ip
        if dst_ip in services_map[src_ip].keys():
            # with a different protocol
            if app_name not in services_map[src_ip][dst_ip][1:]:
                err = "PROTOCOL NEVER USED"
        else:
            err = "UNKNOWN DESTINATION IP"
    else:
        err = "UNKNOWN SOURCE IP"
    
    return resp+err

# SIGINT handler function
def handler(signal_received, frame):
    exit(0)

if __name__ == "__main__":
    # Get interface name and activate the metering processes
    interface = parse_cmdline_args(sys.argv[1:])
    my_streamer = nfstream.NFStreamer(source=interface,
    snapshot_length=1600,
    idle_timeout=120,
    active_timeout=1800,
    udps=None)

    # When SIGINT is received, activate the handler
    signal(SIGINT, handler)

    for flow in my_streamer:
        # Don't count IPv6 addresses (TODO)
        if ":" in flow.src_ip:
            continue

        src_ip   = check_address(flow.src_ip) 
        dst_ip   = check_address(flow.dst_ip)
        app_name = flow.application_name
        
        resp = check_flow(src_ip, dst_ip, app_name)
        
        # Print flow analysis results
        print("{0:2d}. {}".format(flows_counter, resp))
        flows_counter += 1
