"""Servant implementation for the delayed response mechanism."""

import Ice

import IceDrive



class BlobQueryResponse(IceDrive.BlobQueryResponse):
    """Query response receiver."""
    def __init__(self, future: Ice.Future) -> None:
        self.future = future

    def downloadBlob(self, blob: IceDrive.DataTransferPrx, current: Ice.Current = None) -> None:
        """Receive a `DataTransfer` when other service instance knows the `blob_id`."""
        self.future.set_result(blob) #Establecemos el proxy del DataTranfer en el objeto future

    def blobExists(self, current: Ice.Current = None) -> None:
        """Indicate that `blob_id` was recognised by other service instance."""
        
    def blobLinked(self, current: Ice.Current = None) -> None:
        """Indicate that `blob_id` was recognised by other service instance and was linked."""
        print("Blob_id reconocido y enlazado\n")

    def blobUnlinked(self, current: Ice.Current = None) -> None:
        """Indicate that `blob_id` was recognised by other service instance and was unlinked."""
        print("Blob_id reconocido y desenlazado\n")

class BlobQuery(IceDrive.BlobQuery):
    """Query receiver."""
    def __init__(self, blob_service) -> None:
        """" Receive a BlobServicePrx. This proxy will be used to download, link, or unlink the file"""
        self.blob_service = blob_service

    def downloadBlob(self, blob_id: str, response: IceDrive.BlobQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query for downloading an archive based on `blob_id`."""
        try:
            data_transfer_prx = self.blob_service.donwload(blob_id)
            response.downloadBlob(data_transfer_prx)
        except IceDrive.UnknownBlob:
            print("Blob_id no encontrado\n")

    def blobIdExists(self, blob_id: str, reponse: IceDrive.BlobQueryResponsePrx, current: Ice.Current = None) -> None:
        "Receive a query to check if `blob_id` archive exists."

    def linkBlob(self, blob_id: str, response: IceDrive.BlobQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query to create a link for `blob_id` archive if it exists."""
        try:
            self.blob_service.link(blob_id)
            response.blobLinked()
        except IceDrive.UnknownBlob:
            print("Blob_id no encontrado\n")


    def unlinkBlob(self, blob_id: str, response: IceDrive.BlobQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query to destroy a link for `blob_id` archive if it exists."""
        try:
            self.blob_service.unlink(blob_id)
            response.blobUnlinked()
        except IceDrive.UnknownBlob:
            print("Blod_id no encontrado\n")