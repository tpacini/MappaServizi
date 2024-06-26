from nfstream import NFStreamer
import json, sys, os, getopt   
import pandas as pd
from scapy.arch.windows import *

with open('config.json', 'r') as fd:
    j = json.load(fd)
    SOFT_ERR          = j["soft_error"]
    UNK_PROTO_ERR     = j["unknown_proto_error"]
    APP_NAME_ERR      = j["app_name_error"]
    DST_IP_ERR        = j["dst_ip_error"]
    SRC_IP_ERR        = j["src_ip_error"]
    NO_ERR            = j["no_error"]

    REPORT_FILENAME   = j["report_file"]
    SERV_MAP_FILENAME = j["servmap_file"]
    OUT_FILENAME      = j["out_file"]

    DEVICE_IPS        = j["device_ips"]

flows_counter = 0   # number of analyzed flows
report        = {"tot_flows":0, "tot_anom":0, NO_ERR:{}, SOFT_ERR:{}, APP_NAME_ERR:{}, 
                    DST_IP_ERR:{}, SRC_IP_ERR:{}, UNK_PROTO_ERR:{}}  

class ServiceMap:
    def __init__(self):
        self.dataset = None
        self.sources = None

    # Generate the data structure describing the services map
    def generate_services_map(self):
        # Load the dataset 
        try:
            df = pd.read_csv(OUT_FILENAME)
        except FileNotFoundError:
            print("File not found.")
            exit(0)

        # Drop the useless columns
        df.drop(["Unnamed: 0", "src_oui", "dst_oui", "id", "expiration_id","client_fingerprint", 
        "server_fingerprint", "src_mac", "dst_mac", "vlan_id", "tunnel_id", "expiration_id","client_fingerprint", 
        "server_fingerprint", "user_agent", "bidirectional_first_seen_ms", "bidirectional_last_seen_ms", 
        "bidirectional_duration_ms", "dst2src_packets", "dst2src_packets", "dst2src_first_seen_ms", "dst2src_last_seen_ms", 
        "dst2src_duration_ms", "src2dst_first_seen_ms", "src2dst_last_seen_ms", "src2dst_duration_ms", "src2dst_packets", 
        "src2dst_bytes", "dst2src_bytes", "bidirectional_packets"], axis=1, inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Filter on address of analysed device(s)
        df1 = df[(df['src_ip'] == DEVICE_IPS[0]) | (df['dst_ip'] == DEVICE_IPS[0])]

        if len(DEVICE_IPS) > 1:
            for d_addr in DEVICE_IPS[1:]:
                temp_df = df[(df['src_ip'] == d_addr) | (df['dst_ip'] == d_addr)]
                df1 = pd.concat([df1, temp_df])
            
        df = df1[~df1.index.duplicated(keep='first')]
        df.reset_index(drop=True, inplace=True)

        # Filter on "Unknown" protocol name
        df = df[df['application_name'] != "Unknown"]

        # Convert remote addresses in "remote"
        # All the remote addresses end up in "remote" address (source and destination)
        df['src_ip'] = df['src_ip'].apply(check_address)
        df['dst_ip'] = df['dst_ip'].apply(check_address)

        # Generate the dedicated data structure
        self.dataset = df
        sources = {}
        src_ips = df.src_ip.unique()

        for i in src_ips:
            temp = df[df['src_ip'] == i]
            aux_dict = {}

            for index, row in temp.iterrows():
                dst_ip = row['dst_ip']
                b_bytes = row['bidirectional_bytes']
                app_name = row['application_name']
                
                try:
                    pres = aux_dict[dst_ip]
                    pres[0] += int(b_bytes)
                    if not app_name in pres:
                        pres.append(app_name) 
                except KeyError:
                    aux_dict[dst_ip] = [int(b_bytes), app_name]
                    
            sources[i] = aux_dict

        # Save the services map in a json file
        self.sources = sources
        with open(SERV_MAP_FILENAME, 'w') as fd:
            json.dump(sources, fd)
            print("Services' map generated.")

# Parse command-line arguments
def parse_cmdline_args(argv):
    usage_str = "Usage: detect_anomalies.py -h\n\tdetect_anomalies.py -a"

    try:
        opts, args = getopt.getopt(argv, "ah:", ["help=", "analyze="])
    except getopt.GetoptError:
        print("Error")
        sys.exit(2)
    
    # Parsing arguments
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print(usage_str)
            sys.exit()
        elif opt in ['-a', '--analyze_report']:
            print_report()
            exit(0)

# Print the report of flows seen
def print_report():
    try:
        with open(REPORT_FILENAME, 'r') as fd:
            report = json.load(fd)
    except FileNotFoundError:
        print("Report file not found. Exiting...")
        exit(0)

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

# Check if addr is a local or remote address.
def check_address(addr):
    # IPv6 address
    if ":" in addr:
        return 
    parts = addr.split(".")
    # Convert string to int
    for i in range(0, len(parts)):
        parts[i] = int(parts[i])

    # local address 10.0.0.0/8
    if parts[0] == 10:
        return addr
    # local address 172.16.0.0/12
    elif (parts[0] == 172) and ((parts[1] >= 16) and (parts[1] <= 31)):
        return addr
    # local address 192.168.0.0/16
    elif (parts[0] == 192) and (parts[1] == 168):
        return addr
    else:
        return "remote"

# Based on source ip, destination ip and application name of the flow, check if 
# the flow is an anomaly on the network
def check_flow_anomaly(src_ip, dst_ip, app_name):
    # src_ip already seen in the network
    if src_ip in services_map.keys():
        # src_ip has alreay contacted dst_ip
        if dst_ip in services_map[src_ip].keys():
            # with a different protocol
            known_protos = services_map[src_ip][dst_ip][1:]
            if app_name not in known_protos:
                # DNS/TLS soft anomaly
                if ("DNS" in app_name) or ("TLS" in app_name): 
                    return SOFT_ERR
                # Unknown protocol
                elif app_name == "Unknown":
                    return UNK_PROTO_ERR
                return APP_NAME_ERR
        else:
            return DST_IP_ERR
    else:
        return SRC_IP_ERR

    return NO_ERR

# Update a data structure dedicated to the final report
def update_report(src_ip, dst_ip, app_name, b_bytes, report_dict):
    try:
        dst_list = report_dict[src_ip]

         # If "src_ip" is a key, let's see if dst_ip already exists
        if dst_ip not in dst_list.keys():
            dst_list[dst_ip] = [b_bytes, app_name]
        else:
            dst_list[dst_ip][0] += b_bytes
            # app_name never registered
            if app_name not in dst_list[dst_ip][1:]:
                dst_list[dst_ip].append(app_name)
        
        dst_list["tot_bytes"] += b_bytes

    # "src_ip" key doesn't exists
    except KeyError:
        report_dict[src_ip] = {}
        report_dict[src_ip]["tot_bytes"] = b_bytes
        report_dict[src_ip][dst_ip] = [b_bytes, app_name]
    
    return report_dict

# Generate the string for bpf filter
def bpf_string(addresses):
    filter_str = ""

    for addr in addresses:
        filter_str += "dst host " + addr + " or " + "src host " + addr + " or "

    return filter_str[:-4]


if __name__ == "__main__":
    # Get capture interface name
    parse_cmdline_args(sys.argv[1:])
    
    print("Choose a network interface:")
    interfaces = get_windows_if_list()
    i = 0
    for interface in interfaces:
        print(f"[{i}] Name: {interface['name']}, GUID: {interface['guid']}")
        i += 1

    try:
        id = int(input("Interface index: "))
        if id < 0 or id > (len(interfaces)-1):
            raise ValueError
    except ValueError:
        print(f"The index should be an integer between 0 and {len(interfaces)-1}.")

    # Activate metering processes
    if os.name == 'nt':
        print("Windows platform.")
        source = r"\Device\NPF_" + interfaces[id]['guid']
    elif os.name == 'posix':
        print("Linux platform.")
        source = interfaces[id]['guid']
    else:
        print("Platform not supported")
        sys.exit()

    # Generate the services map and load it, used as a reference to detect anomalies
    sm = ServiceMap()
    sm.generate_services_map()

    try:
        with open(SERV_MAP_FILENAME, 'r') as fd:
            services_map = json.load(fd)
    except FileNotFoundError:
        print("Services map file not found. Exiting..")
        exit(0)

    # Activate the metering processes 
    my_streamer = NFStreamer(source=source,
        bpf_filter = bpf_string(DEVICE_IPS), # filter the traffic on src/dst ip
        snapshot_length=1600,
        idle_timeout=60, # set to 120, 60 for testing
        active_timeout=1800,
        udps=None)

    # Display incoming flows and guarantee persistence
    inner_counter = 0
    print("Incoming flows:")
    for flow in my_streamer:
        src_ip   = check_address(flow.src_ip) 
        dst_ip   = check_address(flow.dst_ip)
        app_name = flow.application_name
        b_bytes  = int(flow.bidirectional_bytes)
        resp     = "{0:15s} --> {1:15s} , {2:20s} | ".format(src_ip, dst_ip, app_name)
        
        err = check_flow_anomaly(src_ip, dst_ip, app_name)
        report[err] = update_report(src_ip, dst_ip, app_name, b_bytes, report[err])
        if err != NO_ERR:
            report["tot_anom"] += 1
        report["tot_flows"] += 1

        # Periodical persistence of report
        if inner_counter == 4:
            inner_counter = 0
            with open(REPORT_FILENAME, 'w') as fd:
                json.dump(report, fd)
    
        # Print flow analysis results
        print("{0:3d}. {1}".format(flows_counter, resp+err))
        flows_counter += 1
        inner_counter += 1