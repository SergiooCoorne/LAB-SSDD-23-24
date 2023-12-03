"""Handlers for CLI programs."""

import sys

from .app import BlobApp, ClientApp


def client() -> int:

    app = ClientApp()
    return app.main(sys.argv)


def server() -> int:

    app = BlobApp()
    return app.main(sys.argv)
