import pytest

from blob import BlobService
from blob import DataTransfer 

def create_blob():
    blob = BlobService("archivosTest.txt")
    assert blob != None

def create_data_trasnfer():
    data_transfer = DataTransfer("archivo.txt")
    assert data_transfer != None
