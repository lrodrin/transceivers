from flask import Flask
import pyangbind.lib.pybindJSON as pybindJSON
from binding import sliceable_transceiver_sdm

app = Flask(__name__)


@app.route('/hello')
def helloWorldHandler():
    return 'Hello World from Flask!'

@app.route('/slice')
def make_json():
    model = sliceable_transceiver_sdm()
    model.transceiver.slice.add("1")
    print("Done")
    return pybindJSON.dumps(model, mode='ietf')

app.run(host='10.1.7.64', port=5000)
