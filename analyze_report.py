import json

with open('export_report.json', 'r') as fd:
    report = json.load(fd)

def print_report(report):
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

if __name__ == '__main__':
    print_report(report)
