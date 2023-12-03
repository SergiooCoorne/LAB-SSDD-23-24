"""Authentication service application."""

import logging
import sys
from typing import List

import Ice

import IceDrive

from .blob import BlobService 
from .blob import DataTransfer


class BlobApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the BlobApp class."""
        adapter = self.communicator().createObjectAdapter("BlobAdapter")
        adapter.activate()

        path_archivos = "/home/sergio/Escritorio/VSCodeLinux/LAB-SSDD-23-24/icedrive_blob/archivos.txt"

        servant = BlobService(path_archivos)
        servant_proxy = adapter.addWithUUID(servant)

        logging.info("Proxy: %s", servant_proxy)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


class ClientApp(Ice.Application):
    """Client application."""
    def run(self, args: List[str]) -> int:
        """Code to be run by the application."""
        if len(args) != 2:
            print("Error: a proxy, and only one proxy, should be passed")
            return 1
        
        proxy = self.communicator().stringToProxy(args[1])
        blob_prx = IceDrive.BlobServicePrx.checkedCast(proxy)

        if not blob_prx:
            print("Error: invalid proxy")
            return 1
        
        #print("\nConexion con el proxy '" + proxy.ice_toString() + "' establecida correctamente")

        pruebaDonwload(blob_prx)


def pruebaDonwload(blob_prx):
    data_transfer_prx = blob_prx.download("e633f4fc79badea1dc5db970cf397c8248bac47cc3acf9915ba60b5d76b0e88f")
    if not data_transfer_prx:
        print("\nError al obtener el proxy de DataTransfer\n")
        return 1
    else: 
         print("\nProxy obtenido correctamente\n")

    print("Datos del archivo asociado al objeto DataTransfer: ")
    print(data_transfer_prx.read(10))
        
def pruebaUpload(blob_prx, current: Ice.Current = None):
    #Creamos el objeto DataTransfer con el archivo que queremos subir
    archivo = "/home/sergio/Escritorio/VSCodeLinux/LAB-SSDD-23-24/icedrive_blob/prueba2.txt"
    data_transfer = DataTransfer(archivo)
    #Sacamos el proxy del objeto DataTransfer
    prx = current.adapter.addWithUUID(data_transfer)
    prx_data_transfer = IceDrive.DataTransferPrx.uncheckedCast(prx)
    blob_prx.upload(prx_data_transfer)