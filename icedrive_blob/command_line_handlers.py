"""Handlers for CLI programs."""

import sys

from .app import BlobApp
from .appE1 import BlobAppPruebas
from .clientE1 import ClientAppPruebas

def client() -> int:

    app = ClientAppPruebas()
    return app.main(sys.argv)


def server() -> int:

    app = BlobApp()
    return app.main(sys.argv)
