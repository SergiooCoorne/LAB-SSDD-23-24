"""Module for servants implementations."""
from typing import Set
from .delayed_response import BlobQueryResponse

import hashlib
import os
import random
import string
import Ice
import IceDrive
import threading


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
    def __init__(self, query_publisher, discovery_instance):
    #def __init__(self, path_directory: str):
        path_directory = os.path.expanduser("~")

        # Crear la carpeta si no existe
        folder_name = "ficheros_blob_service"
        folder_path = os.path.join(path_directory, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        self.path_directory = folder_path
        self.directory_files = os.path.join(folder_path, "ficheros_blob_service.txt")
        self.query_publisher = query_publisher
        self.discovery_instance = discovery_instance
        self.expected_responses = {}

        # Comprobar si el archivo existe
        if not os.path.exists(self.directory_files):
            # Si no existe, crear el archivo
            with open(self.directory_files, 'w') as archivo:
                archivo.write("")

    def remove_object_if_exists(self, adapter: Ice.ObjectAdapter, identity: Ice.Identity) -> None:
        """Remove an object from the adapter if exists."""
        if adapter.find(identity) is not None:
            adapter.remove(identity)
            self.expected_responses[identity].set_exception(IceDrive.UnknownBlob()) #Lanzamos la excepcion UnknownBlob para indicar que no 
            #se ha encontrado el blob_id

        del self.expected_responses[identity] #Borramos el objeto Ice.Future asociado a la identidad que le hemos pasado

    def prepare_callback(self, current: Ice.Current) -> IceDrive.BlobQueryResponsePrx:
        """Prepare an Ice.Future object and send the query"""
        future = Ice.Future() #Creamos un objeto Ice.Future (Objeto que todavia no se ha calculado pero se calculara en un futuro)
        reponse = BlobQueryResponse(future) #Creamos un objeto de tipo BlobQueryResponse pasandole el objeto Ice.Future
        prx = current.adapter.addWithUUID(reponse) #Añadimos el objeto al adaptador de objetos y guardamos el proxy de la respuesta
        query_response_prx = IceDrive.BlobQueryResponsePrx.uncheckedCast(prx) #Hacemos un cast del proxy de la respuesta a BlobQueryResponsePrx

        identity = query_response_prx.ice_getIdentity() #Obtenemos la identidad del proxy de la respuesta
        self.expected_responses[identity] = future #Guardamos en el diccionario de respuestas esperadas la identidad y el objeto Ice.Future
        threading.Timer(5.0, self.remove_object_if_exists, (current.adapter, identity)).start() #Creamos un hilo que se ejecutara en 5 segundos y que ejecutara 
        #la funcion remove_object_if_exists pasandole el adaptador de objetos y la identidad. Esto se hace para ahorrar memoria al hacer una llamada de un metodo que no podemos completar
        return query_response_prx
    
    def link(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id file as linked in some directory."""
        print("BlobService-Link by Sergio Cornejo\n") #Mensaje para verificar que se esta usando mi servicio en el cliente

        try:
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
                raise IceDrive.UnknownBlob(str(blob_id))
            
            # Escribimos el contenido actualizado de vuelta al archivo
            try:
                with open(self.directory_files, 'w') as f:
                    for linea in file_contents:
                        f.write(linea)
            except Exception as e:
                print("Error: " + e.reason)
                return None
            
        except IceDrive.UnknownBlob:
            query_response_prx = self.prepare_callback(current)
            self.query_publisher.linkBlob(blob_id, query_response_prx)

    def unlink(self, blob_id: str, current: Ice.Current = None) -> None:
        """"Mark a blob_id as unlinked (removed) from some directory."""
        print("BlobService-Unlink by Sergio Cornejo\n") #Mensaje para verificar que se esta usando mi servicio en el cliente

        try:
            file_contents = []
            found = False
            # Leemos el contenido del archivo y actualizamos la línea correspondiente
            with open(self.directory_files, 'r') as f:
                for linea in f:
                    parts = linea.split()
                    if len(parts) > 0 and parts[0] == blob_id: #Si es el blob_id que buscamos, le restamos 1 
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
                raise IceDrive.UnknownBlob(str(blob_id))

            # Escribimos el contenido actualizado de vuelta al archivo
            try:
                with open(self.directory_files, 'w') as f:
                    for linea in file_contents:
                        f.write(linea)
            except Exception as e:
                print("Error: " + e.reason)
                return None
            
        except IceDrive.UnknownBlob:
            query_response_prx = self.prepare_callback(current)
            self.query_publisher.unlinkBlob(blob_id, query_response_prx)


    def upload(
        self, user: IceDrive.UserPrx, blob: IceDrive.DataTransferPrx, current: Ice.Current = None
    ) -> str:
        """Register a DataTransfer object to upload a file to the service."""
        print("BlobService-Upload by Sergio Cornejo\n") #Mensaje para verificar que se esta usando mi servicio en el cliente

        verify = False
        #Usamos los proxys para comprobar que el usuario pertenece al servicio de Authentication
        ramdon_proxy_authentication = self.discovery_instance.randomAuthentication()
        if(ramdon_proxy_authentication != None):
            proxy_authentication_prx = IceDrive.AuthenticationPrx.uncheckedCast(ramdon_proxy_authentication)

        if(proxy_authentication_prx.verifyUser(user)):
            verify = True

        #Si el usuario está verificado
        if(verify == True):

            #Leemos todo el contenido del archivo en bloques de 2 bytes
            content = b''    
            while True:
                answer = blob.read(2) #El tamaño del bloque es ajustable a nuestro gusto

                content += answer
                if len(answer) == 0:
                    break
            #Aplicamos close() despues de usar el DataTransfer
            blob.close()
                    
            blob_id = hashlib.sha256(content).hexdigest()
            #Si el blob_id ya existe, solo tenemos que incrementar el numero de 
            #veces que se ha vinculado
            if blob_id_exists(blob_id, self.directory_files):
                print("El archivo ya existe en el directorio.\n")
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
        else:
            username = user.getUsername()
            raise IceDrive.Unauthorized(username)
            

    def download(
        self, user: IceDrive.UserPrx, blob_id: str, current: Ice.Current = None
    ) -> IceDrive.DataTransferPrx:
        """Return a DataTransfer objet to enable the client to download the given blob_id."""
        print("BlobService-Download by Sergio Cornejo\n") #Mensaje para verificar que se esta usando mi servicio en el cliente

        try:
            verify = False
            random_proxy_authetication = self.discovery_instance.randomAuthentication()
            if(random_proxy_authetication != None):
                proxy_authetication_prx = IceDrive.AuthenticationPrx.uncheckedCast(random_proxy_authetication)

            if(proxy_authetication_prx.verifyUser(user)):
                verify = True

            if(verify):

                #Comprobamos que el blob_id se encuentra en el directorio "directory_blobs_id" despues de verificar la untenticacion del usuario
                with open(self.directory_files, 'r') as f:
                    for line in f:
                        parts = line.split()
                        if len(parts) > 0 and parts[0] == blob_id:                    
                            file = parts[2]
                            data_transfer = DataTransfer(file)
                            prx = current.adapter.addWithUUID(data_transfer)
                            prx_data_transfer = IceDrive.DataTransferPrx.uncheckedCast(prx)
                            return prx_data_transfer
                        
                    # Si el blob_id no se encuentra en el directorio, lanzamos la excepción UnknownBlob
                    raise IceDrive.UnknownBlob(str(blob_id))
            else:
                username = user.getUsername()
                raise IceDrive.Unauthorized(username)
            
        except IceDrive.UnknownBlob:
            query_response_prx = self.prepare_callback(current)
            self.query_publisher.downloadBlob(blob_id, query_response_prx)
            return self.expected_responses[query_response_prx.ice_getIdentity()]

    def print_proxy_authentication(self):
        """A random proxy of Authentication service"""
        proxy = self.discovery_instance.randomAuthentication()
        print("Proxy Athentication: " + str(proxy) + "\n")
             
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

def blob_id_exists(blob_id: str, directory_files: str) -> bool:
    """Check if the given blob_id already exists in the file."""
    with open(directory_files, 'r') as f:
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
