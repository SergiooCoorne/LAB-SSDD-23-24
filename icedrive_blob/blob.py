"""Module for servants implementations."""

import Ice
import IceDrive
import hashlib
import os

class DataTransfer(IceDrive.DataTransfer):
    """Implementation of an IceDrive.DataTransfer interface."""

    def __init__(self, file_path: str, ) -> IceDrive.DataTransfer:
        """Initialize the DataTransfer object."""
        self.file_path = file_path

        with open(file_path, "rb") as f:
            self.file_content = f.read()
        
        self.sumSHA256 = hashlib.sha256(self.file_content).hexdigest()
        
        with open('blobs.txt', 'w') as f:
            f.write(self.sumSHA256)
            f.write('\n')

    def read(self, size: int, current: Ice.Current = None) -> bytes:
        """Returns a list of bytes from the opened file."""
        content_list = []

        with open(self.file_path, "rb") as f:
            chunck = f.read(size)
            if not chunck:
                return None
            content_list.append(chunck)
            return content_list

    def close(self, current: Ice.Current = None) -> None:
        """Close the currently opened file."""
        self = None

    @staticmethod
    def is_hash_present(file_path: str, target_hash: str) -> bool:
        """Check if a hash is already present in a file."""
        if not os.path.exists(file_path):
            return False

        with open(file_path, 'r') as f:
            return any(line.strip() == target_hash for line in f)

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
