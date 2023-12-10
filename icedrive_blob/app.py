"""Authentication service application."""

import logging
from typing import List

import Ice

import IceDrive

from .blob import BlobService 

#Clase con la que ejecutamos el servicio Blob
class BlobApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""

    def run(self, args: List[str]) -> int:
        adapter = self.communicator().createObjectAdapter("BlobAdapter")
        adapter.activate()

        #Ruta donde queremos que se guarden nuestros ficheros
        path_directory = "/home/sergio/Escritorio/ficheros_blob_service"

        servant = BlobService(path_directory)
        servant_proxy = adapter.addWithUUID(servant)

        logging.info("Proxy sirviente BlobService: %s", servant_proxy)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0