import netconf.util as ncutil
from netconf import nsmap_update, server

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

MODEL_NS = "urn:sliceable-transceiver-sdm"
nsmap_update({'pfx': MODEL_NS})


class MyServer(object):
    def __init__(self, user, pw):
        controller = server.SSHUserPassController(username=user, password=pw)
        self.server = server.NetconfSSHServer(server_ctl=controller, server_methods=self)

    def nc_append_capabilities(self, caps):
        ncutil.subelm(caps, "capability").text = MODEL_NS

    def rpc_my_cool_rpc(self, session, rpc, *params):
        data = ncutil.elm("data")
        data.append(ncutil.leaf_elm("pfx:result", "RPC result string"))
        return data


server = MyServer("test", "test")
