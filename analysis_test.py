import pandas as pd 
from pyvis import network as net
import json

def create_services_map(df):
    # Template: {"src1":{"dst1":[n_bytes, app1, app2], "dst2":n_bytes, ...}, "src2":...... }
    # All the remote addresses end up in "remote" address (source and destination)

    sources = {}
    src_ips = df.src_ip.unique()

    for i in src_ips:
        temp = df[df['src_ip'] == i]
        i = check_address(i)
        aux_dict = {}

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

    return sources

def visualize_map(sources):
    g=net.Network(height='500px', width='800px',heading='')
    g.add_nodes(sources.keys())

    # Add edges
    # First try without weights
    for i in sources.keys():
        elem = sources[i]
        g.add_nodes(elem.keys())
        for j in elem.keys(): 
            g.add_edge(i, j)

    # g.save_graph('example.html')
    g.show('example.html')

def check_address(addr):
    # IPv6 address
    if ":" in addr:
        return addr

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

if __name__ == '__main__':
    # Load the dataset 
    df = pd.read_csv('test1_60min.csv')
    
    # Drop the useless columns
    df.drop(["Unnamed: 0", "src_oui", "dst_oui", "id", "expiration_id","client_fingerprint", "server_fingerprint", "src_mac", "dst_mac", "vlan_id", "tunnel_id", "expiration_id","client_fingerprint", "server_fingerprint", "user_agent", "bidirectional_first_seen_ms", "bidirectional_last_seen_ms", "bidirectional_duration_ms", "dst2src_packets", "dst2src_packets", "dst2src_first_seen_ms", "dst2src_last_seen_ms", "dst2src_duration_ms", "src2dst_first_seen_ms", "src2dst_last_seen_ms", "src2dst_duration_ms", "src2dst_packets", "src2dst_bytes", "dst2src_bytes", "bidirectional_packets"], axis=1, inplace=True)
    df.sort_values(["src_ip"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # IPv6 used for MDNS
    # df = df[(df['src_ip'] != "ipv6_1") & (df['src_ip'] != "ipv6_2")]
    # df = df[(df['dst_ip'] != "ipv6_3")]

    serv_map = create_services_map(df)
    # visualize_map(serv_map)
    
    # Save the services map in a json file
    with open('export.json', 'w') as fd:
        json.dump(serv_map, fd)