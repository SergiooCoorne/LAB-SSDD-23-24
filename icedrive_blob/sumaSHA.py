import hashlib

def calcular_sha256(file_path):
    """Calcula la suma SHA256 de un archivo."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def guardar_en_archivos_txt(archivo_path, archivos_txt):
    """Guarda el nombre del archivo en el archivo de salida."""
    with open(archivos_txt, 'a') as archivos_file:
        archivos_file.write(f"{archivo_path}\n")
        print(f"El nombre del archivo '{archivo_path}' se ha guardado en '{archivos_txt}'.")

def procesar_archivo(archivo_path, blobs_txt, archivos_txt):
    """Procesa el archivo y guarda la información en los archivos de salida."""
    try:
        suma_sha256 = calcular_sha256(archivo_path)
        with open(blobs_txt, 'a') as blobs_file:
            blobs_file.write(f"{suma_sha256}\n")
        guardar_en_archivos_txt(archivo_path, archivos_txt)
        print(f"La suma SHA256 del archivo '{archivo_path}' se ha añadido en '{blobs_txt}'.")
    except FileNotFoundError:
        print(f"El archivo '{archivo_path}' no se encontró.")

if __name__ == "__main__":
    archivo_path = input("Ingrese la ruta del archivo: ")
    blobs_txt = "blobs.txt"
    archivos_txt = "archivos.txt"
    procesar_archivo(archivo_path, blobs_txt, archivos_txt)
