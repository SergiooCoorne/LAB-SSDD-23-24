"""Module for servants implementations."""
import hashlib
import os

import Ice

import IceDrive


class DataTransfer(IceDrive.DataTransfer):
    """Implementation of an IceDrive.DataTransfer interface."""

    def __init__(self, name_file: str):
        self.name_file = name_file #Direccion del archivo
        self.f = open(name_file, "rb")
        self.size_file = os.path.getsize(name_file) #Tamaño del archivo

    def read(self, size: int, current: Ice.Current = None) -> bytes:
        """Returns a list of bytes from the opened file."""

        with open(self.name_file, "rb") as f:
            if size > self.size_file:
                return f.read(self.size_file) #Esta funcion read no es la misma que la que estamos implementando
            else:
                self.size_file -= size
                return f.read(size)


    def close(self, current: Ice.Current = None) -> None:
        """Close the currently opened file."""
        if self.f:
            self.f.close()
            self.f = None #Para asegurarnos de que el archivo se ha cerrado
        return None

class BlobService(IceDrive.BlobService):
    """Implementation of an IceDrive.BlobService interface."""
    def __init__(self, directory_files: str):
        self.directory_files = directory_files
        self.blob_id_to_file = {} #Diccionario donde se almacenan los BlobIDs de los archivos junto la referencia al archivo

    def link(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id file as linked in some directory."""
        file_contents = [] #Lista donde vamos a ir guardando el contenido del archivo

        # Leemos el contenido del archivo y actualizamos la línea correspondiente
        with open(self.directory_files, 'r') as f:
            for linea in f:
                partes = linea.split()
                if partes and len(partes) >= 2 and partes[0] == blob_id: #Si es el blob_id que buscamos, le sumamos 1 al numero de veces que se ha vinculado
                    veces_asociado = int(partes[1]) + 1
                    nueva_linea = partes[0] + " " + str(veces_asociado) + "\n"
                    file_contents.append(nueva_linea)
                else: #Si no es el blob_id que buscamos, lo añadimos tal cual al archivo
                    file_contents.append(linea)
    
        # Escribimos el contenido actualizado de vuelta al archivo
        with open(self.directory_files, 'w') as f:
            for linea in file_contents:
                f.write(linea)

    def unlink(self, blob_id: str, current: Ice.Current = None) -> None:
        """"Mark a blob_id as unlinked (removed) from some directory."""
        file_contents = []

        # Leemos el contenido del archivo y actualizamos la línea correspondiente
        with open(self.directory_files, 'r') as f:
            for linea in f:
                partes = linea.split()
                if partes[0] == blob_id: #Si es el blob_id que buscamos, le restamos 1 al numero de veces que se ha vinculado
                    veces_asociado = int(partes[1]) - 1
                    if veces_asociado == 0: #Si el numero de veces asociado es 0, se eliminaria del diccionario
                        self.blob_id_to_file.pop(blob_id)
                    else:
                        nueva_linea = partes[0] + " " + str(veces_asociado) + "\n"
                        file_contents.append(nueva_linea)

        # Escribimos el contenido actualizado de vuelta al archivo
        with open(self.directory_files, 'w') as f:
            for linea in file_contents:
                f.write(linea)

    def upload(
        self, blob: IceDrive.DataTransferPrx, current: Ice.Current = None
    ) -> str:
        """Register a DataTransfer object to upload a file to the service."""
        #Primero sacamos el contendio que hay en el archivo asociado al objeto DataTransfer y lo guardamos en una lista
        contenido = blob.read(10)
        #Ahora sacamos el suma SHA256 del contenido del archivo y lo añadimos al archivo de blobs
        blob_id = hashlib.sha256(contenido).hexdigest()
        with open(self.directory_files, 'a') as f:
            f.write(blob_id + " " + "1" + "\n") #Añadimos el blob_id al archivo junto con el numero de veces que se ha vinculado
        


    def download(
        self, blob_id: str, current: Ice.Current = None
    ) -> IceDrive.DataTransferPrx:
        """Return a DataTransfer objet to enable the client to download the given blob_id."""
        #Primero comprobamos que el blob_id se encuentra en el directorio "directory_blobs_id"
        with open(self.directory_files, 'r') as f:
            for linea in f:
                partes = linea.split()
                if partes[0] == blob_id:
                    #Si el blob_id se encuentra en el directorio, creamos un objeto DataTransfer
                    #data_transfer = DataTransfer(self.blob_id_to_file[blob_id])
                    archivo = partes[2]
                    data_transfer = DataTransfer(archivo)
                    prx = current.adapter.addWithUUID(data_transfer)
                    prx_data_transfer = IceDrive.DataTransferPrx.uncheckedCast(prx)
                    return prx_data_transfer
            return None
                

