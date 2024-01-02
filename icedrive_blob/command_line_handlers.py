"""Handlers for CLI programs."""

import sys

from .appPruebas import BlobAppPruebas, ClientAppPruebas
from .app import BlobApp
from .app import BlobService

path_directory = "/home/sergio/Escritorio/ficheros_blob_service"

def client() -> int:

    app = ClientAppPruebas()
    return app.main(sys.argv)


def server() -> int:

    app = BlobAppPruebas(BlobService(path_directory))
    return app.main(sys.argv)
