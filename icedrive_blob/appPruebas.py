"""Authentication service application."""

import logging
from typing import List

import Ice
import IceStorm

import IceDrive
import threading

from .blob import BlobService 
from .blob import DataTransfer
from .discovery import Discovery
from .delayed_response import BlobQuery

#Clase con la que he estado ejecutando pruebas para verificar el funcionamiento de los metodos
class BlobAppPruebas(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""
    
    def run(self, args: List[str]) -> int:
        """Execute the code for the BlobApp class."""
        path_directory = "/home/sergio/Escritorio/ficheros_blob_service"

        adapter = self.communicator().createObjectAdapter("BlobAdapter")
        adapter.activate()

        properties = self.communicator().getProperties() #Obtenemos las propiedades del comunicador
        topic_name = properties.getProperty("Discovery") #Obtenemos el nombre del topic cuya clave es "TopicName"

        #Ahora obtenemos el manejador de topics a traves de castear el proxy que nos devuelve el communicator con la clave "IceStorm.TopicManager.Proxy"
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(
            self.communicator().propertyToProxy("IceStorm.TopicManager.Proxy")
        )

        #Intentamos obtener el topic con el nombre que hemos definido antes
        try:
            topic = topic_manager.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_manager.create(topic_name)

        #Obtenemos el publisher que anuncia nuestro servicio castenado el topic que hemos obtenido a un topic del tipo Discovery
        publisher = IceDrive.DiscoveryPrx.uncheckedCast(topic.getPublisher())

        #Ahora vamos a crear un publicador de querys. Este va a ser el encargado de enviar las peticiones a las demas instancias BlobService
        query_pub = IceDrive.BlobQueryResponsePrx.uncheckedCast(topic.getPublisher())
        #Tambien creamos una instancia de la clase que va a recibir las peticiones de otros BlobServices
        blob = BlobService(path_directory, [], query_pub)
        query_receiver = BlobQuery(blob)

        #Vamos a crear un sirvitente de BlobService para poder realizar las operaciones
        
        servant = BlobService(path_directory, [], query_pub)
        servant_blob_proxy = adapter.addWithUUID(servant)
        query_receiver_proxy = adapter.addWithUUID(query_receiver)

        #Parte de la subscripcion al topic
        topic.subscribeAndGetPublisher({}, query_receiver_proxy)

        #Hacemos el que publisher anuncie el proxy de nuestro servicio
        #publisher.announceBlobService(IceDrive.BlobServicePrx.checkedCast(servant_blob_proxy))
        #De esta manera en vez de anunciarlo solo una vez, lo estamos anunciando cada 5 segundos
        threading.Timer(5.0, publisher.announceBlobService, (IceDrive.BlobServicePrx.checkedCast(servant_blob_proxy),)).start()

        #Vamos a crear un sirvitente de DataTransfer para poder realizar Upload()
        #archivo = "/home/sergio/Escritorio/VSCodeLinux/LAB-SSDD-23-24/icedrive_blob/prueba2.txt" #Archivo que vamos a subir

        #servant_datatransfer = DataTransfer(archivo)
        #Los añadimos al adaptador de objetos para que nos de el proxy y asi poder realizar su invocacion remota mediante el cliente
        #servant_dt_proxy = adapter.addWithUUID(servant_datatransfer)

        #Proxys de los dos sirvientes
        logging.info("Proxy BlobService: %s", servant_blob_proxy)
        #logging.info("Proxy2 DataTransfer: %s", servant_dt_proxy)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0

#Cliente que me he creado para poder verificar el funcionamiento de los metodos
class ClientAppPruebas(Ice.Application):
    """Client application."""
    def run(self, args: List[str]) -> int:
        """Code to be run by the application."""
        if len(args) != 3:
            print("Error: El numero de proxys proporcionados no es correcto")
            return 1
        
        #Obtencion de un objeto proxy de BlobService
        proxy = self.communicator().stringToProxy(args[1])
        blob_prx = IceDrive.BlobServicePrx.checkedCast(proxy)

        if not blob_prx:
            print("Error: Proxy Blob invalido")
            return 1
        
        #Obtencion de un objeto proxy de DataTransfer
        prx = self.communicator().stringToProxy(args[2])
        dt_prx = IceDrive.DataTransferPrx.checkedCast(prx)

        if not dt_prx:
            print("Error: Proxy DataTransfer invalido")
            return 1
        
        # -----Pruebas de las funciones-----
        #blob_id = "90cc11e4868e4c93e8da07d9bcbbe90bb39a1eed1558440ac60749a08bf0e2ee"
        #print("-----------Subida de un archivo al servidor-----------")
        #blob_id = self.pruebaUpload(blob_prx, dt_prx)
        #print("-----------Cerrando archivo despues de la subida-----------")
        #dt_prx.close()
        #print("Bajada de un archivo del servidor\n-----------")
        #self.pruebaDonwload(blob_prx, blob_id)
        #print("Incrementando numero de links\n-----------")
        #blob_prx.link(blob_id)
        #print("Decrementando numero de links\n-----------")
        #blob_prx.unlink(blob_id)


    def pruebaDonwload(self, blob_prx, blob_id):
        data_transfer_prx = blob_prx.download(blob_id)

        if not data_transfer_prx:
            print("\nError al obtener el proxy de DataTransfer\n")
            return 1
        else: 
            print("Proxy obtenido correctamente\n")

        print("Datos del archivo asociado al objeto DataTransfer:\n")
        #print(data_transfer_prx.read(10))
        datos = data_transfer_prx.read(100)
        datos_decode = datos.decode("utf-8")
        print(datos_decode + "\n")

    def pruebaUpload(self, blob_prx, dt_prx):
        blob_id = blob_prx.upload(dt_prx)

        if blob_id != None:
            print("Archivo subido correctamente\n")
        return blob_id
