import logging
from logging.handlers import RotatingFileHandler

from flasgger import Swagger
from flask import Flask, request
from os import sys, path

from flask.json import jsonify

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.wss.wss import Wss

app = Flask(__name__)
Swagger(app)


@app.route('/api/hello', methods=['GET'])
def hello_world():  # TODO delete route
    if request.method == 'GET':
        try:
            logger.info('This is a info message!')
            logger.debug('This is a debug message!')
            logger.error('This is a error message!')
            logger.warning('This is a warning message!')
            return jsonify('Hello, World!', 200)

        except Exception as e:
            logger.error(e)
            raise e


@app.route('/api/wss', methods=['POST'])
def wss_configuration():
    """
    WaveShaper configuration
    ---
    post:
    description: |
        Wss configuration # TODO
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: name
      in: body
      type: string
      description: # TODO
    - name: configfile
      in: body
      type: string
      description: # TODO
    responses:
        200:
            description: "Successful operation"
        405:
            description: "Invalid input"
    """
    if request.method == 'POST':
        params = request.json
        if params is not None:
            name = params['name']
            configfile = params['configfile']
            lambda0 = params['lambda0']
            attenuation = params['att']
            phase = params['phase']
            bandwidth = params['bw']
            logger.debug("WaveShaper configuration started")
            try:
                Wss.configuration(name, configfile, lambda0, attenuation, phase, bandwidth)
                return jsonify("WaveShaper was successfully configured", 200)

            except Exception as e:
                logger.error(e)
                raise e
    else:
        raise ValueError('The parameters sended by the agent are not correct.')


if __name__ == '__main__':
    # File Handler
    # fileHandler = RotatingFileHandler('server/server.log', maxBytes=10000000, backupCount=5)
    fileHandler = RotatingFileHandler('server.log', maxBytes=10000000, backupCount=5)
    # Stream Handler
    streamHandler = logging.StreamHandler()
    # Create a Formatter for formatting the logs messages
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(filename)s: %(message)s")
    # TODO Add formatter
    # Add the Formatter to the Handler
    # fileHandler.setFormatter(formatter)
    # streamHandler.setFormatter(formatter)
    # Create the Logger
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.DEBUG)
    # Add Handlers to the Logger
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=False)