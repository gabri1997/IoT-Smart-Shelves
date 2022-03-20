from threading import Thread
import config
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import datetime
from fk import FlaskThread
#from prophet import df, id_shelves, data_prophet
import pandas as pd

#2 Database che servono: generale e quello con lo sconto
prod_shelves_csv = './data/products_shelves.csv'
columns_prod_shelves = ['user','prodotto','prezzo','prezzoscontato','soglia']
prod_shelves = pd.read_csv(prod_shelves_csv, sep=';')

data_file= "./data/data.csv"
data_columns = ["id_shelf", "prodotto", "proprietario", "anno", "mese", "giorno", "ora", "min", "sec", "stato"]

BOTKEY=config.KEY(self=config)
chatId=config.chatID(self=config)
print(chatId)
#sconto = False
#controllo lo stato e setto il prezzo
def check_status(prod_shelves,last_element):

    sconto=False
    product = prod_shelves[prod_shelves['prodotto'] == last_element['prodotto']]
    soglia = product['soglia'].iloc[0]
    #se siamo sotto la soglia scelta dall'utente allora andiamo a settare il nuovo prezzo
    if last_element['stato'] == 0:
        sconto=False
        return -1,sconto
    elif last_element['stato'] <= soglia:
        sconto=True
        return prod_shelves[prod_shelves['prodotto'] == last_element['prodotto']]['prezzoscontato'].iloc[0],sconto

    return prod_shelves[prod_shelves['prodotto'] == last_element['prodotto']]['prezzo'].iloc[0],sconto



class startThread(Thread):
    def __init__(self, nome, up, idchat):
        self.loc = nome
        self.updater = up
        self.idc = idchat
        Thread.__init__(self)

    def run(self):
        exit_process= False
        while exit_process == False:
            print("Thread partito")
            # prima bisogna controllare che la data sia quella del giorno odierno, partendo dal presupposto che al mattino rifornisco gli
            # scaffali e che quindi nessun prodotto possa partire in promozione senza prima aver venduto qualche colle
            #Quando premo start, dovrei vedere per ogni ID, se il prodotto è in promozione e anche il costo stesso dell'oggetto
            #Per ogni ID chat, controlla sul data.csv l'ultimo record per ciascuno (perchè potrebbero esserci più scaffali di pasta)
            #Se lo stato è sotto a 2
            #Controllo nel dataset quanto è il prezzo in promozione settato da utente
            #Lo elenco su telegram

            date_now = datetime.datetime.now()
            df = pd.read_csv(data_file,sep=';')
            if (date_now.year == df['anno'].iloc[-1]) & (date_now.month == df["mese"].iloc[-1]) & (date_now.day == df["giorno"].iloc[-1]):

                #Df è il dataset generale
                utenti = df["proprietario"].unique()
                #Inizio il ciclo prendendo ogni utente del dataset generale e per ognuno faccio il confronto con
                #quelli presenti nel dataset product_shelves.csv
                #DEVONO CORRSIPONDERE I NOMI E I PRODOTTI, MAIUSCOLE COMPRESE, ALTRIMENTI DA UN ERRORE (INDEX OUT OF BOUNDS
                #E NON TROVA LA CORRISPONDENZA
                for u in utenti:
                        last_element = df[df['proprietario'] == u].iloc[-1]
                        prodotto=last_element["prodotto"]
                        prezzo_scontato=prod_shelves[prod_shelves['prodotto'] == prodotto]['prezzoscontato'].iloc[0]
                        prezzo_originale=prod_shelves[prod_shelves['prodotto'] == prodotto]['prezzo'].iloc[0]
                        coordinate=prod_shelves[prod_shelves['prodotto'] == prodotto]['coordinate'].iloc[0]
                        price_value = check_status(prod_shelves, last_element)[0]
                        sconto=check_status(prod_shelves, last_element)[1]
                        if price_value == -1:
                            price = 'FINISHED'
                            self.updater.bot.send_message(chat_id=self.idc, text=f"C'ERI QUASI! Il venditore {u} ha terminato il prodotto : {prodotto}; ", timeout=1)
                        else:
                            if (sconto==False):
                                price = 'Price ' + str(price_value) + ' $'
                                self.updater.bot.send_message(chat_id=self.idc,
                                                              text=f"Il venditore {u} NON ha sconti sul prodotto : {prodotto}; prezzo: {prezzo_originale} euro",
                                                              timeout=1)
                            else:
                                self.updater.bot.send_message(chat_id=self.idc,
                                                              text=f"Il venditore {u} ha messo in sconto il prodotto : {prodotto}; da {prezzo_originale} euro --> {prezzo_scontato} euro, {coordinate} / AFFRETTATI!",
                                                              timeout=1)
                        exit_process = True
            else:
                print("La data non corrisponde")
                self.updater.bot.send_message(chat_id=self.idc, text="Per oggi non ci sono ancora promozioni", timeout=1)
                exit_process = True

