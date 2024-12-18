"""Servant implementations for service discovery."""

import Ice

import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""
    def __init__(self):
        self.proxysAutentication = set()
        self.proxysDirectory = set()
        self.proxysBlob = set()

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        if(prx not in self.proxysAutentication):
            print("Anuncio Authentication recibido. Proxy: " + str(prx) + "\n")
            self.proxysAutentication.add(prx)

    def announceDirectoryService(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        if(prx not in self.proxysDirectory):
            print("Anuncio Directory recibido. Proxy: " + str(prx) + "\n")
            self.proxysDirectory.add(prx)

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        if(prx not in self.proxysBlob):
            print("Anuncio Blob recibido. Proxy: " + str(prx) + "\n")
            self.proxysBlob.add(prx)

    def randomAuthentication(self, current: Ice.Current = None) -> IceDrive.AuthenticationPrx:
        """Return a random Authentication service proxy."""
        return next(iter(self.proxysAutentication), None)
    