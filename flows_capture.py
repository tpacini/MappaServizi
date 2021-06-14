import nfstream

DEBUG = 0

# Print some infos of the received flows 
def print_formatted_flows(my_streamer):
    for flow in my_streamer:
        print("{0:3d}: {1:15s} : {2:5d} --> {3:15s} : {4:5d} | A_name: {5:15s} R_s_n: {6:20s}".format(
            flow.id,
            flow.src_ip,
            flow.src_port,
            flow.dst_ip,
            flow.dst_port,
            flow.application_name,
            flow.requested_server_name))

# Export the received flows in the ".csv" format
def print_pandas_flows(my_streamer):
    df = my_streamer.to_pandas()
    df.to_csv('./test1_60min.csv')

if __name__ == "__main__":
    my_streamer = nfstream.NFStreamer(source="wlp1s0",
            bpf_filter=None,
            snapshot_length=1600,
            idle_timeout=120,
            active_timeout=1800,
            udps=None,
            statistical_analysis=False)

    if DEBUG == 1:
        print_formatted_flows(my_streamer)
    else:
        print_pandas_flows(my_streamer)
