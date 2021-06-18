from detect_anomalies import APP_NAME_ERR
import json
from detect_anomalies import APP_NAME_ERR, DST_IP_ERR, SRC_IP_ERR

with open('export_report.json', 'r') as fd:
    report = json.load(fd)

def print_report(report):
    tot_flows = report["tot_flows"]
    non_anom = 0

    # Keys are anomalies names
    for i in report.keys()[1:]:
        flows = report[i]
        if i == "":
            # Count number of flows with no anomalies
            for src_ips in flows.keys():
                non_anom += len(flows[src_ips][1:])
            print("+++++++ Normal flows +++++++")
        else:
            print("+++++++ {} flows +++++++".format(i))
        
        for src_ip in flows.keys():
            dests = flows[src_ip]
            tot_bytes = dests["tot_bytes"]
            print("+ {0:15s} exchange {1:9d} bytes with: " \
                .format(src_ip, tot_bytes))
            
            for dst_ip in dests.keys()[1:]:
                b = dests[dst_ip][0]
                perc = (b*100)/tot_bytes
                print("\t - {0:15s}, {1:9d} bytes ({2:3.2f}%) using {}") \
                    .format(dst_ip, b, perc)    

    print("+++++++ On {} flows, {} anomalies +++++++".format(tot_flows,
        tot_flows - non_anom))


if __name__ == '__main__':

    print_report(report)
