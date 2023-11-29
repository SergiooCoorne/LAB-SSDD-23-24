import hashlib
import os

class DataTransfer:
    def __init__(self, file_path: str):
        """Initialize the DataTransfer object."""
        self.file_path = file_path #Direccion del archivo asociado a la interfaz DataTransfer
        self.f = open(file_path, "rb")
        self.size_file = os.path.getsize(file_path) #Tamaño del archivo


    def read(self, size: int, current = None):
        """Returns a list of bytes from the opened file."""
        content_list = [] #Lista donde se almacenara el contenido del archivo

        with open(self.file_path, "rb") as f:
            while True:
                chunk = f.read(size)
                #chunk = f.read(size).decode('utf-8')
                content_list.append(chunk)
                if not chunk:
                    break

        return content_list
                    
    def close(self, current = None):
        """Close the currently opened file."""
        if self.f:
            self.f.close()
            self.f = None #Para asegurarnos de que el archivo se ha cerrado
        return None

class BlobService:
    #Recordar que el blob_id es el hash del archivo
    """Implementación de una interfaz IceDrive.BlobService."""
    def __init__(self, path: str):
        """Initialize the BlobService object."""
        self.path = path #El path va a ser el directorio donde se almacenan los BlobIDs de los archivos junto al numero de veces que se han vinculado
        self.blob_id_to_file = {} #Diccionario donde se almacenan los BlobIDs de los archivos junto la referencia al archivo

    def link(self, blob_id: str) -> None:
        """Mark a blob_id file as linked in some directory."""
        file_contents = [] #Lista donde vamos a ir guardando el contenido del archivo

        # Leemos el contenido del archivo y actualizamos la línea correspondiente
        with open(self.path, 'r') as f:
            for linea in f:
                partes = linea.split()
                if partes and len(partes) >= 2 and partes[0] == blob_id: #Si es el blob_id que buscamos, le sumamos 1 al numero de veces que se ha vinculado
                    veces_asociado = int(partes[1]) + 1
                    nueva_linea = partes[0] + " " + str(veces_asociado) + "\n"
                    file_contents.append(nueva_linea)
                else: #Si no es el blob_id que buscamos, lo añadimos tal cual al archivo
                    file_contents.append(linea)
    
        # Escribimos el contenido actualizado de vuelta al archivo
        with open(self.path, 'w') as f:
            for linea in file_contents:
                f.write(linea)

    def unlink(self, blob_id: str) -> None:
        """Mark a blob_id as unlinked (removed) from some directory."""
        file_contents = []

        # Leemos el contenido del archivo y actualizamos la línea correspondiente
        with open(self.path, 'r') as f:
            for linea in f:
                partes = linea.split()
                if partes[0] == blob_id: #Si es el blob_id que buscamos, le restamos 1 al numero de veces que se ha vinculado
                    veces_asociado = int(partes[1]) - 1
                    if veces_asociado == 0: #Si el numero de veces asociado es 0, no lo añadimos al archivo, con lo que se eliminaria
                        self.blob_id_to_file.pop(blob_id) #Eliminamos el blob_id del diccionario
                    else:
                        nueva_linea = partes[0] + " " + str(veces_asociado) + "\n"
                        file_contents.append(nueva_linea)
                else:
                    file_contents.append(linea) #Si no es el blob_id que buscamos, lo añadimos tal cual al archivo

        # Escribimos el contenido actualizado de vuelta al archivo
        with open(self.path, 'w') as f:
            for linea in file_contents:
                f.write(linea)

    def upload(self, blob: DataTransfer) -> str:
        """Registra un objeto DataTransfer para cargar un archivo al servicio."""

        contenido = b''.join(blob.read(blob.size_file)) #Leemos el contenido del archivo y lo convertimos en una secuencia de bytes
        hash = hashlib.sha256(contenido).hexdigest() #Sacamos el hash del contenido del archivo

        if not search_hash(self.path, hash): #Si el hash no esta en el archivo, lo añadimos
            with open(self.path, 'a') as f:
                f.write(hash + " " + "1") #Añadimos el hash y el numero de veces que se ha vinculado (Al ser la primera vez, es 1)
                f.write('\n')

            # Asociamos el blob_id con la ruta del archivo original en el diccionario
            self.blob_id_to_file[hash] = blob.file_path
            print(f"DEBUG: Se ha agregado {hash} con la ruta {blob.file_path} al diccionario.")

            return hash #Devolvemos el hash
        else:
            # Asociamos el blob_id con la ruta del archivo original en el diccionario
            self.blob_id_to_file[hash] = blob.file_path
            return hash

    def download(self, blob_id: str) -> DataTransfer:
        """Devuelve un objeto de transferencia de datos para permitir que el cliente descargue la identificación del blob proporcionada."""
        file_path = self.blob_id_to_file[blob_id] #Obtenemos la ruta del archivo original a partir del blob_id
        if file_path:
            return DataTransfer(file_path)
        else:
            print("No se encontró el blob_id {blob_id}")                


def search_hash(archivo, hash):
    try:
        with open(archivo, 'r') as f:
            for line in f:
                if hash in line:
                    return True
            return False
    except:
        print("Error al abrir el archivo")
        return False
    
def is_hash_present(file_path: str, target_hash: str) -> bool:
        """Check if a hash is already present in a file."""
        if not os.path.exists(file_path):
            return False

        with open(file_path, 'r') as f:
            return any(line.strip() == target_hash for line in f)
