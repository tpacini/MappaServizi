# Introduzione
Questo progetto ha come obiettivo la creazione di uno script in grado di rilevare anomalie basandosi su *una mappa dei servizi.* 

L'idea è di: 
1. esaminare il comportamento della rete andando a catturare il traffico e generando, tramite la libreria *nfstream*, i flussi relativi ai pacchetti.

2. Creare una mappa dei servizi in base ai flussi e utilizzarla come filtro per individuare eventuali anomalie (protocollo mai osservato all'interno della rete, ip sorgente sconosciuto....)


In questo caso è stato analizzato un solo dispositivo, e la mappa dei servizi che otteniamo può essere rappresentata da un grafo in cui i nodi sono gli host locali (gli host remoti sono stati aggregati utilizzando l'indirizzo "remote") e gli archi indicano che i nodi hanno ricevuto/inviato dei dati:

![graph](/output/servmap_graph.png)


## Prerequisiti
Per poter eseguire correttamente gli script è necessario installare *nfstream* con il seguente comando:

`sudo pip3 install nfstream`

**IMPORTANTE:** bisogna eseguire il comando con i permessi di superutente.

# Esecuzione
*Nota: Il file `config.json` contiene dei parametri utilizzati dagli script come ad esempio il nome dei file di output.*

Inizialmente eseguire `sudo flows_capture.py -i eth0` per catturare il traffico dall'interfaccia `eth0` e ottenere in output un file contenente i flussi generati. I permessi di superutente sono necessari per attivare la cattura sull'interfaccia di rete.

A questo punto si può eseguire `sudo detect_anomalies.py -i eth0` per generare una mappa dei servizi, che descrive il "comportamento" (ip sorgente, ip destinazione e protocollo utilizzato) dei dispositivi analizzati, e per iniziare a catturare i pacchetti attraverso l'interfaccia `eth0`; lo script in tempo reale analizza le informazioni dei flussi, ottenuti dai pacchetti, e controlla la presenza di anomalie. Per ogni flusso analizzato verrà mostrato un risultato:

```
1.  10.42.0.130     --> remote          , TLS.Twitch           | NONE
2.  10.42.0.130     --> remote          , TLS.Twitch           | NONE
3.  10.42.0.130     --> remote          , TLS.Twitch           | NONE
4.  10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
5.  10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
6.  10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
7.  10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
8.  10.42.0.130     --> remote          , STUN                 | PROTOCOL NEVER USED
9.  10.42.0.130     --> remote          , ICMP                 | PROTOCOL NEVER USED

10.  10.42.0.130     --> remote          , TLS.eBay             | PROTOCOL NEVER USED
11.  10.42.0.130     --> 10.42.0.1       , DNS.eBay             | PROTOCOL NEVER USED
12.  10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
13.  10.42.0.130     --> remote          , HTTP                 | NONE

14.  fe80::aba5:3795:c21b:6a98 --> ff02::fb        , MDNS                 | NONE
15.  10.42.0.1       --> remote          , MDNS                 | NONE
16.  10.42.0.130     --> remote          , MDNS                 | NONE
17.  ::              --> ff02::1:ffb9:81ba , ICMPV6               | UNKNOWN SOURCE IP
18.  10.42.0.1       --> 10.42.0.96      , ICMP                 | UNKNOWN DESTINATION IP
19.  10.42.0.96      --> remote          , IGMP                 | UNKNOWN SOURCE IP
20.  10.42.0.96      --> remote          , HTTP.Google          | UNKNOWN SOURCE IP
21.  10.42.0.96      --> 10.42.0.1       , DNS.GoogleServices   | UNKNOWN SOURCE IP
22.  10.42.0.96      --> remote          , TLS.GoogleServices   | UNKNOWN SOURCE IP
23.  fe80::2a16:7fff:feb9:81ba --> ff02::16        , ICMPV6               | UNKNOWN SOURCE IP
24.  remote          --> remote          , DHCP                 | UNKNOWN DESTINATION IP
25.  fe80::2a16:7fff:feb9:81ba --> ff02::16        , ICMPV6               | UNKNOWN SOURCE IP
```

Periodicamente un report delle anomalie viene salvato in locale. Una volta terminata la cattura, è possibile visualizzarlo eseguendo `detect_anomalies.py` con il flag `-a` (*sudo* non necessario):

```
+++++++ NONE anomaly flows +++++++
+ 10.42.0.130     exchange 149298689 bytes with: 
	 - 10.42.0.1      ,    108465 bytes (0.07%) using ['DNS', 'DNS', 'DNS.NetFlix', 'DNS.AmazonVideo', 'DNS.Twitch', 'DNS.GoogleServices', 'DNS.Amazon', 'DNS.Google', 'DNS.YouTube', 'DNS.Microsoft']
	 - remote         , 149190224 bytes (99.93%) using ['TLS.Twitch', 'MDNS', 'HTTP', 'TLS', 'TLS.Twitch', 'QUIC.Google', 'TLS.Google', 'QUIC.GoogleServices', 'TLS.Amazon', 'TLS.AmazonVideo', 'TLS.GoogleServices', 'HTTP.Google', 'QUIC.YouTube', 'TLS.YouTube', 'HTTP.Cloudflare', 'ICMP.Google']
+ fe80::aba5:3795:c21b:6a98 exchange       663 bytes with: 
	 - ff02::fb       ,       663 bytes (100.00%) using ['MDNS', 'MDNS']
+ 10.42.0.1       exchange       603 bytes with: 
	 - remote         ,       603 bytes (100.00%) using ['MDNS', 'MDNS']
+ fe80::2cd0:25b4:1b3b:5169 exchange       642 bytes with: 
	 - ff02::fb       ,       642 bytes (100.00%) using ['MDNS', 'MDNS']
+ remote          exchange       330 bytes with: 
	 - 10.42.0.130    ,       330 bytes (100.00%) using ['TLS.Amazon']

+++++++ PROTOCOL NEVER USED anomaly flows +++++++
+ 10.42.0.130     exchange  64890324 bytes with: 
	 - remote         ,  64880257 bytes (99.98%) using ['STUN', 'ICMP', 'NTP.UbuntuONE', 'TLS.eBay', 'STUN', 'Playstation', 'HTTP.UbuntuONE']
	 - 10.42.0.1      ,     10067 bytes (0.02%) using ['DNS.eBay', 'DNS.eBay', 'DNS.UbuntuONE', 'DNS.Facebook']

+++++++ UNKNOWN DESTINATION IP anomaly flows +++++++
+ 10.42.0.1       exchange        62 bytes with: 
	 - 10.42.0.96     ,        62 bytes (100.00%) using ['ICMP']
+ remote          exchange      2112 bytes with: 
	 - remote         ,      2112 bytes (100.00%) using ['DHCP']

+++++++ UNKNOWN SOURCE IP anomaly flows +++++++
+ ::              exchange       432 bytes with: 
	 - ff02::1:ffb9:81ba,       172 bytes (39.81%) using ['ICMPV6', 'ICMPV6']
	 - ff02::16       ,       260 bytes (60.19%) using ['ICMPV6']
+ 10.42.0.96      exchange     20584 bytes with: 
	 - remote         ,     19641 bytes (95.42%) using ['IGMP', 'HTTP.Google', 'TLS.GoogleServices', 'Facebook', 'TLS.YouTube']
	 - 10.42.0.1      ,       943 bytes (4.58%) using ['DNS.GoogleServices', 'DNS.GoogleServices', 'DNS.YouTube']
+ fe80::2a16:7fff:feb9:81ba exchange      1620 bytes with: 
	 - ff02::16       ,      1620 bytes (100.00%) using ['ICMPV6', 'ICMPV6']

+++++++ On 996 flows, 105 anomalies +++++++
```

