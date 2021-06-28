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

Durante i test, gli script sono stati eseguiti su una macchina che aveva il ruolo di hotspot. In questo modo connettendo il dispositivo da analizzare all'hotspot, ho potuto catturare i pacchetti dall'interfaccia wifi. 

# Anomalia
Lo scopo del programma è individuare delle anomalie sulla rete, relative a uno o più dispositivi. Per fare ciò viene utilizzata una mappa dei servizi cioè una struttura dati che descrive quali host hanno comunicato tra di loro e quali protocolli sono stati utilizzati, ad esempio, nel nostro caso: *10.42.0.130* ha inviato solo richieste DNS a *10.42.0.1* mentre *remote* ha comunicato con *10.42.0.130* solo tramite TLS.

Partendo dal presupposto di sapere quali sono le attività principali svolte dai dispositivi analizzati, ad esempio nel caso di una smart tv saprò che può avere del traffico NetFlix, DAZN o di altri provider streaming, posso esaminare il traffico di rete in entrata e in uscita da questi e ricavare una mappa dei servizi che descriva il comportamento "ideale" del dispositivo.

Per questo progetto è stato analizzato un solo dispositivo dedicato ad attività di streaming online. Eseguendo la cattura del traffico di rete, generato da questo dispositivo per un certo periodo di tempo, si ottengono dei flussi e da questi si crea la mappa dei servizi.   

Per individuare le anomalie confronto le informazioni dei flussi, generati in tempo reale dai pacchetti ricevuti sull'interfaccia di rete, con le informazioni della mappa:
- se l'host sorgente non è presente all'interno della mappa, allora lo script restituirà "UNKNOWN_SOURCE_IP"
- viceversa per l'host destinatario restituirà "UNKNOWN_DESTINATION_IP"
- infine, se gli host sorgente e destinatario si trovano già all'interno della mappa dei servizi, ma in questo caso è stato utilizzato un protocollo diverso da quello analizzato, il programma restituirà "PROTOCOL_NEVER_USED"

# Esecuzione
*Nota: Il file `config.json` contiene dei parametri utilizzati dagli script come ad esempio il nome dei file di output.*

Inizialmente eseguire `sudo flows_capture.py -i eth0` per catturare il traffico dall'interfaccia `eth0` e ottenere in output un file contenente i flussi generati. I permessi di superutente sono necessari per attivare la cattura sull'interfaccia di rete.

A questo punto si può eseguire `sudo detect_anomalies.py -i eth0` per generare la mappa dei servizi e per iniziare a catturare i pacchetti attraverso l'interfaccia `eth0`; lo script in tempo reale analizza le informazioni dei flussi, ottenuti dai pacchetti, e controlla la presenza di anomalie. Per ogni flusso analizzato verrà mostrato un risultato:

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
+ 10.42.0.130     exchange 208348503 bytes with: 
         - 10.42.0.1      ,    100355 bytes (0.05%) using ['DNS', 'DNS.NetFlix', 'DNS.Amazon', 'DNS', 'DNS.Microsoft', 'DNS.GoogleServices', 'DNS.AmazonVideo', 'DNS.Google', 'DNS.YouTube', 'DNS.Twitch']
         - remote         , 208248148 bytes (99.95%) using ['HTTP', 'TLS.NetFlix', 'HTTP', 'TLS.GoogleServices', 'MDNS', 'TLS.Amazon', 'TLS.AmazonVideo', 'TLS', 'HTTP.Google', 'TLS.Twitch', 'QUIC.YouTube', 'TLS.YouTube', 'QUIC.Google', 'TLS.Google', 'QUIC.GoogleServices', 'HTTP.Amazon', 'QUIC.Cloudflare', 'TLS.Cloudflare']
+ remote          exchange       264 bytes with: 
         - 10.42.0.130    ,       264 bytes (100.00%) using ['TLS.Amazon']

+++++++ PROTOCOL NEVER USED anomaly flows +++++++
+ 10.42.0.130     exchange     20124 bytes with: 
         - remote         ,     18288 bytes (90.88%) using ['IGMP', 'BitTorrent.Amazon', 'BitTorrent', 'IGMP', 'Unknown']
         - 10.42.0.1      ,      1836 bytes (9.12%) using ['Unknown']
+ remote          exchange       181 bytes with: 
         - 10.42.0.130    ,       181 bytes (100.00%) using ['ICMP.Amazon']

+++++++ UNKNOWN DESTINATION IP anomaly flows +++++++

+++++++ UNKNOWN SOURCE IP anomaly flows +++++++
+ 10.42.0.1       exchange      2340 bytes with: 
         - 10.42.0.130    ,      2340 bytes (100.00%) using ['ICMP']

+++++++ On 656 flows, 47 anomalies +++++++
```

