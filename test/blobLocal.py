import hashlib
import os

class DataTransfer:
    def __init__(self, file_path: str):
        """Initialize the DataTransfer object."""
        self.file_path = file_path
        self.size_file = os.path.getsize(file_path)

        self.f = open(file_path, "rb")
        self.file_content = self.f.read() #Ya se estan leyendo en bytes, con lo que no haria falta aplicar encode('utf-8')

        self.sumSHA256 = hashlib.sha256(self.file_content).hexdigest() #Realiza el hash del contenido del archivo

        if not self.is_hash_present('blobs.txt', self.sumSHA256):
            with open('blobs.txt', 'a') as f:
                f.write(self.sumSHA256)
                f.write('\n')

    def read(self, size: int, current = None):
        """Returns a list of bytes from the opened file."""
        content_list = []

        with open(self.file_path, "rb") as f:
            chunck = f.read(size)
            if not chunck:
                return None
            content_list.append(chunck)
            return content_list
        
    def close(self, current = None):
        """Close the currently opened file."""
        if self.f:
            self.f.close()
            self.f = None #Para asegurarnos de que el archivo se ha cerrado
        return None        

    @staticmethod
    def is_hash_present(file_path: str, target_hash: str) -> bool:
        """Check if a hash is already present in a file."""
        if not os.path.exists(file_path):
            return False

        with open(file_path, 'r') as f:
            return any(line.strip() == target_hash for line in f)




        
