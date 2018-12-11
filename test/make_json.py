import pyangbind.lib.pybindJSON as pybindJSON
import sys

from helpers import *

from bindingTransceiver import sliceable_transceiver_sdm

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def make_json(sliceid, opticalchannelid, coreid, modeid, ncf, slot_width):
    model = sliceable_transceiver_sdm()
    model.transceiver.slice.add(sliceid)
    model.transceiver.slice[sliceid].optical_channel.add(opticalchannelid)
    model.transceiver.slice[sliceid].optical_channel[opticalchannelid].coreid = coreid
    model.transceiver.slice[sliceid].optical_channel[opticalchannelid].modeid = modeid
    model.transceiver.slice[sliceid].optical_channel[opticalchannelid].frequency_slot.ncf = ncf
    model.transceiver.slice[sliceid].optical_channel[opticalchannelid].frequency_slot.slot_width = slot_width
    # for i in new_slice['sliceid'].iteritems():
        #print(i)
    # for intf, conf in yml['interface'].iteritems():
    #     print("Instantiating model for {}".format(intf))
    #     intf_model = model.interfaces.interface.add(intf)
    #     intf_model.description = conf['description']
    #     ip_model = intf_model.ipv4.address.add(conf['address']['prefix'])
    #     ip_model.netmask = conf['address']['netmask']
    return pybindJSON.dumps(model)


def main():
    result_json = make_json(1, 1, "Core19", "LP01", 137, 2)
    print(result_json)

    write_file('sliceable_transceiver.json', result_json)


if __name__ == '__main__':
    sys.exit(main())
