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
            #current.adapter.remove(current.id)
            self.f.close()
            self.f = None #Para asegurarnos de que el archivo se ha cerrado
        return None

class BlobService(IceDrive.BlobService):
    """Implementation of an IceDrive.BlobService interface."""
    def __init__(self, directory_files: str):
        self.directory_files = directory_files
        self.blob_id_to_file = {} 
        #Diccionario donde se almacenan los BlobIDs de los archivos junto 
        #la referencia al archivo por si no queremos acceder al archivo de persistencia 
        #para ver la relacion entre el blob_id y el archivo

    def link(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id file as linked in some directory."""
        file_contents = [] #Lista donde vamos a ir guardando el contenido del archivo

        # Leemos el contenido del archivo y actualizamos la línea correspondiente
        encontrado = False
        with open(self.directory_files, 'r') as f:
            for linea in f:
                partes = linea.split()
                if partes and len(partes) >= 2 and partes[0] == blob_id: #Si es el blob_id que buscamos, 
                    #le sumamos 1 al numero de veces que se ha vinculado
                    encontrado = True
                    veces_asociado = int(partes[1]) + 1
                    nombre_archivo = partes[2]
                    nueva_linea = partes[0] + " " + str(veces_asociado) + " " + nombre_archivo + "\n"
                    file_contents.append(nueva_linea)
                else: #Si no es el blob_id que buscamos, lo añadimos tal cual al archivo
                    file_contents.append(linea)
        #Si no se encuentra el blob_id en el directorio, lanzamos la excepcion UnknownBlob
        if not encontrado:
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
        encontrado = False
        # Leemos el contenido del archivo y actualizamos la línea correspondiente
        with open(self.directory_files, 'r') as f:
            for linea in f:
                partes = linea.split()
                if partes[0] == blob_id: #Si es el blob_id que buscamos, le restamos 1 
                        #al numero de veces que se ha vinculado
                    encontrado = True
                    nombre_archivo = partes[2]
                    veces_asociado = int(partes[1]) - 1
                    if veces_asociado <= 0: #Si el numero de veces asociado es 0, 
                            #o menor que 0, se eliminaria del diccionario
                            #self.blob_id_to_file.pop(blob_id) (Linea comentada porque el diccionario a la hora 
                            #de probar el programa esta vacio)
                        find_and_delete_file(nombre_archivo) #Borramos el archivo del sistema de archivos
                    else:                            
                        nueva_linea = partes[0] + " " + str(veces_asociado) + " " + nombre_archivo +"\n"
                        file_contents.append(nueva_linea)
                else:
                    file_contents.append(linea)
        #Si no se encuentra el blob_id en el directorio, lanzamos la excepcion UnknownBlob
        if not encontrado:
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
            respuesta = blob.read(2)

            #Para comprobar si la lectura se ha hecho de forma incorrecta
            if len(respuesta) != 2 and len(respuesta) != 0:
                raise IceDrive.FailedToReadData("Error al leer el archivo")

            content += respuesta
            if len(respuesta) == 0:
                break

        blob_id = hashlib.sha256(content).hexdigest()
        #Si el blob_id ya existe, solo tenemos que incrementar el numero de 
        #veces que se ha vinculado
        if blob_id_exists(self, blob_id):
            self.link(blob_id)
            return blob_id

        #Si no existe el blob_id, creamos el archivo y lo añadimos al directorio
        name_file_aletory = generate_name()
        create_file(name_file_aletory, content)
        
        try:
            with open(self.directory_files, 'a') as f:
                f.write(blob_id + " " + "0 " + name_file_aletory + "\n") #Añadimos el blob_id 
                #al archivo junto con el numero de veces que se ha vinculado (0) y el nombre del archivo
        except Exception as e:
            print("Error: " + e.reason)
            return None

        self.blob_id_to_file[blob_id] = name_file_aletory #Añadimos el blob_id al diccionario 
        #junto con el nombre del archivo
        #Aplicamos close() despues de usar el DataTransfer
        blob.close()
        return blob_id #Devolvemos el blob_id

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
                
        # Si el blob_id no se encuentra en el directorio, lanzamos la excepción UnknownBlob
        raise IceDrive.UnknownBlob(f"El blob_id no se encuentra en el directorio.")
                

def generate_name():
    letras = string.ascii_lowercase
    longitud = random.randint(5, 10)
    nombre = ''.join(random.choice(letras) for _ in range(longitud))
    return nombre + ".txt"

def create_file(nombre, contenido_bytes):
    with open(nombre, 'wb') as archivo:
        archivo.write(contenido_bytes)

def blob_id_exists(self, blob_id: str) -> bool:
    """Check if the given blob_id already exists in the file."""
    with open(self.directory_files, 'r') as f:
        for linea in f:
            partes = linea.split()
            if partes and len(partes) >= 3 and partes[0] == blob_id:
                return True
    return False

def find_and_delete_file(name_file):
    # Obtén el directorio actual
    current_directory = os.getcwd()

    # Recorre los archivos en el directorio actual
    for root, dirs, files in os.walk(current_directory):
        if name_file in files:
            # Construye la ruta completa del archivo
            ruta_archivo = os.path.join(root, name_file)

            # Intenta eliminar el archivo
            try:
                os.remove(ruta_archivo)
                print(f"El archivo {name_file} ha sido eliminado exitosamente.")
            except Exception as e:
                print(f"No se pudo eliminar el archivo {name_file}. Error: {e}")

       