import ast
import logging
import os
from os import sys, path

import numpy as np
from six.moves import configparser

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC
from agent_core import AgentCore

logging.basicConfig(level=logging.DEBUG)


def createAgent(fd, fi):
    """
    Creates an Agent Core with the configuration file parameters specified by fi.

    :param fd: directory that contains Agent Core configuration conf_files
    :type fd: str
    :param fi: configuration file
    :type fi: str
    :return: a new Agent Core
    :rtype: AgentCore
    """
    config = configparser.RawConfigParser()
    config.read(fd + fi)
    if fi.startswith("b"):
        ac = AgentCore(
            config.get('laser', 'ip'),
            config.get('laser', 'addr'),
            config.get('laser', 'channel'),
            config.get('laser', 'power'),
            None,
            None,
            None,
            None,
            None,
            ast.literal_eval(config.get('dac_osc', 'logical_associations')),
            config.get('rest_api', 'ip')
        )
    else:
        ac = AgentCore(
            config.get('laser', 'ip'),
            config.get('laser', 'addr'),
            config.get('laser', 'channel'),
            config.get('laser', 'power'),
            config.get('oa', 'ip'),
            config.get('oa', 'addr'),
            config.get('oa', 'mode'),
            config.get('oa', 'power'),
            ast.literal_eval(config.get('dac_osc', 'logical_associations')),
            ast.literal_eval(config.get('wss', 'operations')),
            config.get('rest_api', 'ip')
        )
    return ac


if __name__ == '__main__':
    abs_path = os.path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    b_folder = os.path.join(abs_path, "bluespace/config/")
    m_folder = os.path.join(abs_path, "metro-haul/config/")
    # print(b_folder, m_folder)
    conf_files = ["blue_bvt1.cfg", "blue_bvt2.cfg", "metro_bvt1.cfg", "metro_bvt2.cfg"]

    print("Testing AGENT CORE")
    # for file in conf_files:
    #     print("AGENT CORE created from %s" % file)
    #     if file.startswith("b"):
    #         f = b_folder
    #     else:
    #         f = m_folder
    #
    #     ac = createAgent(f, file)
    #     print(ac.ip_amplifier, ac.power_amplifier, ac.channel_laser, ac.losses_laser)

    ac = createAgent(m_folder, "metro_bvt1.cfg")
    print(ac.ip_amplifier, ac.power_amplifier, ac.channel_laser, ac.losses_laser)

    freq = 193.4e6
    bn = np.array(np.ones(DAC.Ncarriers) * DAC.bps, dtype=int).tolist()
    En = np.array(np.ones(DAC.Ncarriers)).tolist()
    eq = "MMSE"
    power = -1.3
    mode = "HD-FEC"
    client = "c1"
    och = "och1"

    # ac.laser_setup(freq)
    # print(ac.dac_setup(bn, En, eq))
    # ac.disconnect()

    ac.amplifier_setup()
    print(ac.wss_setup())
