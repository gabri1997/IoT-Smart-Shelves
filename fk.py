import pandas as pd
from flask import Flask, url_for, jsonify
from config import Config
import matplotlib.pyplot as plt
from flask import render_template, request, redirect, render_template, request, session, abort, flash
import datetime
from fbprophet import Prophet
# from serverHTTP.prophet import previsioni
from threading import Thread
import json
from checker import Checker
from templates import *

users_csv = './data/users.csv'
columns_users = ['email', 'username', 'password']

shelves_csv = './data/shelves.csv'
columns_shelves = ['id_shelf', 'prodotto', 'user']

data_csv = './data/data.csv'
colums_dataset = ['id_shelf', 'prodotto', 'proprietario', 'anno', 'mese', 'giorno', 'ora', 'min', 'sec', 'stato']

prod_shelves_csv = './data/products_shelves.csv'
columns_prod_shelves = ['user', 'prodotto', 'prezzo', 'prezzoscontato', 'soglia', 'coordinate']

full_filename = './static/s.jpg'
full_filename2 = './static/img.jpg'

df = pd.read_csv(data_csv, sep=';')
prodotti = df["prodotto"].unique()

""" Istanzio checker: classe che serve per fare i controlli nelle operazioni login etc. """
checker = Checker()

appname = "Smart Shelf"
app = Flask(__name__,template_folder='templates')

def read_dataset_users():
    try:
        dataset = pd.read_csv(users_csv, sep=';')
    except:
        dataset = pd.DataFrame(columns=columns_users)
    return dataset

@app.errorhandler(404)
def page_not_found(error):
    return 'Errore', 404


# Pagina che visualizza login/reg page se non eseguito il login
# altrimenti visualizza la pagina home
@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return render_template('home.html')

# Gestione del login, al termine chiamo la funzione index()
@app.route('/', methods=['POST'])
def login():
    """ Carico il dataset utenti e quello contenente le info dei prodotti sugli scaffali"""
    users = read_dataset_users()
    #df = pd.read_csv(data_csv, sep=';')
    prod_shelves = pd.read_csv(prod_shelves_csv, sep=';')
    if Checker.check_login(Checker,request.form['username'], request.form['password'], users):
        session['logged_in'] = True
        username = request.form['username']

        if df.empty:
            last_element="Nessuno elemento"
        else:
            last_element = df[df['proprietario'] == username].iloc[-1]
            print(last_element)

        price_value = Checker.check_status(Checker,prod_shelves, last_element)

        if price_value == -1:
            price = 'FINISHED'
        else:
            price = str(price_value) + ' € '
        dict = {'id_shelf': last_element['id_shelf'], 'product': last_element['prodotto'],
                'last_update': str(last_element['giorno']) + '/' + str(last_element['mese']) + '/' + str(last_element['anno']),
                'orario_last_update':str(last_element['ora']) + ':' + str(last_element['min']),
                'state': last_element['stato'],
                'price': price}
        return render_template('home.html', username=username, id_shelf=dict['id_shelf'], update=dict['last_update'], orario=dict['orario_last_update'],
                               state=dict['state'], price=dict['price'])
    else:
        flash('wrong password!')
        return index()

@app.route('/registration')
def registration_():
    return render_template('registration.html')

#
@app.route('/registration_function', methods=['POST'])
def registration():
    users = read_dataset_users()
    if request.form['password'] == request.form['repeat-password']:
        if request.form['username'] and request.form['email']:
            if Checker.check_unique_users(Checker,request.form['username'], users):
                print(users)
                tup = [request.form['email'], request.form['username'], request.form['password']]
                print(tup)
                users.loc[len(users)] = tup
                print(users)
                users.to_csv(users_csv, sep=';', index=False)
                session['logged_in'] = True
            else:
                flash('Username is already used')
        else:
            flash('Please insert username and email')
        return index()
    else:
        flash('Passwords must be the same!')
        session['logged_in'] = False
        return index()

