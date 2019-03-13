"""This is the Agent Core module.
"""
import logging
from os import sys, path

import numpy as np

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser
from lib.amp.amp import Amplifier
from lib.dac.dac import DAC
from rest_api import RestApi

logger = logging.getLogger("AGENT_CORE")
logger.addHandler(logging.NullHandler())


class AgentCore:
    """
    This is the class for Agent Core module.

    :ivar str ip_laser: IP address of Laser
    :ivar str addr_laser: GPIB address of Laser
    :ivar str addr_amplifier: GPIB address of Amplifier
    :ivar str mode_amplifier: Mode of Amplifier
    :ivar float power_amplifier: Power of Amplifier in dBm
    :ivar str ip_rest_server: IP address of REST Server
    :var int speed_of_light: Speed of light in m/s
    """
    ip_laser = '10.1.1.7'
    addr_laser = '11'
    addr_amplifier = '3'
    mode_amplifier = "APC"
    power_amplifier = 0
    ip_rest_server = '10.1.1.10'
    speed_of_light = 299792458

    def __init__(self, id):
        """
        The constructor for the Agent Core class.

        :param id: identify the bvt-agent. 1 for bvt-agent 1 and 2 for bvt-agent 2.
        :type id: int
        """
        self.id = id

        # Laser parameters
        self.ip_laser = AgentCore.ip_laser
        self.addr_laser = AgentCore.addr_laser

        # Amplifier parameters
        self.addr_amplifier = AgentCore.addr_amplifier
        self.mode_amplifier = AgentCore.mode_amplifier
        self.power_amplifier = AgentCore.power_amplifier

        # REST API
        self.ip_rest_server = AgentCore.ip_rest_server
        self.api = RestApi(self.ip_rest_server)

    def bvtConfiguration(self, NCF, bps, pps, equalization):  # CALLED FROM netconf_server.py
        """
        BVT-Agent Configuration.

            - Laser configuration.
            - DAC and OSC configuration.

        :param NCF: nominal central frequency
        :param NCF: int
        :param bps: bits per symbol
        :type bps: float array of 512 positions
        :param pps: power per symbol
        :type pps: float array of 512 positions
        :param equalization: equalization
        :type equalization: str
        """
        lambda0 = (AgentCore.speed_of_light / (NCF * 1e6)) * 1e9  # calculate lambda0
        power_laser = 14.5
        logical_associations = [
            {'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bps, 'En': pps, 'eq': equalization},
            {'id': 2, 'dac_out': 2, 'osc_in': 1, 'bn': bps, 'En': pps, 'eq': equalization}]

        if self.id == 1:
            # Laser1 startup
            channel_laser = 2
            laser_conf = Laser.configuration(self.ip_laser, self.addr_laser, channel_laser, lambda0, power_laser)
            print(laser_conf)

            # DAC/OSC startup
            osc_conf = self.api.DACOSCConfiguration(logical_associations[0])
            print(osc_conf)

        elif self.id == 2:
            # Laser2 startup
            channel_laser = 3
            laser_conf = Laser.configuration(self.ip_laser, self.addr_laser, channel_laser, lambda0, power_laser)
            print(laser_conf)

            # DAC/OSC startup
            osc_conf = self.api.DACOSCConfiguration(logical_associations[1])
            print(osc_conf)

    def optical_channel_configuration(self, och, freq, power, mode):  # CALLED FROM openconfig_server.py
        """
        Configuration of an Optical Channel by setting frequency, power and mode.

            - Run WSS configuration.
            - Run Amplifier configuration.
            - Run Laser configuration.
            - Run DAC/OSC configuration.

        :param och: id to identify the optical channel
        :type och: str
        :param freq: frequency of the optical channel expressed in MHz. 193.3e6 (1550.99 nm) for channel 1 or 193.4e6
        (1550.12 nm) for channel 2
        :type freq: int
        :param power: target output power level of the optical channel expressed in increments of 0.01 dBm.
        3.20 dBm for uniform loading or 0.4 dBm for loading
        :type power: float
        :param mode: vendor-specific mode identifier for identify the operational mode of the optical channel. SD-FEC
        or HD-FEC
        :type mode: str
        """
        bn1 = np.array(np.ones(DAC.Ncarriers) * DAC.bps).tolist()
        bn2 = np.array(np.ones(DAC.Ncarriers)).tolist()
        En1 = np.array(np.ones(DAC.Ncarriers)).tolist()
        En2 = np.round(np.array(np.ones(DAC.Ncarriers) / np.sqrt(2)), 3).tolist()
        eq1 = eq2 = "MMSE"
        logical_associations = [
            {'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bn1, 'En': En1, 'eq': eq1},
            {'id': 2, 'dac_out': 2, 'osc_in': 1, 'bn': bn2, 'En': En2, 'eq': eq2}]

        if self.id == 1:
            # WSS1 startup
            params_wss = {'wss_id': 1, 'operation': [
                {'port_in': 1, 'port_out': 1, 'lambda0': 1550.52, 'att': 0.0, 'phase': 0.0, 'bw': 112.5}]}
            wss_conf = self.api.WSSConfiguration(params_wss)
            logging.debug(wss_conf)
            print(wss_conf)

            # OA1 startup
            ip_amplifier = '10.1.1.16'
            oa_conf = Amplifier.configuration(ip_amplifier, self.addr_amplifier, self.mode_amplifier,
                                              self.power_amplifier)
            logging.debug(oa_conf)
            print(oa_conf)

            # Laser1 startup
            lambda0 = (AgentCore.speed_of_light / (freq * 1e6)) * 1e9  # calculate lambda0
            channel_laser = 2
            power_laser = power + 9  # considering the losses of the modulation MZM module
            laser_conf = Laser.configuration(self.ip_laser, self.addr_laser, channel_laser, lambda0, power_laser)
            logging.debug(laser_conf)
            print(laser_conf)

            # DAC/OSC startup
            osc_conf = self.api.DACOSCConfiguration(logical_associations[0])
            print(osc_conf)

        elif self.id == 2:
            # WSS2 startup
            params_wss = {'wss_id': 2, 'operation': [
        {'port_in': 2, 'port_out': 1, 'lambda0': 1550.88, 'att': 0.0, 'phase': 0.0, 'bw': 50.0},
        {'port_in': 3, 'port_out': 1, 'lambda0': 1550.3, 'att': 0.0, 'phase': 0.0, 'bw': 50.0}]}
            wss_conf = self.api.WSSConfiguration(params_wss)
            logging.debug(wss_conf)
            print(wss_conf)

            # OA2 startup
            ip_amplifier = '10.1.1.15'
            oa_conf = Amplifier.configuration(ip_amplifier, self.addr_amplifier, self.mode_amplifier,
                                              self.power_amplifier)
            logging.debug(oa_conf)
            print(oa_conf)

            # Laser2 startup
            lambda0 = (AgentCore.speed_of_light / (freq * 1e6)) * 1e9  # calculate lambda0
            channel_laser = 3
            power_laser = power + 9  # considering the losses of the modulation MZM module
            laser_conf = Laser.configuration(self.ip_laser, self.addr_laser, channel_laser, lambda0, power_laser)
            logging.debug(laser_conf)
            print(laser_conf)

            # DAC/OSC startup
            osc_conf = self.api.DACOSCConfiguration(logical_associations[1])
            print(osc_conf)

    @staticmethod
    def local_channel_assignment(client, och):
        """
        Client assignation to an Optical Channel.

        :param client: id to identify the client
        :type client: str
        :param och: id to identify the optical channel
        :type och: str
        :return: the client and the optical channel assigned
        :rtype: str
        """
        return "Client {} assigned to the Optical Channel {}".format(client, och)
