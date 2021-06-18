APP_NAME_ERR  = "PROTOCOL NEVER USED"
DST_IP_ERR    = "UNKNOWN DESTINATION IP"
SRC_IP_ERR    = "UNKNOWN SOURCE IP"
NO_ERR        = "NONE"

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
