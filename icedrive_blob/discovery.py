"""Servant implementations for service discovery."""

import Ice

import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""
    def __init__(self, publisher_discovery: IceDrive.DiscoveryPrx):
        self.publisher_dicovery = publisher_discovery

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        self.publisher_dicovery.announceAuthenticationAsync(prx)

    def announceDirectoryServicey(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        self.publisher_dicovery.announceDirectoryServiceyAsync(prx)

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        self.publisher_dicovery.announceBlobServiceAsync(prx)
        print("---Anunciando proxy BlobService---")