# IoT_Smart_Shelves
## Il progetto
Buzz-R è un sistema per la gestione intelligente di
   un evento fieristico

Lo scopo del progetto è quello di rendere gli scaffali
   dei mercanti oggetti intelligenti in grado di interagire e
   cooperare tra loro

Ogni scaffale sarà consapevole del numero di oggetti
   rimasti e comunicherà sia con i mercanti che con i clienti

Utile per:
la cooperazione tra venditori
per massimizzare le vendite 
evitare rimanenze e sprechi
gestire i rifornimenti

# Funzionalità
Rilevare il numero di oggetti presenti sullo scaffale

Mostrare tramite display il numero di rimanenze e il loro prezzo

Notificare tramite led luminoso lo stato di riempimento dello scaffale in base a soglia stabilita dal mercante

Messa in saldo degli oggetti automatica e quindi generazione di offerte per i clienti

Tenere traccia dell’andamento delle vendite tramite Intelligenza Artificiale e quindi programmare i rifornimenti

Gestione delle affinità:
Permette la cooperazione tra scaffali con prodotti affini, ovvero il coordinamento degli sconti di un prodotto sulla base delle scorte rimanenti dei prodotti affini

# A chi potrebbe interessare BUZZ-R ?

Buzz-R è stato realizzato per tutti i venditori di eventi fiersitici che vogliano incrementare le loro vendite in modo intelligente e senza sforzo 

Il suo utilizzo è immediato e non abbisogna di alcuna conoscienza preliminare

Aiuta i venditori a cooperare tra loro aumentando la consapevolezza sulle loro vendite, sulle scorte e sui trend di acquisti seguiti dai clienti

![Screenshot (6)](https://user-images.githubusercontent.com/58270634/190853155-de2ff5b1-6352-42c4-a619-04ecdba90ba8.png)

# Architettura

1) Scaffale e prodotti:
   Microcontrollore e fotoresistenze per rilevare gli oggetti
   3 LED (rosso, giallo,verde) per mostrare il livello di riempimento
   Dispaly per mostrare il prezzo attuale e il numero di oggetti rimasti!
2) Bridge 
     Gli scaffali di un mercante si collegano al Bridge della sua bancarella
     Per ogni bancarella ci sarà un Bridge 
     Collegamento wireless tra scaffale e Bridge nell’architettura finale
     Il Bridge raccoglie i dati riguardanti il numero di oggetti e li invia al server tramite protocollo HTTP
     Il Bridge interroga il Server per chiedere il prezzo del prodotto di uno scaffale
     Dopo aver ottenuto dal Server il prezzo in pacchetto Json, ricava le informazioni e le invia al microcontrollore
3) Server
     E’ unico all’interno della fiera
     Il server gestisce tutte le richieste che provengono dai Bridge delle bancarelle
     Salva tutti i dati raccolti (registrazione utenti, scaffali con prezzi e numero oggetti)
     Comunica con il mercante, il quale dal browser può osservare   lo stato dei suoi scaffali
     Comunica con i clienti tramite server Telegram il quale a sua volta invia a questi ultimi gli sconti attivi o le informazioni utili
     Risponde al Bridge inviando i prezzi aggiornati sulla base degli oggetti rimasti
     Prevede l’andamento delle vendite usando l’intelligenza artificiale e mostra informazioni generali su vendite e rifornimenti
     
     
![Screenshot (8)](https://user-images.githubusercontent.com/58270634/190853284-03313f8e-b009-46ea-a2f7-651205a48255.png)
     
# Sistema di comunicazione BUZZ-R

![Screenshot (10)](https://user-images.githubusercontent.com/58270634/190853599-2ef1fca0-2164-4b88-91d1-1cc39167b639.png)

# Schema del circuito

 Microcontrollore tipo Arduino Uno
 3 fotoresistenze per monitorare assenza/presenza
 3 Led 
 Un display LCD per mostrare il prezzo e numero di oggetti sullo scaffale
 Driver di pilotaggio del display 
 
 ![Screenshot (21)](https://user-images.githubusercontent.com/58270634/190865459-e99f5d06-18de-457e-a22e-25c8a5d7c901.png)

# Dashboard e app Telegram 

![Screenshot (22)](https://user-images.githubusercontent.com/58270634/190865668-fb84a5e4-0c94-4aa3-820b-8c5f2b88f832.png)

# FB-Prophet

Previsioni su andamento vendite future

Genera grafici proiettati a un periodo temporale futuro scelto impostando il parametro period

Per essere utilizzato necessita di un dataset in cui sono presenti due specifiche colonne ‘’ds, y’’

Nel prototipo è stata creata una funzione per l’implementazione di questa classe

![Screenshot (24)](https://user-images.githubusercontent.com/58270634/190867894-055223ef-5d6a-4717-8669-2982cfc90ca3.png)

# Sviluppi futuri 

 1) Utilizzo di sensori più sofisticati per lo scaffale, o rilevamento del numero di oggetti tramite videocamera sfruttando reti neurali come Yolo

 2) Aggiunta dell’accoppiamento automatico tra scaffali 
 
 3) Server totalmente in cloud 

 4) Applicazione proprietaria per i clienti e per i gestori

 5) Presenza di un collegamento diretto con i fornitori 

 6) Aggiunta di un Sistema di sicurezza in grado di evitare sconti illeciti 

 7) Aggiunta di previsioni più puntuali e precise, che tengano conto delle vendite in altre fiere di altre città

 8) Completamento della gestione affinità e della sezione suggerimenti includendo studi basati sui Big Data (market basket analysis applicata a scontrini dei supermercati)

 9) Aggiunta di una bacheca (nella dashboard) che permetta la comunicazione tra venditori registrati in modo da potersi accordare








   









