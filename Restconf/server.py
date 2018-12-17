import subprocess

from flask import Flask, request

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

app = Flask('server')


@app.route('/api/config', methods=['POST'])
def startup_config():
    process_name = request.args.keys()
    try:
        subprocess.call(process_name[0])
        return "Started configuration: {} \n".format(process_name)

    except OSError as error:
        return "ERROR: {} \n".format(error)


@app.route('/api/monitor', methods=['POST'])
def startup_monitor():
    process_name = request.args.keys()
    try:
        subprocess.call(process_name[0])
        return "Started monitoring: {} \n".format(process_name)

    except OSError as error:
        return "ERROR: {} \n".format(error)


@app.route('/api/matlab', methods=['POST'])
def startup_matlab():
    process_name = request.args.keys()
    try:
        subprocess.call(process_name[0])
        return "Executed matlab: {} \n".format(process_name)

    except OSError as error:
        return "ERROR: {} \n".format(error)

if __name__ == '__main__':
    app.run(host='10.1.1.10', port=5000, debug=True)
