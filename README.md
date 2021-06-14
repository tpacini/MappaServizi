Dopo aver eseguito la cattura dei flussi generati dal dispositivo, utilizzando lo script "flows_capture.py"

Analizzo il file ".csv" generato ed estraggo la lista dei protocolli utilizzati dal dispositivo, utilizzando il notebook, che poi diventerà uno script in python, "flows_analysis". 

Infine sfruttando lo script "detect_anomalies.py" analizzo i flussi generati dal dispositivo, soprattutto i protocolli a cui questi flussi fanno riferimento, così da generare un avviso nel caso in cui l'application name di un certo flusso non faccia parte della lista dei protocolli. 