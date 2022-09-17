class Checker:
    def __init__(self):
        pass


    def check_unique_users(self,username, users):
        # se l'username è presente dentro tutti gli utenti
        # print(users['username'].unique())
        # print(username)
        if username in users['username'].unique():
            return False
        return True


    def check_login(self, username, password, users):
        # Seleziono la riga del dataset contenente l'username
        user_serie = users[users['username'] == username]
        # controllo la presenza o meno dell'username controllando la lunghezza della serie
        if len(user_serie) == 1:
            print('Username presente')
            if (user_serie['password'].item()) == password:
                print('Credenziali corrette')
                return True
        return False


    # controllo lo stato e setto il prezzo
    def check_status(self, prod_shelves, last_element):
        product = prod_shelves[prod_shelves['prodotto'] == last_element['prodotto']]
        soglia = product['soglia'].iloc[0]
        # se siamo sotto la soglia scelta dall'utente allora andiamo a settare il nuovo prezzo
        if last_element['stato'] == 0:
            return -1
        elif last_element['stato'] <= soglia:
            return prod_shelves[prod_shelves['prodotto'] == last_element['prodotto']]['prezzoscontato'].iloc[0]

        return prod_shelves[prod_shelves['prodotto'] == last_element['prodotto']]['prezzo'].iloc[0]
