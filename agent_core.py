"""This is the Agent Core module.
"""
import logging
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser
from rest_api import RestApi

logger = logging.getLogger("AGENT_CORE")
logger.addHandler(logging.NullHandler())


class AgentCore:
    """
    This is the class for the Agent Core module.
    """

    def __init__(self, ip_laser, addr_laser, channel_laser, power_laser, ip_amplifier, addr_amplifier, mode_amplifier,
                 power_amplifier, wss_operations, logical_associations, ip_rest_server):
        """
        The constructor for the Agent Core class.

        :param ip_laser: IP address of GPIB-ETHERNET of the Laser
        :type ip_laser: str
        :param addr_laser: GPIB address of the Laser
        :param channel_laser: channel of the Laser
        :type channel_laser: int
        :param power_laser: power of the Laser in dBm
        :type power_laser: float
        :param ip_amplifier: IP address of GPIB-ETHERNET of the Amplifier
        :type ip_amplifier: str
        :param addr_amplifier: GPIB address of the Amplifier
        :type addr_amplifier: str
        :param mode_amplifier: mode of the Amplifier
        :type mode_amplifier: str
        :param power_amplifier: power of the Amplifier in dBm
        :type power_amplifier: float
        :param wss_operations: id of WaveShaper and list of operations to be configured on the WaveShaper
        :type wss_operations: dict
        :param logical_associations: a transmission between DAC and OSC
        :type logical_associations: list
        :param ip_rest_server: IP address of GPIB-ETHERNET of the DAC/OSC REST Server
        :type ip_rest_server: str
        """
        # Laser parameters
        self.ip_laser = str(ip_laser)
        self.addr_laser = str(addr_laser)
        self.channel_laser = int(channel_laser)
        self.power_laser = float(power_laser)

        # OA parameters
        self.ip_amplifier = ip_amplifier
        self.addr_amplifier = addr_amplifier
        self.mode_amplifier = mode_amplifier
        self.power_amplifier = power_amplifier

        # WSS parameters
        if wss_operations is not None:
            self.wss_operations = dict(wss_operations)
        else:
            self.wss_operations = wss_operations

        # DAC/OSC parameters
        self.logical_associations = list(logical_associations)

        # REST API
        self.ip_rest_server = ip_rest_server
        self.api = RestApi(self.ip_rest_server)

    def laser_setup(self, NCF):
        """
        Laser setup.

            - Calculate lambda0 from NCF specified by freq.
            - Set wavelength of the Laser.
            - Set the power of the Laser.

        :param NCF: nominal central frequency
        :param NCF: float
        """
        try:
            lambda0 = (299792.458 / (NCF * 1e6)) * 1e9
            Laser.configuration(self.ip_laser, self.addr_laser, self.channel_laser, lambda0, self.power_laser)

        except Exception as e:
            logger.error("Laser setup not finished, error: %s" % e)
            raise e

    def dac_setup(self, bn, En, eq):
        """
        DAC setup.

            - Add bits per symbol, power per symbol and equalization parameters to logical associations.
            - Generate waveform and load to DAC channel.

        :param bn: bits per symbol
        :type bn: int array of 512 positions
        :param En: power per symbol
        :type En: float array of 512 positions
        :param eq: equalization
        :type eq: str
        :return: estimated SNR per subcarrier and BER
        :rtype: list
        """
        try:
            for i in range(len(self.logical_associations)):
                self.logical_associations[i]['bn'] = bn
                self.logical_associations[i]['En'] = En
                self.logical_associations[i]['eq'] = eq

            result = self.api.dacOscConfiguration(self.logical_associations)
            return result

        except Exception as e:
            logger.error("DAC setup not finished, error: %s" % e)
            raise e

    def setup(self, NCF, bn, En, eq):  # CALLED FROM netconf_server.py
        """
        Configuration of a DRoF by setting nominal central frequency, constellation and equalization.

            - Laser setup.
            - DAC setup.

        :param NCF: nominal central frequency
        :param NCF: float
        :param bn: bits per symbol
        :type bn: int array of 512 positions
        :param En: power per symbol
        :type En: float array of 512 positions
        :param eq: equalization
        :type eq: str
        :return: estimated SNR per subcarrier and BER
        :rtype: list
        """
        try:
            # Laser setup
            self.laser_setup(NCF)

            # DAC/OSC setup
            result = self.dac_setup(bn, En, eq)
            logger.debug("DAC setup finished with SNR = {} and BER = {}".format(result[0], result[1]))
            return result

        except Exception as e:
            logger.error("Configuration of a DRoF failed, error: %s" % e)
            raise e

    def disconnect(self):  # CALLED FROM netconf_server.py
        """
        Disable Laser and remove the logical associations between DAC and OSC.
        """
        try:
            yenista = Laser(self.ip_laser, self.addr_laser)
            yenista.enable(self.channel_laser, False)
            logger.debug("Laser {} on channel {} disabled".format(self.ip_laser, self.channel_laser))

            # remove the logical associations
            for i in range(len(self.logical_associations)):
                assoc_id = self.logical_associations[i]['id']
                dac_out = self.logical_associations[i]['dac_out']
                osc_in = self.logical_associations[i]['osc_in']
                self.api.deleteDACOSCOperationsById(assoc_id)
                logger.debug(
                    "Logical association {} on DAC {} and OSC {} removed".format(assoc_id, dac_out, osc_in))

        except Exception as e:
            logger.error(e)
            raise e

    # def metroSetup(self, och, freq, power, mode):  # CALLED FROM openconfig_server.py
    #     """
    #     Configuration of an Optical Channel by setting frequency, power and mode.
    #
    #         - WSS setup.
    #         - Amplifier setup.
    #         - Laser setup.
    #         - DAC/OSC setup.
    #
    #     :param och: id to identify the optical channel
    #     :type och: str
    #     :param freq: frequency of the optical channel expressed in MHz. 193.3e6 (1550.99 nm) for channel 1 or 193.4e6
    #     (1550.12 nm) for channel 2
    #     :type freq: float
    #     :param power: target output power level of the optical channel expressed in increments of 0.01 dBm.
    #     3.20 dBm for uniform loading or 0.4 dBm for loading
    #     :type power: float
    #     :param mode: vendor-specific mode identifier for identify the operational mode of the optical channel. SD-FEC
    #     or HD-FEC
    #     :type mode: str
    #     """
    #     try:
    #         # WSS setup
    #         result = self.api.wSSConfiguration(self.wss_operations)
    #         logging.debug(result)
    #
    #         # OA setup
    #         result = Amplifier.configuration(self.ip_amplifier, self.addr_amplifier, self.mode_amplifier,
    #                                          self.power_amplifier)
    #         logger.debug(
    #             "Amplifier parameters - status: {}, mode: {}, power: {}".format(result[0], result[1], result[2]))
    #
    #         # Laser and DAC/OSC setup
    #
    #
    #     except Exception as e:
    #         logger.error(e)
    #         raise e
    #
    # @staticmethod
    # def channelAssignment(client, och):  # CALLED FROM openconfig_server.py
    #     """
    #     Client assignation to an Optical Channel.
    #
    #     :param client: id to identify the client
    #     :type client: str
    #     :param och: id to identify the optical channel
    #     :type och: str
    #     :return: the client and the optical channel assigned
    #     :rtype: str
    #     """
    #     return "Client {} assigned to the Optical Channel {}".format(client, och)
    #
    # def metroDisconnect(self):  # CALLED FROM openconfig_server.py
    #     """
    #     Disable Laser and Amplifier.
    #     Remove the logical associations between DAC and OSC and remove the operations configured to WSS.
    #     """
    #     try:
    #         # disable laser and remove the logical associations
    #         self.disconnect()
    #
    #         # disable amplifier
    #         manlight = Amplifier(self.ip_amplifier, self.addr_amplifier)
    #         manlight.enable(False)
    #         logger.debug("Amplifier %s disabled" % self.ip_amplifier)
    #
    #         # remove the operations
    #         wss_id = self.wss_operations['wss_id']
    #         self.api.deleteWSSOperationsById(wss_id)
    #         logger.debug("Operations on WaveShaper %s removed" % wss_id)
    #
    #     except Exception as e:
    #         logger.error(e)
    #         raise e
