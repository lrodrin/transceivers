import pyangbind.lib.pybindJSON as pybindJSON
import sys

from bindingTransceiver import sliceable_transceiver_sdm

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def make_json(sliceid, opticalchannelid, coreid):
    model = sliceable_transceiver_sdm()
    model.transceiver.slice.add(sliceid)
    model.transceiver.slice[sliceid].optical_channel.add(opticalchannelid)
    model.transceiver.slice[sliceid].optical_channel[opticalchannelid].coreid = coreid
    # for i in new_slice['sliceid'].iteritems():
        #print(i)
    # for intf, conf in yml['interface'].iteritems():
    #     print("Instantiating model for {}".format(intf))
    #     intf_model = model.interfaces.interface.add(intf)
    #     intf_model.description = conf['description']
    #     ip_model = intf_model.ipv4.address.add(conf['address']['prefix'])
    #     ip_model.netmask = conf['address']['netmask']
    print("Done")
    return pybindJSON.dumps(model)


def main():
    result_json = make_json("1", "1", "Core19")
    print(result_json)

    # write_file('sliceable_transceiver.json', result_json)


if __name__ == '__main__':
    sys.exit(main())
