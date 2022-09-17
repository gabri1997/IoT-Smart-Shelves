import pandas as pd
from fbprophet import Prophet
import matplotlib.pyplot as plt
from flask import render_template

print("Siamo entrati nelle previsioni")
columns1 = ["id_shelf", "prodotto", "proprietario", "anno", "mese", "giorno", "ora", "min", "sec", "stato"]
columns = ['id_shelf', 'proprietario', 'data', 'ds', 'y']

df = pd.read_csv("./serverHTTP/data/data.csv", sep=';')
data = pd.DataFrame(columns=columns1, data=df)

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
    fig.savefig(f"./static/Monthly_peak{id_shelf}.png", transparent=False, bbox_inches='tight')

# AGGIUNGO LA PARTE IN CUI PER OGNI PRODOTTO VA A GRAFICARNE LE VENDITE IN GRAFICI SEPARATI

prodotti = data["prodotto"].unique()
for prodotto in prodotti:
    dati1 = data[(data["stato"]) != 3]
    dati2 = dati1[(dati1["prodotto"] == prodotto)]
    fig, ax = plt.subplots(figsize=(15, 7))
    dati2.groupby(['giorno']).count()['stato'].plot(ax=ax)
    fig.savefig(f"./static/Vendite_prodotto_tot{prodotto}.png", transparent=False, bbox_inches='tight')

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
data_prophet.to_csv("/serverHTTP/data/prophet_csv", sep=";", index=False)

# Itero e stampo per ogni TIPOLOGIA di scaffale
id_shelves = data_prophet['id_shelf'].unique()
'''

for id_shelf in id_shelves:
    # Per ogni scaffale devo differenziare il dataset
    # Altrimenti fa una previsione senza distinguerli

    data_tmp = data_prophet[data_prophet["id_shelf"] == id_shelf]
    m = Prophet(daily_seasonality=True)
    m.fit(data_tmp)
    future = m.make_future_dataframe(periods=30)
    forecast = m.predict(future)
    fig1 = m.plot(forecast)

    m.plot_components(forecast)
    plt.savefig(f"static/{id_shelf}.png")

'''