@app.route("/<username>")
def home(username):
    print(username)
    users = read_dataset_users()
    # df = pd.read_csv(data_csv, sep=';')
    prod_shelves = pd.read_csv(prod_shelves_csv, sep=';')
    if df.empty:
        last_element = "Nessuno elemento"
    else:
        last_element = df[df['proprietario'] == username].iloc[-1]
        print(last_element)

    price_value = Checker.check_status(Checker, prod_shelves, last_element)

    if price_value == -1:
        price = 'FINISHED'
    else:
        price = str(price_value) + ' € '
    dict = {'id_shelf': last_element['id_shelf'], 'product': last_element['prodotto'],
            'last_update': str(last_element['anno']) + '/' + str(last_element['mese']) + '/' + str(
                last_element['giorno']),
            'orario_last_update': str(last_element['ora']) + '/' + str(last_element['min']),
            'state': last_element['stato'],
            'price': price}
    return render_template('home.html',username=username,id_shelf=dict['id_shelf'], update=dict['last_update'], orario=dict['orario_last_update'],
                               state=dict['state'], price=dict['price'])


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

# Pagina delle statistiche in cui richiama Prophet
@app.route('/analysis/<id_shelf>', methods=["GET"])
def analysis(id_shelf):
    print("Siamo entrati nelle analisi")
    products_shelves = pd.read_csv(prod_shelves_csv, sep=';')
    #username = products_shelves[products_shelves['id_shelf'] == id_shelf]['user'][0]
    username = products_shelves[products_shelves['id_shelf'] == id_shelf]['user'].values[0]
    print(username)
    ##############
    previsioni()
    full_filename_statistiche = f"../static/{id_shelf}.png"
    full_filename_statistiche2 = f"../static/Monthly_peak{id_shelf}.png"
    print(full_filename_statistiche)
    print(full_filename_statistiche2)
    # QUESTE ULTIME RIGHE SONO HARD.CODED PURTROPPO NON SO COME INVIARE DINAMICAMENTE
    # PIU' IMMAGINI AL TEMPLATE SENZA SAPERE A PRIORI QUANTE CE NE SONO (nel nostro caso solo 2 prodotti)
    full_filename_statistiche3 = f"../static/Vendite_prodotto_tot{prodotti[0]}.png"
    full_filename_statistiche4 = f"../static/Vendite_prodotto_tot{prodotti[1]}.png"
    return render_template('analysis.html',username=username,id_shelf=id_shelf,
                           statistiche=full_filename_statistiche,
                           statistiche2=full_filename_statistiche2,
                           statistiche3=full_filename_statistiche3,
                           statistiche4=full_filename_statistiche4)

# Pagina per la gestione degli scaffali
@app.route('/gestione_scaffali/<id_shelf>', methods=["GET"])
def gestione_scaffali(id_shelf):
    products_shelves = pd.read_csv(prod_shelves_csv,sep=';')
    #username = products_shelves[products_shelves['id_shelf']==id_shelf]['user'][0]
    username = products_shelves[products_shelves['id_shelf'] == id_shelf]['user'].values[0]
    print(username)
    elemento_affine_id, elemento_affine_prodotto, prodotto = affinità(id_shelf)

    return render_template('gestione_scaffali.html', id=id_shelf,
                           prodotto= prodotto,
                           elemento_affine_id=elemento_affine_id,
                           elemento_affine_prodotto=elemento_affine_prodotto,
                           username=username,id_shelf=id_shelf)



@app.route('/successo', methods=["POST"])
def successo():
    print("successo")

    # Leggo dalla home cosa mi inserisce l'utente
    Id_scaffale = request.form['ID_scaffale']
    User = request.form['Utente']
    Product = request.form['Product']
    Price = request.form['Price']
    Prezzo_scontato = request.form['Discounted_price']
    Soglia = request.form['Trashold']
    Posizione = request.form['Posizione']

    scrivi_dataset(Id_scaffale, User, Product, Price, Prezzo_scontato, Soglia, Posizione)
    # Andiamo a scrivere il dataset degli scaffali
    scrivi_dataset_shelf(Id_scaffale, Product, User)

    products_shelves = pd.read_csv(prod_shelves_csv, sep=';')
    # username = products_shelves[products_shelves['id_shelf']==id_shelf]['user'][0]
    username = products_shelves[products_shelves['id_shelf'] == Id_scaffale]['user'].values[0]
    print(username)
    print("Questo è il prezzo scontato", Prezzo_scontato)
    if df.empty:
        last_element = "Nessuno elemento"
    else:
        last_element = df[df['proprietario'] == username].iloc[-1]
        print(last_element)

    price_value = Checker.check_status(Checker, products_shelves, last_element)

    if price_value == -1:
        price = 'FINISHED'
    else:
        price = str(price_value) + ' € '
    dict = {'id_shelf': last_element['id_shelf'], 'product': last_element['prodotto'],
            'last_update': str(last_element['anno']) + '/' + str(last_element['mese']) + '/' + str(
                last_element['giorno']),
            'orario_last_update': str(last_element['ora']) + '/' + str(last_element['min']),
            'state': last_element['stato'],
            'price': price}
    return render_template('home.html',username=username,id_shelf=dict['id_shelf'], update=dict['last_update'], orario=dict['orario_last_update'],
                               state=dict['state'], price=dict['price'])

