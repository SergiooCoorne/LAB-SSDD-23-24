from typing import List
import os
import shutil
import hashlib
import pytest
import sys

import Ice

import IceDrive

from blob import BlobService, DataTransfer, generate_name, create_file, blob_id_exists, find_and_delete_file

class TestClientApp(Ice.Application):
   
    @pytest.fixture
    def create_blob_and_data_trasnfer_prx(self, args: List[str]):
        proxy_b = self.communicator().stringToProxy(args[1])
        blob_prx = IceDrive.BlobServicePrx.checkedCast(proxy_b)

        proxy_dt = self.communicator().stringToProxy(args[2])
        dt_prx = IceDrive.DataTransferPrx.checkedCast(proxy_dt)
    
        return blob_prx, dt_prx
    
    def comprobarProxys(self, blob_prx, dt_prx):
        assert blob_prx is not None, "Error: invalid proxy"
        assert dt_prx is not None, "Error: invalid proxy DataTransfer"

