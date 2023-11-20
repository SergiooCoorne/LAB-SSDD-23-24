"""Module for servants implementations."""

import Ice

import IceDrive

import time

class User(IceDrive.User):
    """Implementation of an IceDrive.User interface."""

    def __init__(self, username: str, password: str):
        """Create a new User object."""

        #Le ponemos el atributo timeAlive para saber cuando se ha creado
        creation_time = time.time()
        self.username = username
        self.password = password
        print("Vida del objeto " + self.username + " :" + self.creation_time + " segundos\n")
        
    def getUsername(self, current: Ice.Current = None) -> str:
        """Return the username for the User object."""

        return User.username #Devuelve el nombre de usuario

    def isAlive(self, current: Ice.Current = None) -> bool:
        """Check if the authentication is still valid or not."""

        if User.creation_time - time.time() > 120: #Si se ha creado hace mas de 2 minutos
            return False
        else: #Si se ha creado hace menos de 2 minutos
            return True

    def refresh(self, current: Ice.Current = None) -> None:
        """Renew the authentication for 1 more period of time."""

        User.creation_time = time.time() #Volvemos a poner el tiempo a 0

class BlobService(IceDrive.BlobService):
    """Implementation of an IceDrive.BlobService interface."""

    def link(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id file as linked in some directory."""

    def unlink(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id as unlinked (removed) from some directory."""

    def upload(
        self, blob: IceDrive.DataTransferPrx, current: Ice.Current = None
    ) -> str:
        """Register a DataTransfer object to upload a file to the service."""

    def download(
        self, blob_id: str, current: Ice.Current = None
    ) -> IceDrive.DataTransferPrx:
        """Return a DataTransfer objet to enable the client to download the given blob_id."""