# Pagina dei contatti
@app.route("/contatti")
def contatti():
    return render_template("contatti.html")

# Pagina dei rifornimenti
@app.route("/rifornisci", methods=["POST"])
def rifornisci():
    full_filename5 = './static/rif.jpg'
    return render_template("rifornimenti.html", rif=full_filename5)

def scrivi_dataset(Id_scaffale, User, Product, Price, Prezzo_scontato, Soglia, Posizione):
    # columns=['id_shelf','user','prodotto','prezzo','prezzoscontato','soglia','coordinate']
    # dataset = pd.DataFrame(columns=columns)
    print("Sono entarto nella funzione scrivi_dataset")
    prod_shelves = pd.read_csv(prod_shelves_csv, sep=';')
    if Id_scaffale in prod_shelves['id_shelf'].unique():
        # Se era già presente e sto solo aggiornando droppo e aggiungo
        prod_shelves.drop(prod_shelves[prod_shelves["id_shelf"] == Id_scaffale].index, inplace=True)
        prod_shelves = prod_shelves.append({'id_shelf': Id_scaffale, 'user': User, 'prodotto': Product,
                                            'prezzo': Price, 'prezzoscontato': Prezzo_scontato, 'soglia': Soglia,
                                            'coordinate': Posizione}, ignore_index=True)

        # print("Questa è l'ultima riga aggiunta droppando: ",prod_shelves.iloc[-1])
        prod_shelves.to_csv(prod_shelves_csv, sep=';', index=False)
        print(prod_shelves)
    else:
        # Altrimenti non elimino nulla
        prod_shelves = prod_shelves.append({'id_shelf': Id_scaffale, 'user': User, 'prodotto': Product, 'prezzo': Price,
                                            'prezzoscontato': Prezzo_scontato, 'soglia': Soglia,
                                            'coordinate': Posizione}, ignore_index=True)
        # print("Questa è l'ultima riga aggiunta senza droppare: ", prod_shelves.iloc[-1])
        prod_shelves.to_csv(prod_shelves_csv, sep=';', index=False)
        print(prod_shelves)


def scrivi_dataset_shelf(Id_scaffale, Product, User):
    print("Sono entrato nella funzione scrivi_dataset_shelf")
    shelf = pd.read_csv(shelves_csv, sep=";")
    print(shelf["id_shelf"])
    valori = shelf['id_shelf'].unique()
    print("Questi sono i valori:", valori)

    if Id_scaffale in valori:
        print("Non c'è bisogno di aggiungerlo")
    else:
        shelf = shelf.append({'id_shelf': Id_scaffale, 'prodotto': Product, 'proprietario': User}, ignore_index=True)
        shelf.to_csv(shelves_csv, sep=';', index=False)
        return print("Ho scritto il dataset degli scaffali")


