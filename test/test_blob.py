from blobLocal import DataTransfer
import os
import pytest

@pytest.fixture #Fixture para crear un archivo de prueba
def setup_data_transfer():
    # Crear un archivo de prueba con contenido
    text = 'Prueba 3'
    with open('test_file.txt', 'w') as test_file:
        test_file.write(text)

    # Crear una instancia de DataTransfer usando el archivo de prueba
    data_transfer = DataTransfer('test_file.txt')

    # Añadir la entrada del hash al archivo blobs.txt (Comprueba si ya esta añadida, y si lo está, no la añade mas veces)
    if not is_hash_present('blobs.txt', data_transfer.sumSHA256):
        with open('blobs.txt', 'a') as f:
            f.write(data_transfer.sumSHA256 + '\n')
    
    if not is_text_present('equivalencias.txt', text):
        with open('equivalencias.txt', 'a') as f:
            f.write(text + '\n')

    # yield: Punto de separación entre la configuración y la limpieza
    yield data_transfer
 
def test_read(setup_data_transfer):
    # Probar la función read para leer el contenido del archivo
    content = setup_data_transfer.read(10)
    assert content is not None

def test_close(setup_data_transfer):
    # Probar la función close para cerrar el archivo
    setup_data_transfer.close()
    # Verificar que el archivo esté cerrado
    assert setup_data_transfer.f is None


def is_hash_present(file_path: str, target_hash: str) -> bool:
    """Check if a hash is already present in a file."""
    if not os.path.exists(file_path):
        return False

    with open(file_path, 'r') as f:
        return any(line.strip() == target_hash for line in f)
    

def is_text_present(file_path: str, target_text: str) -> bool:
    """Check if a text is already present in a file."""
    if not os.path.exists(file_path):
        return False

    with open(file_path, 'r') as f:
        return any(line.strip() == target_text.strip() for line in f)