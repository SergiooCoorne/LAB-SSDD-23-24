"""Handlers for CLI programs."""

import sys

from .appPruebas import BlobAppPruebas, ClientAppPruebas
from .app import BlobApp

def client() -> int:

    app = ClientAppPruebas()
    return app.main(sys.argv)


def server() -> int:

    app = BlobAppPruebas()
    return app.main(sys.argv)
