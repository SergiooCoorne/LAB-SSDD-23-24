#Cliente que me he creado para poder verificar el funcionamiento de los metodos

import logging
from typing import List

import Ice
import IceStorm

import IceDrive

from .blob import BlobService 
from .blob import DataTransfer

class ClientAppPruebas(Ice.Application):
    """Client application."""
    def run(self, args: List[str]) -> int:
        """Code to be run by the application."""
        if len(args) != 3:
            print("Error: El numero de proxys proporcionados no es correcto")
            return 1
        
        #Obtencion de un objeto proxy de BlobService
        proxy = self.communicator().stringToProxy(args[1])
        blob_prx = IceDrive.BlobServicePrx.checkedCast(proxy)

        if not blob_prx:
            print("Error: Proxy Blob invalido")
            return 1
        
        #Obtencion de un objeto proxy de DataTransfer
        prx = self.communicator().stringToProxy(args[2])
        dt_prx = IceDrive.DataTransferPrx.checkedCast(prx)

        if not dt_prx:
            print("Error: Proxy DataTransfer invalido")
            return 1
        
        # -----Pruebas de las funciones-----
        #blob_id = "90cc11e4868e4c93e8da07d9bcbbe90bb39a1eed1558440ac60749a08bf0e2ee"
        #print("-----------Subida de un archivo al servidor-----------")
        #blob_id = self.pruebaUpload(blob_prx, dt_prx)
        #print("-----------Cerrando archivo despues de la subida-----------")
        #dt_prx.close()
        #print("Bajada de un archivo del servidor\n-----------")
        #self.pruebaDonwload(blob_prx, blob_id)
        #print("Incrementando numero de links\n-----------")
        #blob_prx.link(blob_id)
        #print("Decrementando numero de links\n-----------")
        #blob_prx.unlink(blob_id)


    def pruebaDonwload(self, blob_prx, blob_id):
        data_transfer_prx = blob_prx.download(blob_id)

        if not data_transfer_prx:
            print("\nError al obtener el proxy de DataTransfer\n")
            return 1
        else: 
            print("Proxy obtenido correctamente\n")

        print("Datos del archivo asociado al objeto DataTransfer:\n")
        #print(data_transfer_prx.read(10))
        datos = data_transfer_prx.read(100)
        datos_decode = datos.decode("utf-8")
        print(datos_decode + "\n")

    def pruebaUpload(self, blob_prx, dt_prx):
        blob_id = blob_prx.upload(dt_prx)

        if blob_id != None:
            print("Archivo subido correctamente\n")
        return blob_id
