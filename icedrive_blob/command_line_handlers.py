"""Handlers for CLI programs."""

import sys

from .app import BlobApp, BlobAppPruebas, ClientAppPruebas


def client() -> int:

    app = ClientAppPruebas()
    return app.main(sys.argv)


def server() -> int:

    app = BlobAppPruebas()
    return app.main(sys.argv)
