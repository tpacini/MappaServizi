from nfstream import NFStreamer
import sys, getopt
import json
from scapy.arch.windows import *
import os

with open('config.json', 'r') as fd:
    j = json.load(fd)
    OUT_FILENAME = j['out_file']

# Parse command-line arguments
def parse_cmdline_args(argv):
    usage = "Usage: flows_capture.py\n\t-h for help"

    try:
        opts, _ = getopt.getopt(argv, "h:", ["help=", "interface="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    
    # Parsing arguments
    for opt, _ in opts:
        if opt in ['-h', '--help']:
            print(usage)
            sys.exit()

if __name__ == "__main__":
    # Get command-line arguments
    parse_cmdline_args(sys.argv[1:])

    # Choose the traffic capture interface 
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
        
    my_streamer = NFStreamer(source=source,
            bpf_filter=None,
            snapshot_length=1600,
            idle_timeout=120,
            active_timeout=1800,
            udps=None,
            statistical_analysis=False)

    # Export the flows using pandas in a .csv format
    try:
        df = my_streamer.to_pandas()
        df.to_csv(OUT_FILENAME)
    except AttributeError:
        print("No captured data. File empty.")