import pyangbind.lib.pybindJSON as pybindJSON

from flask import Flask, request
from binding import sliceable_transceiver_sdm

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"

app = Flask(__name__)

model = sliceable_transceiver_sdm()
new_slice = model.transceiver.slice.add("1")

@app.route('/api/transceiver', methods=['GET'])
def read():
	# return pybindJSON.dumps(new_slice)
	return pybindJSON.dumps(model, mode='ietf')

@app.route('/api/slice/1', methods=['POST'])
def create():
	payload = request.json
	new_slice.optical_channel.add(payload['id'])
	return "Created: {} \n".format(payload)

@app.route('/api/slice/1', methods=['PUT'])
def update():
	payload = request.json
	new_slice.optical_channel.set_opticalchannelid = [payload['id']]
	return "Updated: {} \n".format(payload)

app.run(host='10.1.7.64', port=5000)
