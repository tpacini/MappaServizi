# Map of the services

## Introduction
The aim of the project was to create a script that could identify network anomalies by looking at a *map* of services.

First, the software records the network behaviour, the `flows_capture.py` file captures the network traffic and generates the packet related flows using the *nfstream* library.

Based on these flows, a map of the services is created, which is used as a filter to identify potential anomalies (unknown protocol, unknown source IP, ...).

## Requirements
To run the script, some libraries should be installed:

`pip install -r requirements.txt`

For Python 3.x:

`pip3 install -r requirements.txt`

**IMPORTANT:** run the command with superuser permissions

## Usage

*Note: the script works both for Linux and Windows.*

1. Modify the `config.json` file, if needed
    - *device_ips:* IP addresses of the analyzed devices
    - *out_file:* output path for the network capture file
    - *servmap_file:* output path for services' map
    - *report_file:* output path of the report file
2. Run `sudo flows_capture.py` to capture the traffic on the selected interface and output a file containing the captured network traffic. Superuser privileges are required to enable network capture on the network interface.
3. Run `sudo detect_anomalies.py` to create the services map and start capturing the packets through the selected network interface; in real time, the script analyses the flow information looking for anomalies. A result is displayed for each flow examined:

```
 1.  10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 2.  10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 3.  10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
 4.  10.42.0.130     --> remote          , TLS.Amazon           | NONE
 5.  10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
...
 65. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 66. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 67. 10.42.0.130     --> remote          , BitTorrent.Amazon    | PROTOCOL NEVER USED
 68. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 69. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 70. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 71. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 72. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 73. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 74. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 75. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 76. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
...
319. 10.42.0.130     --> remote          , TLS                  | NONE
320. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
321. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
322. remote          --> 10.42.0.130     , ICMP                 | PROTOCOL NEVER USED
323. 10.42.0.130     --> remote          , QUIC.Google          | NONE
324. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
325. 10.42.0.130     --> remote          , QUIC.Google          | NONE
326. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
327. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
...
364. 10.42.0.130     --> 10.42.0.1       , DNS.UbuntuONE        | DNS/TLS APPLICATION
365. 10.42.0.130     --> 10.42.0.96      , Unknown              | UNKNOWN DESTINATION IP
366. 10.42.0.130     --> remote          , SSH                  | PROTOCOL NEVER USED
367. remote          --> 10.42.0.130     , Unknown              | UNKNOWN PROTOCOL
368. 10.42.0.130     --> 10.42.0.96      , Unknown              | UNKNOWN DESTINATION IP
369. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
370. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
371. 10.42.0.130     --> 10.42.0.96      , Unknown              | UNKNOWN DESTINATION IP
372. 10.42.0.130     --> 10.42.0.96      , TLS                  | UNKNOWN DESTINATION IP
373. 10.42.0.130     --> 10.42.0.96      , Unknown              | UNKNOWN DESTINATION IP
374. 10.42.0.130     --> 10.42.0.1       , DHCP                 | PROTOCOL NEVER USED
375. 10.42.0.130     --> remote          , NTP.UbuntuONE        | NONE
376. remote          --> 10.42.0.130     , Unknown              | UNKNOWN PROTOCOL
```

Periodically, an anomaly report is stored on the local machine. After capture, the user can run `sudo python3 detect_anomalies.py -a` to get a formatted version of the report:

