import nfstream
import json
import sys
import getopt   

APP_NAME_ERR  = "PROTOCOL NEVER USED"
DST_IP_ERR    = "UNKNOWN DESTINATION IP"
SRC_IP_ERR    = "UNKNOWN SOURCE IP"
NO_ERR        = "NONE"

flows_counter = 0   # number of analyzed flows
report        = {"tot_flows":0, "tot_anom":0, NO_ERR:{}, APP_NAME_ERR:{}, DST_IP_ERR:{}, SRC_IP_ERR:{}}  

# Load the services map used as a reference to detect anomalies
with open('export.json', 'r') as fd:
    services_map = json.load(fd)

# Check if addr is a local or remote address
def check_address(addr):
    # Split the address and convert it to int
    parts = list(map(int, addr.split(".")))
    
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

# Parse command-line arguments
def parse_cmdline_args(argv):
    interface = "null"
    usage_str = "Usage: detect_anomalies.py -i <interface>\n" + \
                " "*7 + "detect_anomalies.py -a"

    # No arguments/flag in input
    if len(argv) == 0:
        print(usage_str)
        sys.exit()

    try:
        opts, args = getopt.getopt(argv, "ahi:", ["help=", "interface=", "analyze="])
    except getopt.GetoptError:
        print("Error")
        sys.exit(2)
    
    # Parsing arguments
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print(usage_str)
            sys.exit()
        elif opt in ['-i', '--interface']:
            interface = arg
        elif opt in ['-a', '--analyze_report']:
            print_report()
            exit(0)

    if interface == "null":
        print(usage_str)
        sys.exit()

    return interface

def print_report():
    #TODO: Fare controllo su esistenza del file
    with open('export_report.json', 'r') as fd:
        report = json.load(fd)

    tot_flows = report["tot_flows"]
    tot_anom = report["tot_anom"]

    # Keys are anomalies names
    for i in list(report.keys())[2:]:
        flows = report[i]
        print("\n+++++++ {} anomaly flows +++++++".format(i))
        
        for src_ip in flows.keys():
            dests = flows[src_ip]
            tot_bytes = dests["tot_bytes"]
            print("+ {0:15s} exchange {1:9d} bytes with: " \
                .format(src_ip, tot_bytes))
            
            for dst_ip in list(dests.keys())[1:]:
                b = dests[dst_ip][0]
                perc = (b*100)/tot_bytes
                print("\t - {0:15s}, {1:9d} bytes ({2:3.2f}%) using {3}" \
                    .format(dst_ip, b, perc, dests[dst_ip][1:]))    

    print("\n+++++++ On {} flows, {} anomalies +++++++".format(tot_flows, tot_anom))

# Based on source ip, destination ip and application name of the flow, check if 
# the flow is an anomaly on the network
def check_flow(src_ip, dst_ip, app_name):
    # src_ip already seen in the network
    if src_ip in services_map.keys():
        # src_ip has alreay contacted dst_ip
        if dst_ip in services_map[src_ip].keys():
            # with a different protocol
            if app_name not in services_map[src_ip][dst_ip][1:]:
                return APP_NAME_ERR
        else:
            return DST_IP_ERR
    else:
        return SRC_IP_ERR

    return NO_ERR

# Update a data structure dedicated to the final report (after an interruption like SIGINT)
def update_report(src_ip, dst_ip, app_name, b_bytes, report_dict):
    try:
        dst_list = report_dict[src_ip]

         # If "src_ip" is a key, let's see if dst_ip already exists
        if dst_ip not in dst_list.keys():
            dst_list[dst_ip] = [b_bytes, app_name]
        else:
            dst_list[dst_ip][0] += b_bytes
            # app_name never registered
            if app_name not in dst_list[dst_ip][2:]:
                dst_list[dst_ip].append(app_name)
        
        dst_list["tot_bytes"] += b_bytes

    # "src_ip" key doesn't exists
    except KeyError:
        report_dict[src_ip] = {}
        report_dict[src_ip]["tot_bytes"] = b_bytes
        report_dict[src_ip][dst_ip] = [b_bytes, app_name]
    
    return report_dict


if __name__ == "__main__":
    inner_counter = 0

    # Get interface name and activate the metering processes
    interface = parse_cmdline_args(sys.argv[1:])
    my_streamer = nfstream.NFStreamer(source=interface,
        snapshot_length=1600,
        idle_timeout=60, # set to 120, 60 for testing
        active_timeout=1800,
        udps=None)

    for flow in my_streamer:
        # Doesn't count IPv6 addresses (TODO)
        if ":" in flow.src_ip:
            continue

        src_ip   = check_address(flow.src_ip) 
        dst_ip   = check_address(flow.dst_ip)
        app_name = flow.application_name
        b_bytes  = int(flow.bidirectional_bytes)
        resp     = "{0:15s} --> {1:15s} , {2:20s} | ".format(src_ip, dst_ip, app_name)
        
        err = check_flow(src_ip, dst_ip, app_name)
        report[err] = update_report(src_ip, dst_ip, app_name, b_bytes, report[err])
        if err != NO_ERR:
            report["tot_anom"] += 1
        report["tot_flows"] += 1

        # report dictionary persistence
        if inner_counter == 5:
            inner_counter = 0
            with open('export_report.json', 'w') as fd:
                json.dump(report, fd)
    
        # Print flow analysis results
        print("{0:2d}. {1}".format(flows_counter, resp+err))
        flows_counter += 1
        inner_counter += 1
        
# TODO: Support IPv6
# TODO: Aggiungere un flag che incorpori lo script report_analyze, così da non dover eseguire mille script diversi
'''
tot_flows: ...
tot_anom; ...
ERR1: {
    src_ip1: {
        tot_bytes: ...
        dst_ip:[bytes, app_name]
        dst_ip1:[bytes, app_name1, app_name2]
        ...
    }
}
'''