# FUNZIONE RICHIAMATA QUANDO CLICCHIAMO SU STATISTICHE
def previsioni():
    print("Siamo entrati nelle previsioni")
    #columns1 = ["id_shelf", "prodotto", "proprietario", "anno", "mese", "giorno", "ora", "min", "sec", "stato"]
    columns = ['id_shelf', 'proprietario', 'data', 'ds', 'y']

    df = pd.read_csv("data/data.csv", sep=';')

    #CONTROLLO PRESENZA DEI DATI NEL DATASET
    if df.size == 0:
        print("NON CI SONO DATI")
        path_immagine='./static/dati.jpg'
        return render_template('non_ci_sono_dati.html', dati=path_immagine)

    data = pd.DataFrame(columns=colums_dataset, data=df)

    # creo il dataset per prophet
    data_prophet = pd.DataFrame(columns=columns)

    # Itero e stampo per ogni TIPOLOGIA di scaffale
    id_shelves = data['id_shelf'].unique()
    vendite = []
    i = 0


    for id_shelf in id_shelves:

        n_rifornimenti = data[(data["stato"] == 3) & (data["id_shelf"] == id_shelf)]
        vendite.append(len(n_rifornimenti))
        print("Questo è il numero di volte in cui si svuota lo scaffale:", id_shelf + " : " + str(vendite[i]))
        i = i + 1



    # GRAFICI VENDITE
    # Grafichiamo l'andamento dei rifornimenti (e quindi delle vendite) in un mese per B01

    for id_shelf in id_shelves:

        dati = data[(data["id_shelf"] == id_shelf) & (data["stato"] == 3)]
        fig, ax = plt.subplots(figsize=(15, 7))
        dati.groupby(['giorno']).count()['stato'].plot(ax=ax)
        fig.savefig(f"static/Monthly_peak{id_shelf}.png", transparent=False, bbox_inches='tight')

    # AGGIUNGO LA PARTE IN CUI PER OGNI PRODOTTO VA A GRAFICARNE LE VENDITE IN GRAFICI SEPARATI

    prodotti = data["prodotto"].unique()
    for prodotto in prodotti:
        dati1 = data[(data["stato"]) != 3]
        dati2 = dati1[(dati1["prodotto"] == prodotto)]
        fig, ax = plt.subplots(figsize=(15, 7))
        dati2.groupby(['giorno']).count()['stato'].plot(ax=ax)
        fig.savefig(f"static/Vendite_prodotto_tot{prodotto}.png", transparent=False, bbox_inches='tight')

    # Grafichiamo l'andamento generale delle vendite insieme
    # data2=data[data["stato"]==0]
    # fig, ax = plt.subplots(figsize=(16,7))
    # data2.groupby(['giorno','prodotto']).count()['stato'].unstack().plot(ax=ax)
    # fig.savefig(f"Images/Daily_pick_overlap.png", transparent=True, bbox_inches='tight')

    # data_prophet = data[data["id_shelf"]=="B01"]
    data_tmp = data.drop("prodotto", axis=1)
    data_tmp = data_tmp.drop("proprietario", axis=1)
    data_tmp = data_tmp.drop("ora", axis=1)
    data_tmp = data_tmp.drop("min", axis=1)
    data_tmp = data_tmp.drop("sec", axis=1)
    # elimino i dati in cui lo scaffale è pieno, le venite saranno 0,1,2
    data_tmp.drop(data_tmp[data_tmp["stato"] == 3].index, inplace=True)
    # data_tmp.iloc[:, -2:].groupby(data_tmp.columns[-2]).count().iloc[0, 0]
    # data_tmp[data_tmp["id_shelf"]=='H02']

    data_tmp2 = pd.DataFrame(columns=["id_shelf", "ds", "y"])
    data_tmp2["id_shelf"] = data_tmp["id_shelf"]
    data_tmp["anno"] = data_tmp["anno"].apply(lambda x: str(x))
    data_tmp["mese"] = data_tmp["mese"].apply(lambda x: str(x))
    data_tmp["giorno"] = data_tmp["giorno"].apply(lambda x: str(x))
    data_tmp2["ds"] = pd.DatetimeIndex(data_tmp["anno"] + '-' + data_tmp["mese"] + '-' + data_tmp["giorno"])

    data_tmp2 = data_tmp2.drop_duplicates(subset=["ds"])
    l = len(data_tmp2)
    for i in range(0, l):
        data_tmp2.iloc[i, -1] = data_tmp.iloc[:, -2:].groupby(data_tmp.columns[-2]).count().iloc[i, 0]
    data_prophet = data_tmp2
    data_prophet.to_csv("./data/prophet_csv", sep=";", index=False)

    # Itero e stampo per ogni TIPOLOGIA di scaffale
    id_shelves = data_prophet['id_shelf'].unique()

    for id_shelf in id_shelves:
        # Per ogni scaffale devo differenziare il dataset
        # Altrimenti fa una previsione senza distinguerli

        data_tmp = data_prophet[data_prophet["id_shelf"] == id_shelf]
        m = Prophet(daily_seasonality=True)
        m.fit(data_tmp)
        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)
        fig1 = m.plot(forecast)

        #m.plot_components(forecast)
        plt.savefig(f"static/{id_shelf}.png")