```
+++++++ NONE anomaly flows +++++++
+ 10.42.0.130     exchange  71595235 bytes with: 
         - 10.42.0.1      ,     51994 bytes (0.07%) using ['DNS', 'DNS.AmazonVideo', 'DNS.Amazon', 'DNS.Google', 'DNS.GoogleServices', 'DNS.Microsoft', 'DNS.NetFlix', 'DNS.YouTube']
         - remote         ,  71543241 bytes (99.93%) using ['TLS', 'TLS.Amazon', 'HTTP', 'TLS.AmazonVideo', 'TLS.Google', 'QUIC.Google', 'TLS.YouTube', 'HTTP.Google', 'NTP.UbuntuONE', 'TLS.Cloudflare', 'QUIC.YouTube', 'TLS.GoogleServices']

+++++++ DNS/TLS APPLICATION anomaly flows +++++++
+ 10.42.0.130     exchange   1680371 bytes with: 
         - 10.42.0.1      ,      2417 bytes (0.14%) using ['DNS.Wikipedia', 'DNS.UbuntuONE']
         - remote         ,   1677954 bytes (99.86%) using ['TLS.Wikipedia']

+++++++ PROTOCOL NEVER USED anomaly flows +++++++
+ 10.42.0.130     exchange     67578 bytes with: 
         - remote         ,     66886 bytes (98.98%) using ['BitTorrent', 'BitTorrent.Amazon', 'ICMP', 'IGMP', 'SSDP', 'SSH']
         - 10.42.0.1      ,       692 bytes (1.02%) using ['DHCP']
+ remote          exchange      1399 bytes with: 
         - 10.42.0.130    ,      1399 bytes (100.00%) using ['ICMP', 'ICMP.Amazon']

+++++++ UNKNOWN DESTINATION IP anomaly flows +++++++
+ 10.42.0.130     exchange   5154607 bytes with: 
         - 10.42.0.96     ,   5154607 bytes (100.00%) using ['Unknown', 'TLS']

+++++++ UNKNOWN SOURCE IP anomaly flows +++++++
+ 10.42.0.1       exchange      2600 bytes with: 
         - 10.42.0.130    ,      2600 bytes (100.00%) using ['ICMP']

+++++++ UNKNOWN PROTOCOL anomaly flows +++++++
+ 10.42.0.130     exchange      2040 bytes with: 
         - 10.42.0.1      ,      2040 bytes (100.00%) using ['Unknown']
+ remote          exchange      2198 bytes with: 
         - 10.42.0.130    ,      2198 bytes (100.00%) using ['Unknown']

+++++++ On 561 flows, 159 anomalies +++++++
```

## Map of the services 
The purpose of the program is to detect anomalies on the network, related to one or more devices. It does this by using a **services map**, which is a data structure that describes *which hosts have communicated with other hosts and what protocols have been used*, for example by looking at `services_map.json`:
- *10.42.0.130* sent only DNS requests to *10.42.0.1*,
- *remote* communicated with *10.42.0.130* only via TLS.

The services map is a **json file** (`services_map.json`), a key-value dictionary:
- **key:** source ip
- **value:** list of key-value pairs
  - **sub_key:** destination ip
  - **sub_value:** array containing the number of bytes that the two hosts have exchanged and a list of the protocols used.

```json
"10.42.0.130": {
        "10.42.0.1": [
            87215,
            "DNS",
            "DNS.Microsoft",
            "DNS.NetFlix",
            "..."
        ],
        "remote": [
            169616558,
            "TLS",
            "HTTP",
            "..."
        ]
    },
```

Based on our knowledge of the devices analysed (e.g. a smart TV will mainly do streaming and web browsing), we can create a service map that represents the 'behaviour' of the devices by monitoring the network traffic to and from them.

For this project, I had the opportunity to analyse only one device, mainly dedicated to online streaming activities (YouTube, Netflix....). This is a possible representation of the map of services (arcs are marked by a list of protocols):

![](./output/servmap_graph.png)

## Anomaly
An **anomaly** is defined as *network traffic that differs from that described in the service's map*, for example, traffic may be generated using a protocol never used by that device (to that particular host), or data may be sent/received to/from an unknown host.

To detect anomalies, the flow information generated in real time by the user's network activity is compared with the information in the map:
| Condition | Value returned |
| --------- | -------------- |
| **src_host** is not present within the map (as source ip) | "UNKNOWN_SOURCE_IP" |
| **dst_host** is not present within the map (as dst. ip)   | "UNKNOWN_DESTINATION_IP" |
| **protocol** other than those used by the (src, dst) pair is detected | "PROTOCOL_NEVER_USED" | 
| main **protocol** is DNS or TLS | "DNS/TLS APPLICATION" |
| **protocol** is unknown ("Unknown") |  "UNKNOWN PROTOCOL" |

The last two cases are minor anomalies because they identify atypical network behaviour, but in most cases they don't pose a threat like the other anomalies; for example, if my device starts generating TLS traffic from Ebay, while the only TLS traffic observed on this device is related to Amazon, it is important to notify the user, but it is very unlikely to generate a threat.

I choose not to notify multiple anomalies related to a single flow, but to prioritise one of them; for example, if my device is contacting an unknown local host with an unknown protocol, the only anomaly notified will be "UNKNOWN_DESTINATION_IP", skipping the "UNKNOWN PROTOCOL".

---

:warning: 
This project is tested on a single device. The anomaly detector is very simple and in a real scenario a more complex system should be used. Machine learning or more sophisticated algorithms are typically used for such a task. 
:warning: