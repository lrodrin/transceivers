"""This is the Agent Core module.
"""
import logging

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser
from lib.amp.amp import Amplifier
from rest_api import RestApi

logging.basicConfig(filename="agent.log", level=logging.DEBUG)


class AgentCore:
    """
    This is the class for Agent Core module.

    :ivar str ip_laser: IP address of Laser
    :ivar str addr_laser: GPIB address of Laser
    :ivar float power_laser: Power of Laser in dBm

    :ivar str ip_amplifier: IP address of Amplifier
    :ivar str addr_amplifier: GPIB address of Amplifier
    :ivar str mode_amplifier: Mode of Amplifier
    :ivar float power_amplifier: Power of Amplifier in dBm

    :ivar str ip_rest_server:

    :var int speed_of_light: Speed of light in m/s
    """
    ip_laser = '10.1.1.7'
    addr_laser = '11'
    power_laser = 14.5

    addr_amplifier = '3'
    mode_amplifier = "APC"
    power_amplifier = 0

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

        # Amplifier parameters
        self.ip_amplifier = str()
        self.addr_amplifier = AgentCore.addr_amplifier
        self.mode_amplifier = AgentCore.mode_amplifier
        power_amplifier = AgentCore.power_amplifier

        # REST API
        self.ip_rest_server = AgentCore.ip_rest_server
        self.api = RestApi(self.ip_rest_server)

    def bvtConfiguration(self, id, mode, NCF, bps, pps, equalization):
        """

        :param id: identify the bvt-agent
        :type id: int
        :param mode: identify the configuration scenario. 1 for BLUESPACE and 2 for METRO
        :type mode: int
        :param NCF: nominal central frequency
        :param NCF: int
        :param bps: bits per symbol
        :type bps: float array of 512 positions
        :param pps: power per symbol
        :type pps: float array of 512 positions
        :param equalization: equalization
        :type equalization: str
        """
        if id == 1:
            if mode == 1:
                # Laser1 startup
                lambda0 = (AgentCore.speed_of_light / (NCF * 1e6)) * 1e9  # calculate lambda0
                Laser.configuration(self.ip_laser, self.addr_laser, 2, lambda0, self.power_laser)

                # DAC/OSC startup
                params_dac_osc = [{'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bps, 'En': pps, 'eq': equalization}]
                self.api.DACOSCConfiguration(params_dac_osc)

            elif mode == 2:
                # WSS1 startup
                params_wss = {'wss_id': 1, 'operation': [
                    {'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]}
                self.api.WSSConfiguration(params_wss)

                # OA1 startup
                self.ip_amplifier = '10.1.1.16'
                Amplifier.configuration(self.ip_amplifier, self.addr_amplifier, self.mode_amplifier, self.power_amplifier)

                # Laser1 startup
                lambda0 = (AgentCore.speed_of_light / (NCF * 1e6)) * 1e9  # calculate lambda0
                Laser.configuration(self.ip_laser, self.addr_laser, 2, lambda0, self.power_laser)

                # DAC/OSC startup
                params_dac_osc = [{'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bps, 'En': pps, 'eq': equalization}]
                self.api.DACOSCConfiguration(params_dac_osc)

        elif id == 2:
            if mode == 1:
                # Laser startup
                lambda0 = (AgentCore.speed_of_light / (NCF * 1e6)) * 1e9  # calculate lambda0
                Laser.configuration(self.ip_laser, self.addr_laser, 3, lambda0, self.power_laser)

                # DAC/OSC startup
                params_dac_osc = [{'id': 2, 'dac_out': 2, 'osc_in': 1, 'bn': bps, 'En': pps, 'eq': equalization}]
                self.api.DACOSCConfiguration(params_dac_osc)

            elif mode == 2:
                # WSS2 startup
                params_wss = {'wss_id': 1, 'operation': [
                    {'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]}
                self.api.WSSConfiguration(params_wss)

                # OA2 startup
                self.ip_amplifier = '10.1.1.15'
                Amplifier.configuration(self.ip_amplifier, self.addr_amplifier, self.mode_amplifier,
                                        self.power_amplifier)

                # Laser2 startup
                lambda0 = (AgentCore.speed_of_light / (NCF * 1e6)) * 1e9  # calculate lambda0
                Laser.configuration(self.ip_laser, self.addr_laser, 3, lambda0, self.power_laser)

                # DAC/OSC startup
                params_dac_osc = [{'id': 2, 'dac_out': 2, 'osc_in': 1, 'bn': bps, 'En': pps, 'eq': equalization}]
                self.api.DACOSCConfiguration(params_dac_osc)