def affinità(id_shelf):
    df = pd.read_csv(data_csv, sep=';')
    ID = id_shelf
    shelf = pd.read_csv(shelves_csv, sep=';')
    ids_list = shelf['id_shelf'].unique()
    global last_element_id, last_element_affine_id
    for e in ids_list:
        if e == ID:
            last_element_id = e
        else:
            last_element_affine_id = e

    # prendo l'ultima riga dal dataset per ogni elemento
    last_element_obj = df[df['id_shelf'] == last_element_id].iloc[-1]
    last_element_affine_obj = df[df['id_shelf'] == last_element_affine_id].iloc[-1]
    prodotto=last_element_obj["prodotto"]
    prodotto_affine= last_element_affine_obj["prodotto"]
    return last_element_affine_id, prodotto_affine,prodotto


""" METODI UTILIZZATI DAL BRIDGE PER SCRIVERE O LEGGERE"""

@app.route('/shelf_status', methods=['POST'])
def shelf_status():
    req = request.get_data().decode("utf-8")
    print('Request shelf_status:')
    print(req)
    status = int(req[20])
    timestamp = datetime.datetime.now()
    #id_dello_scaffale = req[0] + req[1] + req[2]
    id_dello_scaffale = req[9:12]
    try:
        dataset = pd.read_csv(data_csv, sep=';')
        shelf = pd.read_csv(shelves_csv, sep=';')
    except:
        dataset = pd.DataFrame(columns=colums_dataset)
        # QUA LO DEVE LEGGERE DALLA REGISTRAZIONE, NEL FORM DELLA REGISTRAZIONE BISONGEREBBE AGGIUNGERE IL PRODOTTO
        # COSI SI POSSONO AGGIUNGERE UTENTI
        # shelf = pd.DataFrame([['B01','pasta','fillo'],['H02','sughi','gabri']],columns=columns_shelves)
        shelf = pd.DataFrame(columns=columns_shelves)
        shelf.to_csv(shelves_csv, sep=';', index=False)

    ids = shelf["id_shelf"].unique()
    print("AL MOMENTO QUESTI SONO GLI ID", ids)

    if id_dello_scaffale in ids:
        print('Dataset PRIMA:')
        print(dataset)
        timestamp.time()
        # colums_dataset = ['id_shelf','prodotto','proprietario','anno','mese','giorno','ora','min','sec','stato']
        tupla = [id_dello_scaffale, '', 'default', timestamp.year, timestamp.month, timestamp.day, timestamp.hour,
                 timestamp.minute, timestamp.second, status]
        # il livello è sottratto di 1 solo per chiarezza di lettura ed avere unqa corrispondeza tra primo livello=1, secondo livello=2, terzo livello=3

        # Lunghezza del file csv
        # print('lunghezza' + str(len(shelf)))
        for i in range(len(shelf)):
            if shelf['id_shelf'].iloc[i] == tupla[0]:
                # AGGIORNAMENTO DELLA TUPLA CON DATI CONTENUTI AL'INTERNO DI SHELVES_CSV
                tupla[1] = shelf['prodotto'].iloc[i]
                tupla[2] = shelf['user'].iloc[i]
        print("tupla:")
        print(tupla)
        # inserisco nell'ultima riga quello ricevuto dal bridge e lo scrivo sul file csv
        dataset.loc[len(dataset)] = tupla
        dataset.to_csv(data_csv, sep=';', index=False)
        # Le righe di codice successive mi servono solamente come controllo
        print(dataset)
        if status == 0:
            print("Numero oggetti: 0")
        if status == 1:
            print("Numero oggetti: 1")
        elif status == 2:
            print("Numero oggetti: 2")
        elif status == 3:
            print("Numero oggetti: 3")

        return 'OK'
    else:
        print("Questo è l'ID ricevuto ma lo scaffale non è ONLINE:", id)

