from flask import Flask
import pyangbind.lib.pybindJSON as pybindJSON
from server.binding import sliceable_transceiver_sdm

app = Flask(__name__)


@app.route('/hello')
def helloWorldHandler():
    return 'Hello World from Flask!'

@app.route('/transceiver')
def hehe():
    model = sliceable_transceiver_sdm()
    model.transceiver.slice.sliceid = 1
    print(model.transceiver.slice["1"])
    return model


app.run(host='0.0.0.0', port=8090)