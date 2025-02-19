import argparse
import logging
from logging.handlers import RotatingFileHandler
from os import sys, path

from flasgger import Swagger
from flask import Flask, request
from flask.json import jsonify

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from agent_core import AgentCore

app = Flask(__name__)
Swagger(app)

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)


def startup(*margs):
    """
    Define BVT-Agent.

    :param margs: id of bvt-agent
    :type margs: int
    :return: AgentCore specified for bvt-agent defined
    :rtype: AgentCore
    """
    parser = argparse.ArgumentParser("OPENCONFIG Server Startup")
    parser.add_argument('-id', type=int, help='BVT-agent id')

    args = parser.parse_args(*margs)
    agent = AgentCore(args.id)
    return agent


ac = startup()


@app.route('/api/hello', methods=['GET'])
def hello_world():
    """
    Test configuration
    ---
    post:
    description: Test configuration
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: name
      in: body
      type: string
      description: Identifies the name of tester
    responses:
        200:
            description: "Successful operation"
        405:
            description: "Invalid input"
    """
    if request.method == 'GET':
        data = request.json
        if data is not None:
            try:
                return jsonify("Hello World %s!" % str(data), 200)

            except Exception as e:
                logger.error(e)
                return jsonify('ERROR: %s' % e, 405)
        else:
            return jsonify('The parameters sended by the agent are not correct.', 405)


def define_logger():
    """
    Create, formatter and add Handlers (RotatingFileHandler and StreamHandler) to the logger.
    """
    fileHandler = RotatingFileHandler('server.log', maxBytes=10000000, backupCount=5)  # File Handler
    streamHandler = logging.StreamHandler()  # Stream Handler
    # Create a Formatter for formatting the logs messages
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(filename)s: %(message)s")
    # Add the Formatter to the Handlers
    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)
    # Add Handlers to the logger
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)


if __name__ == '__main__':
    define_logger()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)