# metodo utilizzato dal bridge per ottenere informazioni sullo scaffale
@app.route('/check_shelf', methods=["GET"])
def check_shelf():
    # va riletto ogni volta perchè df è una variabile globale
    df = pd.read_csv(data_csv, sep=';')
    ID = request.args.get('id')
    print ("Request check shelf: " + ID)
    # Per ogni id devo definire l'elemento affine e l'elemento che mi serve
    shelf = pd.read_csv(shelves_csv, sep=';')
    ids_list = shelf['id_shelf'].unique()
    print("Ecco la lista",ids_list)

    global last_element_id, last_element_affine_id
    for e in ids_list:
        if e == ID:
            last_element_id = e
        else:
            last_element_affine_id = e

    # prendo l'ultima riga dal dataset per ogni elemento
    last_element_obj = df[df['id_shelf'] == last_element_id].iloc[-1]
    last_element_affine_obj = df[df['id_shelf'] == last_element_affine_id].iloc[-1]
    print("elemento:")
    print(last_element_obj)
    print("elemento affine:")
    print(last_element_affine_obj)
    # Conto il numero di oggetti
    numero_oggetti = (last_element_obj["stato"])
    numero_oggetti_affini = (last_element_affine_obj["stato"])
    print("Numero oggetti: ", numero_oggetti)
    print("Numero oggetti affini: ", numero_oggetti_affini)

    # Ricavo le 2 soglie che mi servono dal dataset in cui ho la soglia
    dataset = pd.read_csv(prod_shelves_csv, sep=";")
    data_row_obj = dataset[dataset["id_shelf"] == last_element_id].iloc[-1]
    print("data_row_obj")
    print(data_row_obj)
    data_row_obj_affine = dataset[dataset["id_shelf"] == last_element_affine_id].iloc[-1]
    print("data_row_affine_obj")
    print(data_row_obj_affine)
    soglia_obj = data_row_obj["soglia"]
    soglia_obj_affine = data_row_obj_affine["soglia"]

    # Ricavo il prezzo e il prezzo scontato del mio oggetto richiesto dal Bridge
    prezzo_obj = data_row_obj["prezzo"]
    prezzo_obj_scontato = data_row_obj["prezzoscontato"]

    # soglia_int=np.astype()
    # Qua teoricamente nell'if ci vuole un OR, nel senso che:
    # io devo settare il prezzo in promozione in due casi :
    # 1)Se il prodotto stesso è sotto soglia
    # 2)Se il prodotto affiliato è sotto soglia
    # Quindi devo aggiungere il controllo che il prodotto affiliato sia sotto soglia
    # PER DARE IMPORTANZA ALLA COMUNICAZIONE TRA DISPOSITIVI

    # Costruisco il pacchetto
    print("prezzo: " + str(prezzo_obj))
    print("prezzo scontato: " + str(prezzo_obj_scontato))

    if numero_oggetti <= soglia_obj or numero_oggetti_affini < soglia_obj_affine:
        #jsondata = json.dumps(id=ID, prezzo=prezzo_obj_scontato)
        return jsonify(id=ID, prezzo=str(prezzo_obj_scontato))
    else:
        #jsondata = json.dumps(id=ID, prezzo=prezzo_obj)
        return jsonify(id=ID, prezzo=str(prezzo_obj))

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')


@app.route('/suggerimenti/<id_shelf>')
def suggerimenti(id_shelf):
    products_shelves = pd.read_csv(prod_shelves_csv, sep=';')
    username = products_shelves[products_shelves['id_shelf'] == id_shelf]['user'].values[0]
    print(username)
    return render_template('suggerimenti.html',id_shelf=id_shelf,username=username)


class FlaskThread(Thread):
	def __init__(self, nome):
        	Thread.__init__(self)
        	self.nome = nome
	def run(self):

		myconfig = Config()
		app.config.from_object(myconfig)
		app.run(host='0.0.0.0', port=80)