#comando telegram per vedere l'ultimo stato per ogni prodotto
class statusThread(Thread):
    def __init__(self, nome, up, idchat):
        self.loc = nome
        self.updater = up
        self.idc = idchat
        Thread.__init__(self)

    def run(self):
        exit_process= False
        while exit_process == False:
            data = pd.read_csv(data_file,sep=';')
            for i in range(len(prod_shelves)):
                venditore = prod_shelves.iloc[i]['user']
                id_shelf = prod_shelves.iloc[i]['id_shelf']
                obj = data[(data['proprietario'] == venditore)].iloc[-1]
                prodotto = obj['prodotto']
                ore = obj['ora']
                min = obj['min']
                giorno = obj['giorno']
                mese= obj['mese']
                anno = obj['anno']
                stato = int(obj['stato'])
                if min < 10:
                    min = '0' + str(min)
                self.updater.bot.send_message(chat_id=self.idc,
                                              text=f"Il prodotto: \"{prodotto}\" venduto da \"{venditore}\"\n"
                                                   f"sono presenti ancora {stato} oggetti\n"
                                                   f"ultimo aggiornamento alle {ore}:{min} del {giorno}/{mese}/{anno}",
                                              timeout=1)

            exit_process = True



# comando telegram per richiedere i prodotti
class prodottiThread(Thread):
    def __init__(self, nome, up, idchat):
        self.loc = nome
        self.updater = up
        self.idc = idchat
        Thread.__init__(self)

    def run(self):
        exit_process= False
        while exit_process == False:
            print("Thread prodotti partito")
            if len(prod_shelves) == 0:
                self.updater.bot.send_message(chat_id=self.idc,
                                              text=f"Nel sistema non sono presenti prodotti registrati!",
                                              timeout=1)
            else:
                for i in range(len(prod_shelves)):
                    print(prod_shelves.iloc[i])
                    prodotto = prod_shelves.iloc[i]['prodotto']
                    venditore = prod_shelves.iloc[i]['user']
                    prezzo = prod_shelves.iloc[i]['prezzo']
                    luogo = prod_shelves.iloc[i]['coordinate']
                    self.updater.bot.send_message(chat_id=self.idc,
                                                  text=f"Il prodotto: \"{prodotto}\" venduto da \"{venditore}\""
                                                       f"al prezzo di {prezzo} $\nsi trova presso {luogo}; ",
                                                  timeout=1)
            exit_process = True



def start(update,context):
    chatId = update.effective_chat.id
    ph=startThread("shelf", updater, chatId)
    ph.start()

def status(update,context):
    chatId = update.effective_chat.id
    ph = statusThread("shelf", updater, chatId)
    ph.start()

def prodotti(update,context):
    chatId = update.effective_chat.id
    ph = prodottiThread("shelf", updater, chatId)
    ph.start()

def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('I comandi possibili sono /start, /status, /prodotti')

"""
def echo(update, context):
    #Echo the user message.

    chatid = update.effective_chat.id
    receivedmessage = update.message.text
    sendmessage = ' I received: ' + receivedmessage
    updater.bot.send_message (chat_id=chatid, text=sendmessage)
    print (chatid)
    # sample2: update.message.reply_text(update.message.text)
"""

def botMain():
    global updater

    updater=Updater(BOTKEY, use_context=True) #Oggetto principale per la gestione del Bot
    dp=updater.dispatcher #Oggetto per l'aggiunta degli handler, un handler è una funzione che viene richiamata quando mi arrivano dei messaggi

    #handler messaggi
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("prodotti",prodotti))
    dp.add_handler(CommandHandler("help",help_command))


    # add an handler for messages
    #dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling() #Funzione non bloccante che attiva la ricezione dei messaggi da telegram
    updater.idle()          #Funzione bloccante

if __name__=='__main__':
    #Il servizio flask è in un thread
    #perchè il gestore di telegram deve stare per forza nel thread principale
    thread=FlaskThread("flask")
    thread.start()
    botMain()

