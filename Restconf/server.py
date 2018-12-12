import json

import pyangbind.lib.pybindJSON as pybindJSON
import subprocess

from flask import Flask, request
from bindingTransceiver import sliceable_transceiver_sdm

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

app = Flask('server')

model = sliceable_transceiver_sdm()


# GET OPERATIONS
@app.route('/api/transceiver', methods=['GET'])
def get_transceiver():
    return pybindJSON.dumps(model)


@app.route('/api/transceiver/slices', methods=['GET'])
def get_slices():
    return pybindJSON.dumps(model.transceiver)


# POST OPERATIONS
@app.route('/api/transceiver/slice', methods=['POST'])
def new_slice():
    payload = request.json
    sliceid = payload['sliceid']
    if sliceid not in model.transceiver.slice:
        opticalchannelid = payload['opticalchannelid']
        coreid = payload['coreid']
        modeid = payload['modeid']
        ncf = payload['ncf']
        slot_width = payload['slot_width']
        create_slice(coreid, modeid, ncf, opticalchannelid, sliceid, slot_width)
        return "Created slice %s: %s" % (sliceid, json.dumps(payload))
    else:
        return "Slice %s exists", sliceid


def create_slice(coreid, modeid, ncf, opticalchannelid, sliceid, slot_width):
    model.transceiver.slice.add(sliceid)
    model.transceiver.slice[sliceid].optical_channel.add(opticalchannelid)
    model.transceiver.slice[sliceid].optical_channel[opticalchannelid].coreid = coreid
    model.transceiver.slice[sliceid].optical_channel[opticalchannelid].modeid = modeid
    model.transceiver.slice[sliceid].optical_channel[opticalchannelid].frequency_slot.ncf = ncf
    model.transceiver.slice[sliceid].optical_channel[opticalchannelid].frequency_slot.slot_width = slot_width


# @app.route('/api/transceiver/slice/<int:_id>', methods=['POST'])
# def new_opticalchannel(_id):
#     payload = request.json
#     for sliceid in model.transceiver.slice.iteritems():
#         # if _id == sliceid:
#         sliceid.optical_channel.add(payload['opticalchannelid'])
#     return "Created: {} \n".format(payload)
#
# @app.route('/api/transceiver/slice/<int:_id>', methods=['POST'])
# def new_opticalsignal(_id):
#     payload = request.json
#     for sliceid in model.transceiver.slice.iteritems():
#         # if _id == sliceid:
#         sliceid.optical_channel.add(payload['opticalchannelid'])
#     return "Created: {} \n".format(payload)


@app.route('/api/config', methods=['POST'])
def startup_config():
    process_name = request.args.keys()
    subprocess.call(process_name[0])
    return "Started configuration: {} \n".format(process_name)


@app.route('/api/monitor', methods=['POST'])
def startup_monitor():
    process_name = request.args.keys()
    subprocess.call(process_name[0])
    return "Started monitoring: {} \n".format(process_name)


@app.route('/api/matlab', methods=['POST'])
def startup_matlab():
    process_name = request.args.keys()
    subprocess.call(process_name[0])
    return "Started matlab: {} \n".format(process_name)


# DELETE OPERATIONS
@app.route('/api/transceiver/slice', methods=['DELETE'])
def delete_slice():
    payload = request.json
    sliceid = payload['sliceid']
    if sliceid in model.transceiver.slice:
        model.transceiver.slice.delete(sliceid)
        return "Deleted slice %s: %s" % (sliceid, json.dumps(payload))
    else:
        return "Slice %s not exists", sliceid


if __name__ == '__main__':
    app.run(host='10.1.16.53', port=5000, debug=True)
