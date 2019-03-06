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
    :ivar int channel_laser: Channel of Laser
    :ivar float power_laser: Power of Laser in dBm
    :ivar str ip_amplifier: IP address of Amplifier
    :ivar str addr_amplifier: GPIB address of Amplifier
    :ivar str mode_amplifier: Mode of Amplifier.
    :ivar float power_amplifier: Power of Amplifier in dBm

    :ivar str ip_rest_server: IP address of REST Server
    :ivar dict operations: Operations of WSS
    :ivar list logical_associations: Local associations between DAC and OSC

    :var int speed_of_light: Speed of light in m/s
    """
    ip_laser = '10.1.1.7'
    addr_laser = '11'
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
        self.channel_laser = int()
        self.power_laser = float()

        # Amplifier parameters
        self.ip_amplifier = str()
        self.addr_amplifier = AgentCore.addr_amplifier
        self.mode_amplifier = AgentCore.mode_amplifier
        self.power_amplifier = AgentCore.power_amplifier

        # REST API
        self.ip_rest_server = AgentCore.ip_rest_server
        self.api = RestApi(self.ip_rest_server)

        self.operations = dict()
        self.logical_associations = list()

    def bvtConfiguration(self, id, mode, NCF, bps, pps, equalization):  # CALLED FROM NETCONF or RESTCONF
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
            self.channel_laser = 2
            if mode == 1:
                # Laser1 startup
                lambda0 = (AgentCore.speed_of_light / (NCF * 1e6)) * 1e9  # calculate lambda0
                self.power_laser = 14.5
                laser_conf = Laser.configuration(self.ip_laser, self.addr_laser, self.channel_laser, lambda0, self.power_laser)
                print(laser_conf)

                # DAC/OSC startup
                logical_associations = [
                    {'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bps, 'En': pps, 'eq': equalization}]
                osc_conf = self.api.DACOSCConfiguration(logical_associations)
                print(osc_conf)

            elif mode == 2:
                self.ip_amplifier = '10.1.1.16'
                self.logical_associations = [
                    {'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bps, 'En': pps, 'eq': equalization}]
                self.operations = {'wss_id': 1, 'operation': [
                    {'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]}

        elif id == 2:
            self.channel_laser = 3
            if mode == 1:
                # Laser1 startup
                lambda0 = (AgentCore.speed_of_light / (NCF * 1e6)) * 1e9  # calculate lambda0
                self.power_laser = 14.5
                laser_conf = Laser.configuration(self.ip_laser, self.addr_laser, self.channel_laser, lambda0, self.power_laser)
                print(laser_conf)

                # DAC/OSC startup
                logical_associations = [
                    {'id': 1, 'dac_out': 2, 'osc_in': 1, 'bn': bps, 'En': pps, 'eq': equalization}]
                osc_conf = self.api.DACOSCConfiguration(logical_associations)
                print(osc_conf)

            elif mode == 2:
                self.ip_amplifier = '10.1.1.15'
                self.logical_associations = [
                    {'id': 1, 'dac_out': 2, 'osc_in': 1, 'bn': bps, 'En': pps, 'eq': equalization}]
                self.operations = {'wss_id': 2, 'operation': [
                    {'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]}

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

    def optical_channel_configuration(self, och, freq, power, mode):
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
        :return:
        :rtype:
        """
        logging.debug("Optical Channel %s configuration started" % och)
        try:
            # WSS startup
            wss_conf = self.api.WSSConfiguration(params_wss)
            logging.debug(wss_conf)
            print(wss_conf)

            # OA startup
            oa_conf = Amplifier.configuration(self.ip_amplifier, self.addr_amplifier, self.mode_amplifier,
                                              self.power_amplifier)
            logging.debug(oa_conf)
            print(oa_conf)

            # Laser startup
            lambda0 = (AgentCore.speed_of_light / (freq * 1e6)) * 1e9  # calculate lambda0
            self.power_laser = power + 9  # considering the losses of the modulation MZM module
            laser_conf = Laser.configuration(self.ip_laser, self.addr_laser, self.channel_laser, lambda0, self.power_laser)
            logging.debug(laser_conf)
            print(laser_conf)

            # DAC/OSC startup
            osc_conf = self.api.DACOSCConfiguration(params_dac_osc)
            logging.debug(osc_conf)
            print(osc_conf)

            msg = "Optical Channel %s was successfully configured" % och
            logging.debug(msg)
            return msg

        except Exception as e:
            error_msg = "Optical Channel {} wasn't successfully configured. Error: {}".format(och, e)
            logging.error(error_msg)
            raise error_msg
