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
 15. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 16. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
 17. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
 18. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
 19. 10.42.0.130     --> remote          , TLS                  | NONE
 20. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
 21. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
 22. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
 23. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
 24. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
 25. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
 26. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
 27. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
 28. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
 29. 10.42.0.130     --> remote          , TLS.Google           | NONE
 30. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
 31. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 32. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
 33. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
 34. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 35. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 36. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 37. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 38. 10.42.0.130     --> remote          , TLS                  | NONE
 39. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
 40. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
 41. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 42. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 43. 10.42.0.130     --> remote          , HTTP                 | NONE
 44. 10.42.0.130     --> remote          , HTTP                 | NONE
 45. 10.42.0.130     --> remote          , HTTP                 | NONE
 46. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
 47. 10.42.0.130     --> remote          , TLS.Google           | NONE
 48. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
 49. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 50. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
 51. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 52. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 53. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 54. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 55. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 56. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 57. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 58. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 59. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 60. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
 61. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 62. 10.42.0.130     --> remote          , QUIC.Google          | NONE
 63. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
 64. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
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
 77. 10.42.0.130     --> remote          , TLS.Google           | NONE
 78. 10.42.0.130     --> remote          , TLS.Google           | NONE
 79. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
 80. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
 81. 10.42.0.130     --> 10.42.0.1       , DNS.Wikipedia        | DNS/TLS APPLICATION
 82. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
 83. 10.42.0.130     --> remote          , HTTP                 | NONE
 84. 10.42.0.130     --> 10.42.0.1       , DNS.Wikipedia        | DNS/TLS APPLICATION
 85. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 86. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 87. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
 88. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
 89. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
 90. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
 91. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
 92. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 93. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
 94. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
 95. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
 96. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 97. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 98. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
 99. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
100. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
101. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
102. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
103. remote          --> 10.42.0.130     , ICMP                 | PROTOCOL NEVER USED
104. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
105. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
106. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
107. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
108. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
109. remote          --> 10.42.0.130     , ICMP                 | PROTOCOL NEVER USED
110. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
111. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
112. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
113. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
114. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
115. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
116. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
117. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
118. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
119. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
120. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
121. remote          --> 10.42.0.130     , ICMP                 | PROTOCOL NEVER USED
122. 10.42.0.130     --> remote          , TLS                  | NONE
123. 10.42.0.130     --> 10.42.0.1       , DNS.Wikipedia        | DNS/TLS APPLICATION
124. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
125. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
126. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
127. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
128. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
129. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
130. 10.42.0.130     --> remote          , HTTP.Google          | NONE
131. 10.42.0.130     --> remote          , ICMP                 | PROTOCOL NEVER USED
132. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
133. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
134. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
135. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
136. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
137. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
138. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
139. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
140. 10.42.0.130     --> remote          , TLS                  | NONE
141. 10.42.0.130     --> remote          , TLS                  | NONE
142. 10.42.0.130     --> 10.42.0.1       , DNS.GoogleServices   | NONE
143. 10.42.0.130     --> 10.42.0.1       , DNS.GoogleServices   | NONE
144. 10.42.0.130     --> remote          , TLS                  | NONE
145. 10.42.0.130     --> remote          , TLS                  | NONE
146. 10.42.0.130     --> remote          , TLS                  | NONE
147. 10.42.0.130     --> remote          , TLS                  | NONE
148. 10.42.0.130     --> remote          , HTTP.Google          | NONE
149. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
150. 10.42.0.130     --> remote          , TLS                  | NONE
151. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
152. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
153. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
154. 10.42.0.130     --> remote          , TLS                  | NONE
155. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
156. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
157. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
158. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
159. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
160. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
161. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
162. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
163. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
164. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
165. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
166. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
167. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
168. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
169. 10.42.0.130     --> remote          , TLS                  | NONE
170. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
171. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
172. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
173. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
174. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
175. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
176. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
177. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
178. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
179. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
180. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
181. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
182. 10.42.0.130     --> 10.42.0.1       , DNS.UbuntuONE        | DNS/TLS APPLICATION
183. 10.42.0.130     --> remote          , NTP.UbuntuONE        | NONE
184. 10.42.0.130     --> remote          , NTP.UbuntuONE        | NONE
185. 10.42.0.130     --> remote          , TLS                  | NONE
186. 10.42.0.130     --> 10.42.0.1       , DNS.Microsoft        | NONE
187. 10.42.0.130     --> remote          , HTTP                 | NONE
188. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
189. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
190. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
191. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
192. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
193. 10.42.0.130     --> 10.42.0.1       , DNS.NetFlix          | NONE
194. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
195. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
196. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
197. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
198. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
199. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
200. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
201. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
202. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
203. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
204. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
205. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
206. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
207. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
208. 10.42.0.130     --> remote          , TLS                  | NONE
209. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
210. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
211. 10.42.0.130     --> remote          , TLS                  | NONE
212. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
213. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
214. 10.42.0.130     --> remote          , TLS.Google           | NONE
215. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
216. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
217. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
218. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
219. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
220. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
221. 10.42.0.130     --> remote          , TLS                  | NONE
222. 10.42.0.130     --> remote          , TLS                  | NONE
223. 10.42.0.130     --> remote          , TLS                  | NONE
224. 10.42.0.130     --> remote          , HTTP.Google          | NONE
225. 10.42.0.130     --> remote          , TLS                  | NONE
226. 10.42.0.130     --> remote          , TLS                  | NONE
227. 10.42.0.130     --> remote          , HTTP                 | NONE
228. 10.42.0.130     --> remote          , HTTP                 | NONE
229. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
230. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
231. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
232. 10.42.0.130     --> remote          , HTTP.Google          | NONE
233. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
234. 10.42.0.130     --> remote          , HTTP.Google          | NONE
235. 10.42.0.130     --> remote          , TLS.Google           | NONE
236. 10.42.0.130     --> remote          , TLS.Google           | NONE
237. 10.42.0.130     --> remote          , TLS.Google           | NONE
238. 10.42.0.130     --> remote          , TLS.Google           | NONE
239. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
240. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
241. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
242. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
243. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
244. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
245. 10.42.0.130     --> remote          , IGMP                 | PROTOCOL NEVER USED
246. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
247. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
248. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
249. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
250. 10.42.0.130     --> remote          , SSDP                 | PROTOCOL NEVER USED
251. 10.42.0.130     --> remote          , SSDP                 | PROTOCOL NEVER USED
252. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
253. 10.42.0.130     --> 10.42.0.1       , Unknown              | UNKNOWN PROTOCOL
254. 10.42.0.1       --> 10.42.0.130     , ICMP                 | UNKNOWN SOURCE IP
255. 10.42.0.130     --> remote          , QUIC.Google          | NONE
256. 10.42.0.130     --> remote          , HTTP                 | NONE
257. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
258. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
259. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
260. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
261. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
262. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
263. remote          --> 10.42.0.130     , ICMP.Amazon          | PROTOCOL NEVER USED
264. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
265. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
266. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
267. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
268. 10.42.0.130     --> remote          , TLS.Cloudflare       | NONE
269. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
270. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
271. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
272. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
273. 10.42.0.130     --> remote          , TLS.Google           | NONE
274. 10.42.0.130     --> 10.42.0.1       , DNS.YouTube          | NONE
275. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
276. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
277. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
278. 10.42.0.130     --> remote          , TLS.Google           | NONE
279. 10.42.0.130     --> remote          , TLS.Google           | NONE
280. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
281. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
282. 10.42.0.130     --> remote          , TLS.Google           | NONE
283. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
284. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
285. 10.42.0.130     --> remote          , TLS.Google           | NONE
286. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
287. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
288. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
289. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
290. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
291. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
292. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
293. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
294. 10.42.0.130     --> remote          , TLS                  | NONE
295. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
296. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
297. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
298. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
299. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
300. remote          --> 10.42.0.130     , ICMP                 | PROTOCOL NEVER USED
301. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
302. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
303. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
304. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
305. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
306. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
307. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
308. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
309. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
310. remote          --> 10.42.0.130     , ICMP                 | PROTOCOL NEVER USED
311. 10.42.0.130     --> remote          , HTTP                 | NONE
312. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
313. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
314. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
315. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
316. 10.42.0.130     --> remote          , TLS                  | NONE
317. 10.42.0.130     --> remote          , TLS                  | NONE
318. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
319. 10.42.0.130     --> remote          , TLS                  | NONE
320. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
321. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
322. remote          --> 10.42.0.130     , ICMP                 | PROTOCOL NEVER USED
323. 10.42.0.130     --> remote          , QUIC.Google          | NONE
324. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
325. 10.42.0.130     --> remote          , QUIC.Google          | NONE
326. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
327. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
328. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
329. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
330. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
331. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
332. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
333. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
334. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
335. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
336. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
337. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
338. 10.42.0.130     --> remote          , TLS                  | NONE
339. 10.42.0.130     --> remote          , HTTP.Google          | NONE
340. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
341. 10.42.0.130     --> remote          , TLS                  | NONE
342. 10.42.0.130     --> remote          , TLS                  | NONE
343. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
344. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
345. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
346. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
347. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
348. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
349. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
350. 10.42.0.130     --> remote          , TLS                  | NONE
351. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
352. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
353. 10.42.0.130     --> remote          , TLS                  | NONE
354. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
355. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
356. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
357. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
358. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
359. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
360. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
361. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
362. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
363. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
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
377. 10.42.0.130     --> remote          , HTTP                 | NONE
378. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
379. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
380. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
381. 10.42.0.130     --> remote          , TLS                  | NONE
382. 10.42.0.130     --> 10.42.0.1       , DNS.NetFlix          | NONE
383. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
384. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
385. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
386. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
387. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
388. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
389. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
390. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
391. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
392. 10.42.0.130     --> remote          , TLS                  | NONE
393. 10.42.0.130     --> remote          , TLS                  | NONE
394. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
395. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
396. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
397. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
398. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
399. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
400. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
401. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
402. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
403. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
404. 10.42.0.130     --> remote          , HTTP.Google          | NONE
405. 10.42.0.130     --> remote          , HTTP.Google          | NONE
406. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
407. 10.42.0.130     --> remote          , TLS                  | NONE
408. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
409. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
410. 10.42.0.130     --> remote          , HTTP.Google          | NONE
411. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
412. 10.42.0.130     --> remote          , HTTP                 | NONE
413. 10.42.0.130     --> remote          , QUIC.Google          | NONE
414. 10.42.0.130     --> remote          , HTTP                 | NONE
415. 10.42.0.130     --> remote          , HTTP                 | NONE
416. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
417. 10.42.0.130     --> remote          , TLS.Google           | NONE
418. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
419. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
420. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
421. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
422. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
423. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
424. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
425. 10.42.0.130     --> remote          , IGMP                 | PROTOCOL NEVER USED
426. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
427. 10.42.0.130     --> remote          , TLS.Amazon           | NONE
428. 10.42.0.130     --> remote          , HTTP                 | NONE
429. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
430. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
431. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
432. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
433. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
434. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
435. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
436. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
437. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
438. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
439. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
440. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
441. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
442. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
443. 10.42.0.130     --> remote          , QUIC.Google          | NONE
444. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
445. 10.42.0.130     --> remote          , QUIC.Google          | NONE
446. 10.42.0.130     --> 10.42.0.1       , DNS.YouTube          | NONE
447. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
448. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
449. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
450. 10.42.0.130     --> 10.42.0.1       , DNS.Wikipedia        | DNS/TLS APPLICATION
451. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
452. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
453. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
454. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
455. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
456. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
457. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
458. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
459. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
460. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
461. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
462. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
463. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
464. 10.42.0.130     --> remote          , TLS                  | NONE
465. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
466. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
467. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
468. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
469. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
470. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
471. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
472. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
473. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
474. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
475. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
476. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
477. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
478. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
479. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
480. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
481. 10.42.0.130     --> remote          , HTTP                 | NONE
482. 10.42.0.130     --> remote          , HTTP                 | NONE
483. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
484. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
485. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
486. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
487. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
488. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
489. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
490. remote          --> 10.42.0.130     , ICMP                 | PROTOCOL NEVER USED
491. 10.42.0.130     --> remote          , BitTorrent           | PROTOCOL NEVER USED
492. 10.42.0.130     --> remote          , HTTP                 | NONE
493. 10.42.0.130     --> remote          , TLS                  | NONE
494. 10.42.0.130     --> 10.42.0.1       , DNS.Wikipedia        | DNS/TLS APPLICATION
495. 10.42.0.130     --> 10.42.0.1       , DNS.Wikipedia        | DNS/TLS APPLICATION
496. 10.42.0.130     --> 10.42.0.1       , DNS.Wikipedia        | DNS/TLS APPLICATION
497. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
498. 10.42.0.130     --> remote          , TLS                  | NONE
499. 10.42.0.130     --> 10.42.0.1       , DNS.Wikipedia        | DNS/TLS APPLICATION
500. 10.42.0.130     --> 10.42.0.1       , DNS.Wikipedia        | DNS/TLS APPLICATION
501. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
502. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
503. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
504. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
505. 10.42.0.130     --> remote          , TLS.Wikipedia        | DNS/TLS APPLICATION
506. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
507. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
508. 10.42.0.130     --> remote          , QUIC.YouTube         | NONE
509. 10.42.0.130     --> remote          , TLS.Google           | NONE
510. 10.42.0.130     --> remote          , TLS.Google           | NONE
511. 10.42.0.130     --> remote          , TLS.Google           | NONE
512. 10.42.0.130     --> remote          , TLS.Google           | NONE
513. 10.42.0.130     --> remote          , TLS.Google           | NONE
514. 10.42.0.130     --> remote          , TLS.Google           | NONE
515. 10.42.0.130     --> remote          , TLS.Google           | NONE
516. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
517. 10.42.0.130     --> 10.42.0.1       , DNS.Google           | NONE
518. 10.42.0.130     --> 10.42.0.1       , DNS.YouTube          | NONE
519. 10.42.0.130     --> 10.42.0.1       , DNS.YouTube          | NONE
520. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
521. 10.42.0.130     --> remote          , TLS.YouTube          | NONE
522. 10.42.0.130     --> remote          , HTTP.Google          | NONE
523. 10.42.0.130     --> remote          , QUIC.YouTube         | NONE
524. 10.42.0.130     --> remote          , QUIC.YouTube         | NONE
525. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
526. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
527. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
528. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
529. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
530. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
531. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
532. 10.42.0.130     --> remote          , TLS                  | NONE
533. 10.42.0.130     --> remote          , TLS                  | NONE
534. 10.42.0.130     --> remote          , TLS                  | NONE
535. 10.42.0.130     --> remote          , TLS.GoogleServices   | NONE
536. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
537. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
538. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
539. 10.42.0.130     --> 10.42.0.1       , DNS.Amazon           | NONE
540. 10.42.0.130     --> remote          , TLS                  | NONE
541. 10.42.0.130     --> remote          , TLS                  | NONE
542. 10.42.0.130     --> remote          , TLS                  | NONE
543. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
544. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
545. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
546. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
547. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
548. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
549. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
550. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
551. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
552. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
553. 10.42.0.130     --> remote          , TLS.AmazonVideo      | NONE
554. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
555. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
556. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
557. 10.42.0.130     --> 10.42.0.1       , DNS                  | NONE
558. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
559. 10.42.0.130     --> 10.42.0.1       , DNS.AmazonVideo      | NONE
560. 10.42.0.130     --> remote          , NTP.UbuntuONE        | NONE
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