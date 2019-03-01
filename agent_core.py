"""This is the Agent Core module.
"""
import logging

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser
from rest_api import RestApi

logging.basicConfig(filename="agent.log", level=logging.DEBUG)


class AgentCore:
    """
    This is the class for Agent Core module.

    :ivar str ip_laser: IP address of Laser
    :ivar str addr_laser: GPIB address of Laser
    :ivar float power_laser: Power of Laser in dBm
    :ivar str ip_rest_server:
    :var int speed_of_light: Speed of light in m/s
    """
    ip_laser = '10.1.1.7'
    addr_laser = '11'
    power_laser = 14.5
    ip_rest_server = '10.1.1.10'
    speed_of_light = 299792458

    def __init__(self):
        """
        The constructor for the Agent Core class.
        """
        # Laser parameters
        self.ip_laser = AgentCore.ip_laser
        self.addr_laser = AgentCore.addr_laser
        self.power_laser = AgentCore.power_laser

        # DAC/OSC parameters
        self.ip_rest_server = AgentCore.ip_rest_server

        # REST API
        self.api = RestApi(self.ip_rest_server)

    def startup(self, id, mode, NCF, bps, pps, equalization):
        """

        :param id: identify de agent
        :type id: int
        :param mode: identify the scenario. 1 for BLUESPACE and 2 for METRO.
        :type mode: int
        :param NCF: # TODO send from netconf server
        :param NCF: # TODO
        :param bps: # TODO send from netconf server
        :type bps: # TODO
        :param pps: # TODO send from netconf server
        :type pps: # TODO
        :param equalization: # TODO send from netconf server
        :type equalization: # TODO
        """
        if id == 1:
            if mode == 1:
                # Laser startup
                lambda0 = (AgentCore.speed_of_light / (NCF * 1e6)) * 1e9  # calculate lambda0
                Laser.configuration(self.ip_laser, self.addr_laser, 2, lambda0, self.power_laser)

                # DAC/OSC startup
                params_dac_osc = [{'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bps, 'En': pps, 'eq': equalization},
                                  {'id': 2, 'dac_out': 2, 'osc_in': 1, 'bn': bps, 'En': pps, 'eq': equalization}]

                self.api.DACOSCConfiguration(params_dac_osc)

            elif mode == 2:
                pass

        elif id == 2:
            if mode == 1:
                # Laser startup
                lambda0 = (AgentCore.speed_of_light / (NCF * 1e6)) * 1e9  # calculate lambda0
                Laser.configuration(self.ip_laser, self.addr_laser, 2, lambda0, self.power_laser)

                # DAC/OSC startup
                # TODO extract
                params_dac_osc = [{'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bps, 'En': pps, 'eq': equalization},
                                  {'id': 2, 'dac_out': 2, 'osc_in': 1, 'bn': bps, 'En': pps, 'eq': equalization}]

                self.api.DACOSCConfiguration(params_dac_osc)

            elif mode == 2:
                pass
