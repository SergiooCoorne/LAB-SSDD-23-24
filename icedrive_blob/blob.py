"""Module for servants implementations."""
import hashlib
import os
import random
import string

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
        content = b''
        
        if size > self.size_file:
            #Esta funcion read no es la misma que la que estamos implementando
            content = self.f.read(self.size_file)
            #Comprobamos si la lectura ha sido correcta
            if len(content) != self.size_file:
                raise IceDrive.FailedToReadData("Error al leer el archivo")
            return content
        else:
            self.size_file -= size
            content = self.f.read(size)
            #Comprobamos si la lectura ha sido correcta
            if len(content) != size:
                raise IceDrive.FailedToReadData("Error al leer el archivo")
            return content

    def close(self, current: Ice.Current = None) -> None:
        """Close the currently opened file."""
        if self.f:
            current.adapter.remove(current.id)
            self.f.close()
            self.f = None #Para asegurarnos de que el archivo se ha cerrado
        return None

class BlobService(IceDrive.BlobService):
    """Implementation of an IceDrive.BlobService interface."""
    def __init__(self, path_directory: str):
        self.path_directory = path_directory
        self.directory_files = path_directory + "/" + "ficheros_blob_service.txt"

        # Comprobar si el archivo existe
        if not os.path.exists(self.directory_files):
            # Si no existe, crear el archivo
            with open(self.directory_files, 'w') as archivo:
                archivo.write("")
        
    
    def link(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id file as linked in some directory."""
        file_contents = [] #Lista donde vamos a ir guardando el contenido del archivo

        # Leemos el contenido del archivo y actualizamos la línea correspondiente
        found = False
        with open(self.directory_files, 'r') as f:
            for line in f:
                parts = line.split()
                if parts and len(parts) >= 2 and parts[0] == blob_id: #Si es el blob_id que buscamos, 
                    #le sumamos 1 al numero de veces que se ha vinculado
                    found = True
                    links = int(parts[1]) + 1
                    filename = parts[2]
                    nueva_linea = parts[0] + " " + str(links) + " " + filename + "\n"
                    file_contents.append(nueva_linea)
                else: #Si no es el blob_id que buscamos, lo añadimos tal cual al archivo
                    file_contents.append(line)
        #Si no se encuentra el blob_id en el directorio, lanzamos la excepcion UnknownBlob
        if not found:
            raise IceDrive.UnknownBlob(f"El blob_id no se encuentra en el directorio.")
        
        # Escribimos el contenido actualizado de vuelta al archivo
        try:
            with open(self.directory_files, 'w') as f:
                for linea in file_contents:
                    f.write(linea)
        except Exception as e:
            print("Error: " + e.reason)
            return None

    def unlink(self, blob_id: str, current: Ice.Current = None) -> None:
        """"Mark a blob_id as unlinked (removed) from some directory."""
        file_contents = []
        found = False
        # Leemos el contenido del archivo y actualizamos la línea correspondiente
        with open(self.directory_files, 'r') as f:
            for linea in f:
                parts = linea.split()
                if parts[0] == blob_id: #Si es el blob_id que buscamos, le restamos 1 
                        #al numero de veces que se ha vinculado
                    found = True
                    filename = parts[2]
                    links = int(parts[1]) - 1
                    if links <= 0: #Si el numero de veces asociado es 0, 
                            #o menor que 0, se elimina el archivo del sistema de archivos
                        find_and_delete_file(filename) #Borramos el archivo del sistema de archivos
                    else:                            
                        new_line = parts[0] + " " + str(links) + " " + filename +"\n"
                        file_contents.append(new_line)
                else:
                    file_contents.append(linea)
        #Si no se encuentra el blob_id en el directorio, lanzamos la excepcion UnknownBlob
        if not found:
            raise IceDrive.UnknownBlob(f"El blob_id no se encuentra en el directorio.")

        # Escribimos el contenido actualizado de vuelta al archivo
        try:
            with open(self.directory_files, 'w') as f:
                for linea in file_contents:
                    f.write(linea)
        except Exception as e:
            print("Error: " + e.reason)
            return None

    def upload(
        self, blob: IceDrive.DataTransferPrx, current: Ice.Current = None
    ) -> str:
        """Register a DataTransfer object to upload a file to the service."""

        #Leemos todo el contenido del archivo en bloques de 2 bytes
        content = b''    
        while True:
            answer = blob.read(2) #El tamaño del bloque es ajustable a nuestro gusto

            #Para comprobar si la lectura se ha hecho de forma incorrecta
            if len(answer) != 2 and len(answer) != 0:
                raise IceDrive.FailedToReadData("Error al leer el archivo")

            content += answer
            if len(answer) == 0:
                break

        #Aplicamos close() despues de usar el DataTransfer
        blob.close()
        
        blob_id = hashlib.sha256(content).hexdigest()
        #Si el blob_id ya existe, solo tenemos que incrementar el numero de 
        #veces que se ha vinculado
        if blob_id_exists(self, blob_id):
            self.link(blob_id)
            return blob_id

        #Si no existe el blob_id, creamos el archivo y lo añadimos al directorio
        name_file_aletory = generate_name()
        path = create_file(name_file_aletory, content, self.path_directory)
        
        #Escribimos en nuestro archivo que relaciona los blob_id con los archivos
        try:
            with open(self.directory_files, 'a') as f:
                #path = os.path.abspath(f.name)
                f.write(blob_id + " " + "0 " + path + "\n") #Añadimos el blob_id 
                #al archivo junto con el numero de veces que se ha vinculado (0) y el nombre del archivo
        except Exception as e:
            print("Error: " + e.reason)
            return None

        return blob_id #Devolvemos el blob_id

    def download(
        self, blob_id: str, current: Ice.Current = None
    ) -> IceDrive.DataTransferPrx:
        """Return a DataTransfer objet to enable the client to download the given blob_id."""
        #Primero comprobamos que el blob_id se encuentra en el directorio "directory_blobs_id"
        with open(self.directory_files, 'r') as f:
            for line in f:
                parts = line.split()
                if parts[0] == blob_id:                    
                    file = parts[2]
                    data_transfer = DataTransfer(file)
                    prx = current.adapter.addWithUUID(data_transfer)
                    prx_data_transfer = IceDrive.DataTransferPrx.uncheckedCast(prx)
                    return prx_data_transfer
                
        # Si el blob_id no se encuentra en el directorio, lanzamos la excepción UnknownBlob
        raise IceDrive.UnknownBlob(f"El blob_id no se encuentra en el directorio.")
                

def generate_name():
    letras = string.ascii_lowercase
    longitud = random.randint(5, 10)
    nombre = ''.join(random.choice(letras) for _ in range(longitud))
    return nombre + ".txt"

def create_file(nombre, contenido_bytes, path_directory):
    path = os.path.join(path_directory, nombre)

    with open(path, 'wb') as archivo:
        archivo.write(contenido_bytes)

    return path

def blob_id_exists(self, blob_id: str) -> bool:
    """Check if the given blob_id already exists in the file."""
    with open(self.directory_files, 'r') as f:
        for line in f:
            parts = line.split()
            if parts and len(parts) >= 3 and parts[0] == blob_id:
                return True
    return False

def find_and_delete_file(name_file):
    """Find and delete a file in the current directory."""
    try:
        os.remove(name_file)
        print(f"El archivo ha sido eliminado exitosamente.")
    except Exception as e:
        print(f"No se pudo eliminar el archivo. Error: {e}")

       
