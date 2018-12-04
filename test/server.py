import pyangbind.lib.pybindJSON as pybindJSON

from flask import Flask, request
from binding import sliceable_transceiver_sdm

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"

app = Flask(__name__)

model = sliceable_transceiver_sdm()

@app.route('/api/transceiver', methods=['GET'])
def get_transceiver():
	return pybindJSON.dumps(model, mode='ietf')

@app.route('/api/transceiver/slice', methods=['POST'])
def create_slice():
	payload = request.json
	model.transceiver.slice.add(payload['sliceid'])
	return "Created: {} \n".format(payload)

@app.route('/api/transceiver/slice', methods=['DELETE'])
def delete_slice():
	payload = request.json
	model.transceiver.slice.delete(payload['sliceid'])
	return "Deleted: {} \n".format(payload)

# @app.route('/api/transceiver/slice/<int:_id>', methods=['POST'])
# def create_opticalchannel(_id):
# 	payload = request.json
# 	for sliceid in model.transceiver.slice.iteritems():
# 		# if _id == sliceid:
# 		sliceid.optical_channel.add(payload['opticalchannelid'])
# 	return "Created: {} \n".format(payload)

app.run(host='10.1.16.53', port=5000)
