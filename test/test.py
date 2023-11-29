from blobLocal import DataTransfer
from blobLocal import BlobService
import os
import pytest

@pytest.fixture
def setup():
    with open("archivo_test.txt", "w") as f:
        f.write("Hola")
    with open("blobs_test.txt", "w") as f:
        f.write("")

    datatransfer = DataTransfer("archivo_test.txt")
    blobservice = BlobService("blobs_test.txt")

    yield datatransfer, blobservice
    # Limpiamos el archivo después de los tests
    if os.path.exists("blobs_test.txt"):
        os.remove("blobs_test.txt")
        os.remove("archivo_test.txt")

def test1(setup):
    datatransfer, blobservice = setup
    assert datatransfer is not None

def test2(setup):
    datatransfer, blobservice = setup
    bytes = datatransfer.read(10)
    assert bytes is not None

def test3(setup):
    datatransfer, blobservice = setup

    hash = blobservice.upload(datatransfer)
    with open("blobs_test.txt", "r") as f:
        for line in f:
            if hash in line:
                assert True
                return
            
def test4(setup):
    datatransfer, blobservice = setup
    hash = blobservice.upload(datatransfer)

    interfaz = blobservice.download(hash)
    assert interfaz.file_path is "archivo_test.txt"

def test5(setup):
    datatransfer, blobservice = setup
    hash = blobservice.upload(datatransfer)

    blobservice.link(hash)
    with open("blobs_test.txt", "r") as f:
        for line in f:
            if hash in line:
                lineas = line.split()
                assert lineas[1] is "2" #Comprobamos que es 2 porque al subirlo se vincula una vez, y al hacer link ya son 2

def test6(setup):
    datatransfer, blobservice = setup
    hash = blobservice.upload(datatransfer)

    blobservice.unlink(hash)
    with open("blobs_test.txt", "r") as f:
        for line in f:
            if hash not in line:
                assert True
                return
    
def test7(setup):
    datatransfer, blobservice = setup
    datatransfer.close()
    assert datatransfer.f is None