import ast

import numpy as np
from six.moves import configparser
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.dac.dac import DAC


def get_config(id, filename):
    """
    Get all attributes from a configuration file specified by filename
    :param id: identify configuration scenario
    :type id: int
    :param filename: configuration filename
    :type filename: str
    """
    config = configparser.RawConfigParser()
    config.read(filename)

    print("laser section")
    print(config.get('laser', 'ip'))
    print(config.get('laser', 'addr'))
    print(config.get('laser', 'channel'))
    print(config.get('laser', 'power'))

    print("dac_osc section")
    ldo = ast.literal_eval(config.get('dac_osc', 'logical_associations'))
    print(list(ldo))

    print("rest_api section")
    print(config.get('rest_api', 'ip'))

    if id == 2:
        print("oa section")
        print(config.get('oa', 'ip'))
        print(config.get('oa', 'addr'))
        print(config.get('oa', 'mode'))
        print(config.get('oa', 'power'))

        print("wss section")
        d = ast.literal_eval(config.get('wss', 'operations'))
        print(dict(d))


if __name__ == '__main__':
    files = ["blue_bvt1.cfg", "blue_bvt2.cfg", "metro_bvt1.cfg", "metro_bvt2.cfg"]
    get_config(2, files[2])

    bn = np.array(np.ones(DAC.Ncarriers) * DAC.bps).tolist()
    En = np.array(np.ones(DAC.Ncarriers)).tolist()
    eq = "MMSE"
