"""Authentication service application."""

import logging
from typing import List

import Ice

import IceDrive

from .blob import BlobService 

#Clase con la que ejecutamos el servicio Blob
class BlobApp(Ice.Application):
    def run(self, args: List[str]) -> int:
        adapter = self.communicator().createObjectAdapter("BlobAdapter")
        adapter.activate()

        path_archivos = "/home/sergio/Escritorio/VSCodeLinux/LAB-SSDD-23-24/icedrive_blob/archivos.txt"

        servant = BlobService(path_archivos)
        servant_proxy = adapter.addWithUUID(servant)

        logging.info("Proxy sirviente BlobService: %s", servant_proxy)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0