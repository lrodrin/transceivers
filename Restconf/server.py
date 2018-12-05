import pyangbind.lib.pybindJSON as pybindJSON
import subprocess

from flask import Flask, request
from bindingTransceiver import sliceable_transceiver_sdm

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

app = Flask('api')

model = sliceable_transceiver_sdm()


@app.route('/api/transceiver', methods=['GET'])
def get_transceiver():
    return pybindJSON.dumps(model)


@app.route('/api/transceiver/slice', methods=['POST'])
def create_slice():
    payload = request.json
    sliceid = payload['sliceid']
    opticalchannelid = payload['opticalchannelid']
    coreid = payload['coreid']
    model.transceiver.slice.add(sliceid)
    model.transceiver.slice[sliceid].optical_channel.add(opticalchannelid)
    model.transceiver.slice[sliceid].optical_channel[opticalchannelid].coreid = coreid
    return "Created: {} \n".format(payload)


@app.route('/api/transceiver/slice', methods=['DELETE'])
def delete_slice():
    payload = request.json
    model.transceiver.slice.delete(payload['sliceid'])
    return "Deleted: {} \n".format(payload)


@app.route('/api/transceiver/slice/<int:_id>', methods=['POST'])
def create_opticalchannel(_id):
    payload = request.json
    for sliceid in model.transceiver.slice.iteritems():
        # if _id == sliceid:
        sliceid.optical_channel.add(payload['opticalchannelid'])
    return "Created: {} \n".format(payload)


@app.route('/api/config', methods=['POST'])
def execute_config():
    process_name = request.args.keys()
    subprocess.call(process_name[0])
    return "Executed: {} \n".format(process_name)

@app.route('/api/monitor', methods=['POST'])
def execute_monitor():
    process_name = request.args.keys()
    subprocess.call(process_name[0])
    return "Executed: {} \n".format(process_name)


if __name__ == '__main__':
    app.run(host='10.1.16.53', port=5000, debug=True)
