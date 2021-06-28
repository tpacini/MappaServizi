# Introduzione
Questo progetto ha come obiettivo la creazione di uno script in grado di rilevare anomalie basandosi su *una mappa dei servizi.* 

L'idea è di: 
1. esaminare il comportamento della rete andando a catturare il traffico e generando, tramite la libreria *nfstream*, i flussi relativi ai pacchetti.

2. creare una mappa dei servizi in base ai flussi e utilizzarla come filtro per individuare eventuali anomalie (protocollo mai osservato all'interno della rete, ip sorgente sconosciuto....)

## Prerequisiti
Per poter eseguire correttamente gli script è necessario installare *nfstream* con il seguente comando:

`sudo pip3 install nfstream`

**IMPORTANTE:** bisogna eseguire il comando con i permessi di superutente.

Durante i test, gli script sono stati eseguiti su una macchina che aveva il ruolo di hotspot. In questo modo connettendo il dispositivo da analizzare alla macchina è possibile catturare i pacchetti dall'interfaccia wifi. 

# Metodologia e risultati
Lo scopo del programma è individuare delle anomalie sulla rete, relative a uno o più dispositivi. Per fare ciò viene utilizzata una mappa dei servizi cioè una struttura dati che descrive quali host hanno comunicato tra di loro e quali protocolli sono stati utilizzati, nel nostro caso ad esempio *10.42.0.130* ha inviato solo richieste DNS a *10.42.0.1* mentre *remote* ha comunicato con *10.42.0.130* solo tramite TLS.

## Mappa dei servizi 
La mappa dei servizi è un file json (*services_map.json*) che ha come chiavi l'ip sorgente, per ogni ip sorgente ci sono n chiavi che rappresentano gli ip destinazione e come valore di ques e come chiavegenerata aggregando i flussi per coppia ip sorgente-destinazione. 

Partendo dal presupposto di sapere quali sono le attività principali svolte dai dispositivi analizzati, ad esempio nel caso di una smart tv, streaming e navigazione web, possiamo creare una mappa dei servizi, che descriva il "comportamento" dei dispositivi, esaminando il traffico di rete in entrata e in uscita.

Per questo progetto è stato analizzato un solo dispositivo dedicato ad attività di streaming online. Eseguendo la cattura del traffico di rete, generato da questo dispositivo per un certo periodo di tempo, otteniamo tramite *nfstream* dei flussi e da questi possiamo poi creare la mappa.   

## Anomalia
Per individuare le anomalie si confrontano le informazioni dei flussi, generati in tempo reale dai pacchetti ricevuti sull'interfaccia di rete, con le informazioni della mappa:
- se l'host sorgente non è presente all'interno della mappa, allora lo script restituirà "UNKNOWN_SOURCE_IP"
- viceversa per l'host destinatario restituirà "UNKNOWN_DESTINATION_IP"
- infine, se gli host sorgente e destinatario si trovano già all'interno della mappa dei servizi, ma viene utilizzato un protocollo diverso da quelli registrati per questa coppia di host, il programma restituirà "PROTOCOL_NEVER_USED"
  - se il protocollo principale è DNS o TLS allora restituisce "DNS/TLS APPLICATION"
  - se il protocollo è sconosciuto ("Unknown") allora restituisce "UNKNOWN PROTOCOL"

Gli ultimi due casi sono delle anomalie di minore importanza, poiché si discostano dalla norma ma sono meno rilevanti rispetto alle altre tre.

Per come è stato implementato il codice, ho deciso di non notificare moltiplici anomalie di un singolo flusso ma di fornire una priorità a ognuna di queste; ad esempio se il mio dispositivo contatta un host locale sconosciuto con un protocollo sconosciuto, l'unica anomalia che notificherà sarà quella di "UNKNOWN_DESTINATION_IP", senza aggiungere anche quella di "UNKNOWN PROTOCOL".

## Test e risultati
Per testare il programma ho inizialmente catturato per circa 60 minuti i flussi generati dal dispositivo dedicato allo streaming, mentre veniva utilizzato in maniera "ideale". Successivamente eseguendo `detect_anomalies.py` ho generato la mappa dei servizi (dai flussi) e poi ho iniziato ad utilizzare il dispositivo, cosicché lo script potesse iniziare ad analizzare i flussi in tempo reale.

Per testare la rilevazione di anomalie, ho iniziato ad esempio a generare traffico torrent o ad aprire sessioni SSH verso host remoti. Inoltre, come previsto, facendo comunicare il dispositivo con una macchina locale mai osservata prima, lo script genera un'anomalia di tipo *ip sorgente/destinatario sconosciuto*.

I risultati ottenuti vengono riassunti nel report, ottenibile eseguendo `detect_anomalies.py` con il flag `-a`, e nei test che ho eseguito sono stati piuttosto soddisfacenti, a parte rarissimi casi (con BitTorrent) in cui il protocollo non veniva riconosciuto da NFStream nei restanti casi il programma è riuscito ad identificare tutte le anomalie.

Nel report vengono rappresentati insieme alla lista dei protocolli utilizzati da un certo host, anche i byte che sono stati ricevuti da questo. 

# Esecuzione
*Nota: Il file `config.json` contiene dei parametri utilizzati dagli script come ad esempio il nome dei file di output.*

Inizialmente eseguire `sudo flows_capture.py -i eth0` per catturare il traffico dall'interfaccia `eth0` e ottenere in output un file contenente i flussi generati. I permessi di superutente sono necessari per attivare la cattura sull'interfaccia di rete.

A questo punto si può eseguire `sudo detect_anomalies.py -i eth0` per generare la mappa dei servizi e per iniziare a catturare i pacchetti attraverso l'interfaccia `eth0`; lo script in tempo reale analizza le informazioni dei flussi, ottenuti dai pacchetti, e controlla la presenza di anomalie. Per ogni flusso analizzato verrà mostrato un risultato:

```
  0. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
  1. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
  2. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
  3. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
  4. 10.42.0.130     --> remote          , TLS                  | NONE
  5. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
  6. 10.42.0.130     --> remote          , HTTP                 | NONE
  7. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
  8. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
  9. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 10. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 11. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 12. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
 13. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 14. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
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

Periodicamente un report delle anomalie viene salvato in locale. Una volta terminata la cattura, è possibile visualizzarlo eseguendo `detect_anomalies.py` con il flag `-a` (*sudo* non necessario):

```
+++++++ NONE anomaly flows +++++++
+ 10.42.0.130     receive  71595235 bytes from: 
         - 10.42.0.1      ,     51994 bytes (0.07%) using ['DNS', 'DNS.AmazonVideo', 'DNS.Amazon', 'DNS.Google', 'DNS.GoogleServices', 'DNS.Microsoft', 'DNS.NetFlix', 'DNS.YouTube']
         - remote         ,  71543241 bytes (99.93%) using ['TLS', 'TLS.Amazon', 'HTTP', 'TLS.AmazonVideo', 'TLS.Google', 'QUIC.Google', 'TLS.YouTube', 'HTTP.Google', 'NTP.UbuntuONE', 'TLS.Cloudflare', 'QUIC.YouTube', 'TLS.GoogleServices']

+++++++ DNS/TLS APPLICATION anomaly flows +++++++
+ 10.42.0.130     receive   1680371 bytes from: 
         - 10.42.0.1      ,      2417 bytes (0.14%) using ['DNS.Wikipedia', 'DNS.UbuntuONE']
         - remote         ,   1677954 bytes (99.86%) using ['TLS.Wikipedia']

+++++++ PROTOCOL NEVER USED anomaly flows +++++++
+ 10.42.0.130     receive     67578 bytes from: 
         - remote         ,     66886 bytes (98.98%) using ['BitTorrent', 'BitTorrent.Amazon', 'ICMP', 'IGMP', 'SSDP', 'SSH']
         - 10.42.0.1      ,       692 bytes (1.02%) using ['DHCP']
+ remote          receive      1399 bytes from: 
         - 10.42.0.130    ,      1399 bytes (100.00%) using ['ICMP', 'ICMP.Amazon']

+++++++ UNKNOWN DESTINATION IP anomaly flows +++++++
+ 10.42.0.130     receive   5154607 bytes from: 
         - 10.42.0.96     ,   5154607 bytes (100.00%) using ['Unknown', 'TLS']

+++++++ UNKNOWN SOURCE IP anomaly flows +++++++
+ 10.42.0.1       receive      2600 bytes from: 
         - 10.42.0.130    ,      2600 bytes (100.00%) using ['ICMP']

+++++++ UNKNOWN PROTOCOL anomaly flows +++++++
+ 10.42.0.130     receive      2040 bytes from: 
         - 10.42.0.1      ,      2040 bytes (100.00%) using ['Unknown']
+ remote          receive      2198 bytes from: 
         - 10.42.0.130    ,      2198 bytes (100.00%) using ['Unknown']

+++++++ On 561 flows, 159 anomalies +++++++
```