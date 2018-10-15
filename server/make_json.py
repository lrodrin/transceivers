#!/usr/bin/env python

import pyangbind.lib.pybindJSON as pybindJSON
from server.binding import sliceable_transceiver_sdm
from server.helpers import *
import sys


__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def make_json():
    model = sliceable_transceiver_sdm()
    new_slice = model.transceiver.slice.add(1)
    for i in new_slice['sliceid'].iteritems():
        print(i)
    # for intf, conf in yml['interface'].iteritems():
    #     print("Instantiating model for {}".format(intf))
    #     intf_model = model.interfaces.interface.add(intf)
    #     intf_model.description = conf['description']
    #     ip_model = intf_model.ipv4.address.add(conf['address']['prefix'])
    #     ip_model.netmask = conf['address']['netmask']
    print("Done")
    return pybindJSON.dumps(model, mode='ietf')



def main():
    result_json = make_json()

    write_file('sliceable_transceiver.json', result_json)


if __name__ == '__main__':
    sys.exit(main())
