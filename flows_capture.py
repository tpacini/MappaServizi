import nfstream
import sys, getopt
import pandas as pd
import json
from signal import signal, SIGINT


# Export the received flows in the ".csv" format
def print_pandas_flows(my_streamer, out_file):
    df = my_streamer.to_pandas()
    df.to_csv('./' + out_file + '.csv')

# Parse command-line arguments
def parse_cmdline_args(argv):
    interface = "null"
    out_file = "null"

    # No arguments/flag in input
    if len(argv) == 0:
        print("Usage: flows_capture.py -i <capture_interface> -o <output_filename>")
        sys.exit()

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["help=", "interface=", "output_filename="])
    except getopt.GetoptError:
        print("Error")
        sys.exit(2)
    
    # Parsing arguments
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print("Usage: flows_capture.py -i <capture_interface> -o <output_filename>")
            sys.exit()
        elif opt in ['-i', '--interface']:
            interface = arg
        elif opt in ['-o', '--output_filename']:
            out_file = arg

    if interface == "null" or out_file == "null":
        print("Usage: flows_capture.py -i <capture_interface> -o <output_filename>")
        sys.exit()

    return interface, out_file

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

# SIGINT handler function
def handler(signal_received, frame, out_file):
    # Import the '.csv' file and remove the useless columns
    df = pd.read_csv('./' + out_file + '.csv')
    df.drop(["Unnamed: 0", "src_oui", "dst_oui", "id", "expiration_id","client_fingerprint", "server_fingerprint", "src_mac", "dst_mac", "vlan_id", "tunnel_id", "expiration_id", \
    "client_fingerprint", "server_fingerprint", "user_agent", "bidirectional_first_seen_ms", "bidirectional_last_seen_ms", "bidirectional_duration_ms", "dst2src_packets", \
    "dst2src_packets", "dst2src_first_seen_ms", "dst2src_last_seen_ms", "dst2src_duration_ms", "src2dst_first_seen_ms", "src2dst_last_seen_ms", "src2dst_duration_ms", \
    "src2dst_packets", "src2dst_bytes", "dst2src_bytes", "bidirectional_packets"], axis=1, inplace=True)
    df.sort_values(["src_ip"], inplace=True)
    df.reset_index(drop=True, inplace=True)


    # Template dictionary: {"src1":{"dst1":[n_bytes, app1, app2], "dst2":n_bytes, ...}, "src2":...... }
    # All the remote addresses end up in "remote" address (source and destination)
    sources = {}
    src_ips = df.src_ip.unique()

    for i in src_ips:
        # Don't count IPv6 addresses (TODO)
        if ":" in src_ips:
            continue
        
        aux_dict = {}
        temp = df[df['src_ip'] == i]
        i = check_address(i)

        for index, row in temp.iterrows():
            dst_ip = check_address(row['dst_ip'])
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

    sources.keys()

    with open('export.json', 'w') as fd:
        json.dump(sources, fd)

    exit(0)


if __name__ == "__main__":
    # Get command-line arguments
    interface, out_file = parse_cmdline_args(sys.argv[1:])

    # When SIGINT is received, activate the handler
    signal(SIGINT, handler, out_file)

    # Activate metering processes
    my_streamer = nfstream.NFStreamer(source=interface,
            bpf_filter=None,
            snapshot_length=1600,
            idle_timeout=120,
            active_timeout=1800,
            udps=None,
            statistical_analysis=False)

    print_pandas_flows(my_streamer, out_file)


