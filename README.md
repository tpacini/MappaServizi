# Introduzione
Questo progetto ha come obiettivo la creazione di uno script in grado di rilevare anomalie basandosi su *una mappa dei servizi.* 

L'idea è di: 
1. esaminare il comportamento della rete andando a catturare il traffico e generando, tramite la libreria *nfstream*, i flussi relativi ai pacchetti.

2. Creare una mappa dei servizi in base ai flussi e utilizzarla come filtro per individuare eventuali anomalie (protocollo mai osservato all'interno della rete, ip sorgente sconosciuto....)

## Prerequisiti
Per poter eseguire correttamente gli script è necessario installare *nfstream* con il seguente comando:

`sudo pip3 install nfstream`

**IMPORTANTE:** bisogna eseguire il comando con i permessi di superutente.

Durante i test, gli script sono stati eseguiti su una macchina che aveva il ruolo di hotspot. In questo modo connettendo il dispositivo da analizzare all'hotspot è possibile catturare i pacchetti dall'interfaccia wifi. 

# Metodologia e risultati

## Cos'è un'anomalia
Lo scopo del programma è individuare delle anomalie sulla rete, relative a uno o più dispositivi. Per fare ciò viene utilizzata una mappa dei servizi cioè una struttura dati che descrive quali host hanno comunicato tra di loro e quali protocolli sono stati utilizzati, nel nostro caso ad esempio *10.42.0.130* ha inviato solo richieste DNS a *10.42.0.1* mentre *remote* ha comunicato con *10.42.0.130* solo tramite TLS.

Partendo dal presupposto di sapere quali sono le attività principali svolte dai dispositivi analizzati, ad esempio nel caso di una smart tv, streaming e navigazione web, posso esaminare il traffico di rete in entrata e in uscita da questi e descrivere il loro comportamento "ideale" con una mappa dei servizi.

Per questo progetto è stato analizzato un solo dispositivo dedicato ad attività di streaming online. Eseguendo la cattura del traffico di rete, generato da questo dispositivo per un certo periodo di tempo, otteniamo tramite *nfstream* dei flussi e da questi possiamo poi creare la mappa.   

Per individuare le anomalie confronto le informazioni dei flussi, generati in tempo reale dai pacchetti ricevuti sull'interfaccia di rete, con le informazioni della mappa:
- se l'host sorgente non è presente all'interno della mappa, allora lo script restituirà "UNKNOWN_SOURCE_IP"
- viceversa per l'host destinatario restituirà "UNKNOWN_DESTINATION_IP"
- infine, se gli host sorgente e destinatario si trovano già all'interno della mappa dei servizi, ma viene utilizzato un protocollo diverso da quelli registrati per questa coppia di host, il programma restituirà "PROTOCOL_NEVER_USED"
  - se il protocollo principale è DNS o TLS allora restituisce "DNS/TLS APPLICATION"
  - se il protocollo è sconosciuto ("Unknown") allora restituisce "UNKNOWN PROTOCOL"

Gli ultimi due casi sono delle anomalie di minore importanza, poiché si discostano dalla norma ma sono meno rilevanti rispetto alle altre tre.

Per come è stato implementato il codice, ho deciso di non notificare moltiplici anomalie di un singolo flusso ma di fornire una priorità a ognuna di queste; ad esempio se il mio dispositivo contatta un host locale sconosciuto con un protocollo sconosciuto, l'unica anomalia che notificherà sarà quella di "UNKNOWN_DESTINATION_IP", senza aggiungere anche quella di "UNKNOWN PROTOCOL".

## Test e risultati ottenuti
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
  4. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
  5. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
  6. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
  7. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
  8. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
  9. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 10. 10.42.0.130     --> 10.42.0.1       , DNS.NetFlix          | NONE
 11. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
 12. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
 13. 10.42.0.130     --> 10.42.0.1       , DNS.Microsoft        | NONE
 14. 10.42.0.130     --> 10.42.0.1       , DNS.NetFlix          | NONE
 15. 10.42.0.130     --> 10.42.0.1       , Unknown              | PROTOCOL NEVER USED
 16. 10.42.0.1       --> 10.42.0.130     , ICMP                 | UNKNOWN SOURCE IP
 17. 10.42.0.130     --> remote          , IGMP                 | PROTOCOL NEVER USED
 18. 10.42.0.130     --> remote          , IGMP                 | PROTOCOL NEVER USED
 19. 10.42.0.130     --> remote          , TLS.NetFlix          | NONE
 20. 10.42.0.130     --> remote          , SSDP                 | PROTOCOL NEVER USED
 21. 10.42.0.130     --> remote          , SSDP                 | PROTOCOL NEVER USED
 22. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 23. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 24. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
... 
344. 10.42.0.130     --> 10.42.0.96      , Unknown              | UNKNOWN DESTINATION IP
345. 10.42.0.130     --> 10.42.0.96      , Unknown              | UNKNOWN DESTINATION IP
346. 10.42.0.130     --> 10.42.0.96      , Unknown              | UNKNOWN DESTINATION IP
347. 10.42.0.130     --> remote          , IGMP                 | PROTOCOL NEVER USED
348. 10.42.0.130     --> remote          , IGMP                 | PROTOCOL NEVER USED
...
553. 10.42.0.130     --> 10.42.0.1       , DNS.Wikipedia        | PROTOCOL NEVER USED
554. 10.42.0.130     --> remote          , TLS.Wikipedia        | PROTOCOL NEVER USED
555. 10.42.0.130     --> remote          , TLS.Wikipedia        | PROTOCOL NEVER USED
556. 10.42.0.130     --> remote          , QUIC.Google          | NONE
557. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
558. 10.42.0.130     --> remote          , QUIC.Google          | NONE
```

Periodicamente un report delle anomalie viene salvato in locale. Una volta terminata la cattura, è possibile visualizzarlo eseguendo `detect_anomalies.py` con il flag `-a` (*sudo* non necessario):

```
+++++++ NONE anomaly flows +++++++
+ 10.42.0.130     exchange  81181970 bytes with: 
	 - 10.42.0.1      ,     40464 bytes (0.05%) using ['DNS', 'DNS', 'DNS.Amazon', 'DNS.NetFlix', 'DNS.AmazonVideo', 'DNS.Google', 'DNS.Microsoft', 'DNS.GoogleServices', 'DNS.YouTube']
	 - remote         ,  81141506 bytes (99.95%) using ['TLS.Amazon', 'TLS.NetFlix', 'HTTP', 'TLS.YouTube', 'HTTP.Google', 'TLS.Google', 'TLS', 'QUIC.YouTube', 'TLS.Amazon', 'QUIC.Google', 'TLS.Cloudflare', 'TLS.GoogleServices']
+ remote          exchange       691 bytes with: 
	 - 10.42.0.130    ,       691 bytes (100.00%) using ['TLS', 'TLS']

+++++++ PROTOCOL NEVER USED anomaly flows +++++++
+ 10.42.0.130     exchange   2919729 bytes with: 
	 - 10.42.0.1      ,      7124 bytes (0.24%) using ['Unknown', 'DNS.Wikipedia', 'Unknown', 'DNS.Github', 'DNS.Reddit']
	 - remote         ,   2912605 bytes (99.76%) using ['IGMP', 'IGMP', 'SSDP', 'BitTorrent', 'HTTP.GoogleServices', 'BitTorrent.Amazon', 'QUIC.GoogleServices', 'SSH', 'Unknown', 'TLS.Wikipedia', 'TLS.Github', 'TLS.Reddit']
+ remote          exchange      2742 bytes with: 
	 - 10.42.0.130    ,      2742 bytes (100.00%) using ['ICMP', 'ICMP.Amazon', 'ICMP', 'TLS.Amazon']

+++++++ UNKNOWN DESTINATION IP anomaly flows +++++++
+ 10.42.0.130     exchange     31904 bytes with: 
	 - 10.42.0.96     ,     31904 bytes (100.00%) using ['Unknown', 'Unknown']

+++++++ UNKNOWN SOURCE IP anomaly flows +++++++
+ 10.42.0.1       exchange      4940 bytes with: 
	 - 10.42.0.130    ,      4940 bytes (100.00%) using ['ICMP', 'ICMP']

+++++++ On 611 flows, 268 anomalies +++++++
```

eseguito la cattura utilizzando normalmente il dispositivo e poi aspettando 2 minuti (idle timeout) per poter far terminare gli ultimi flussi