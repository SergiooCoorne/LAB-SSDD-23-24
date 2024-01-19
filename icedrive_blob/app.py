"""Authentication service application."""

import logging
from typing import List

import Ice
import IceStorm

import IceDrive
import threading
import time

from threading import Timer
from .blob import BlobService 
from .blob import DataTransfer
from .discovery import Discovery
from .delayed_response import BlobQuery

#Clase que ejecuta mi cliente de BlobService
class BlobApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""
    
    def run(self, args: List[str]) -> int:
        """Execute the code for the BlobApp class."""
        
        adapter = self.communicator().createObjectAdapter("BlobAdapter")

        announce_subcriber = Discovery()
        announce_subcriber_pr = adapter.addWithUUID(announce_subcriber)
        announce_subcriber_prxy = IceDrive.DiscoveryPrx.uncheckedCast(announce_subcriber_pr)

        properties = self.communicator().getProperties() #Obtenemos las propiedades del comunicador
        topic_name_discovery = properties.getProperty("Discovery.Topic") #Obtenemos el nombre del topic cuya clave es "TopicName"
        topic_name_blob = properties.getProperty("Blob.DeferredResolution.Topic") #Obtenemos el nombre del topic para la parte de resolucion diferida

        #Obtenemos un topic del tipo Discovery para poder hacer nuestro anunciamiento de servicio porteriormente
        topic_discovery = self.get_topic(topic_name_discovery)
        topic_blob = self.get_topic(topic_name_blob)
        #PARTE DE RESOLUCION DIFERIDA
        #Ahora vamos a crear un publicador de querys. Este va a ser el encargado de enviar las peticiones a las demas instancias BlobService
        query_pub = IceDrive.BlobQueryPrx.uncheckedCast(topic_blob.getPublisher())
        #Tambien creamos una instancia de la clase que va a recibir las peticiones de otros BlobServices
        blob = BlobService(None, announce_subcriber)
        query_receiver = BlobQuery(blob) #Creamos nuestro receptor de peticiones pasandole una instancia de BlobService
        
        #Vamos a crear un sirvitente de BlobService para poder realizar las operaciones
        servant = BlobService(query_pub, announce_subcriber)
        servant_blob_proxy = adapter.addWithUUID(servant)
        query_receiver_proxy = adapter.addWithUUID(query_receiver)

        #ANUNCIAMIENTO DE NUESTRO SERVICIO#
        #Obtenemos el publisher que anuncia nuestro servicio castenado el topic que hemos obtenido a un topic del tipo Discovery
        publisher = IceDrive.DiscoveryPrx.uncheckedCast(topic_discovery.getPublisher())
        theread = threading.Thread(target = self.annouceProxy, args = (publisher, (servant_blob_proxy)))
        theread.daemon = True 
        theread.start()

        #SUBSCRIPCION A LOS TOPICS DE DESCUBRIMIENTO
        topic_discovery.subscribeAndGetPublisher({}, announce_subcriber_prxy)
        
        #PARTE DE LA SUBSCRIPCION PARA RESOLUCION DIFERIDA
        topic_blob.subscribeAndGetPublisher({}, query_receiver_proxy)

        #Proxys del sirviente
        logging.info("Proxy BlobService: %s\n", servant_blob_proxy)

        adapter.activate()
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0

    def get_topic(self, topic_name):
        """Returns proxy for the TopicManager from IceStorm."""
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(
            self.communicator().propertyToProxy("IceStorm.Proxy")
        )
        
        try:
            return topic_manager.retrieve(topic_name)
        except IceStorm.NoSuchTopic: 
            return topic_manager.create(topic_name)
        
    def annouceProxy(self, publisher, prx):
        while True:
            publisher.announceBlobService(
                IceDrive.BlobServicePrx.checkedCast(prx),
                None
            )
            print("Anuncio enviado. Proxy: " + str(prx) + "\n")
            time.sleep(5)

    def proxyAuthentication(self, servant):
        while True:
            servant.print_proxy_authentication()
            time.sleep(5)

