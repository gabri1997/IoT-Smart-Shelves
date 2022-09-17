import serial
import serial.tools.list_ports
import requests
import time
from flask import request

# url per inserire i dati sul dataset
url = 'http://192.168.178.23/shelf_status'
#url="http://87.18.17.201/shelf_status"
# url per controllare lo stato degli scaffali ed aggiornare eventualmente il prezzo sul display
url2 = 'http://192.168.178.23/check_shelf'

class Bridge():

    def setupSerial(self):

        self.ser=None
        print("Available ports: ")
        ports=serial.tools.list_ports.comports()

        self.port_name=None
        for port in ports:
            print(port.device)
            print(port.description)

            if 'arduino' or 'dispositivo' or 'USB-SERIAL CH340' in port.description.lower():
                self.port_name=port.device
        print(f'Connecting to: {self.port_name}')

        try:
            if self.port_name is not None:
                self.ser=serial.Serial(self.port_name, 9600, timeout=0)
        except:
            self.ser = None

        self.inputBuffer=[]


    def setup(self):
        #Funzione da aggiornare ogni volta che si aggiunge un setup
        self.setupSerial()


    def useLevelData(self):
        print(f"\nId_Shelf: {self.inputBuffer[1]+self.inputBuffer[2]+self.inputBuffer[3]}")
        print(f"\nHo ricevuto i dati sul numero di oggetti {self.inputBuffer[4]}")
        #requests.post("http://iotproj.ddns.net/level", data=self.inputBuffer[1]+self.inputBuffer[2]+self.inputBuffer[3]+self.inputBuffer[4])

        """
        id_shelf=self.inputBuffer[1]+self.inputBuffer[2]+self.inputBuffer[3]
        status=self.inputBuffer[4]
        requests.post(url, data=id_shelf+status)
        """
        id_shelf = self.inputBuffer[1] + self.inputBuffer[2] + self.inputBuffer[3]
        data = {'id_shelf' : id_shelf,
                'status' : self.inputBuffer[4]}
        requests.post(url, data=data)
        #requests.post("http://87.18.17.201/shelf_status",data=id_shelf+status)
        #requests.post(url2, data=id_shelf)
        #data = request.get_json(url)
        #print("Questi sono i dati", data)
        # 1,2,3 è l'ID
        # 4 è lo stato
        return id_shelf


    def loop(self):
        state_packet=False
        start = time.time()
        ids_array=[]

        while(True):
            if self.ser is not None:

                if self.ser.in_waiting>0:
                    lastchar=self.ser.read(1).decode('utf-8')

                    if lastchar == 'S' and state_packet is False:
                        state_packet=True

                    if lastchar == 'P':
                        if state_packet is True:
                            id_shelf = self.useLevelData()
                            if id_shelf not in ids_array:
                                ids_array.append(id_shelf)
                            self.inputBuffer = []
                            state_packet =False
                    else:
                        #E' inutile salvarsi nel buffer il carattere terminatore
                        self.inputBuffer.append(lastchar)

            if (len(ids_array) != 0) and (time.time() - start) > 2:
                start = time.time()
                for id in ids_array:
                    r = requests.get(url2, params="id="+ str(id))
                    print(r.url)
                    # pacchetto creato sotto forma di json
                    json_pkg = r.json()
                    id_shelf = json_pkg['id']
                    prezzo = json_pkg['prezzo']
                    print("id_shelf: "+ str(id_shelf) + " prezzo " + str(int(prezzo)))
                    #scrivo sulla seriale
                    self.ser.write(str(prezzo).encode())
                    """
                    str_tx = self.ser.write(0xff)
                    print('Number of bytes' + str(str_tx))
                    str_tx = self.ser.write(int(prezzo))
                    print('Number of bytes' + str(str_tx))
                    str_tx = self.ser.write(0xfe)
                    print('Number of bytes' + str(str_tx))
                    """





if __name__ == '__main__':
    br=Bridge()
    br.setup()
    br.loop()