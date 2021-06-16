import nfstream
import sys, getopt

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

if __name__ == "__main__":
    # Get command-line arguments
    interface, out_file = parse_cmdline_args(sys.argv[1:])

    # Activate metering processes
    my_streamer = nfstream.NFStreamer(source=interface,
            bpf_filter=None,
            snapshot_length=1600,
            idle_timeout=120,
            active_timeout=1800,
            udps=None,
            statistical_analysis=False)

    print_pandas_flows(my_streamer, out_file)