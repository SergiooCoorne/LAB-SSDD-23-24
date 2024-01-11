"""Servant implementations for service discovery."""

import Ice

import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""
    def __init__(self, servant):
        self.servant = servant
        self.proxysAutentication = []
        self.proxysDiscovery = []
        self.proxysBlobService = []
        
    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        print(str("\n" + str(prx)))

    def announceDirectoryServicey(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        print("\n" + str(prx))

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        self.proxysBlobService.append(prx)
        print("Anuncio recibido. Proxy: " + str(prx) + "\n")