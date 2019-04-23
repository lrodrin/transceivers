"""This is the Agent Core module.
"""
import logging
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser
from lib.amp.amp import Amplifier
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
        self.wss_operations = wss_operations

        # DAC/OSC parameters
        self.logical_associations = list(logical_associations)

        # REST API
        self.ip_rest_server = ip_rest_server
        self.api = RestApi(self.ip_rest_server)

    def laser_setup(self, freq):
        """
        Laser setup.

            - Calculate lambda0 from frequency specified by freq.
            - Set wavelength of the Laser.
            - Set the power of the Laser.

        :param freq: frequency
        :param freq: float
        """
        try:
            lambda0 = (299792.458 / (freq * 1e6)) * 1e9
            Laser.configuration(self.ip_laser, self.addr_laser, self.channel_laser, lambda0, self.power_laser)

        except Exception as e:
            logger.error("Laser setup not finished, error: %s" % e)
            raise e

    def dac_setup(self, bn, En, eq):
        """
        DAC/OSC setup.
        Performs DSP to modulate/demodulate an OFDM signal.

            - DAC setup creates an OFDM signal and uploads it to Leia DAC.
            - OSC setup adquires the transmitted OFDM signal and perform DSP to retrieve the original datastream.

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
            logger.error("DAC/OSC setup not finished, error: %s" % e)
            raise e

    def amplifier_setup(self):
        """
        Amplifier setup.
        Set mode and power of the Amplifier.
        """
        try:
            Amplifier.configuration(self.ip_amplifier, self.addr_amplifier, self.mode_amplifier, self.power_amplifier)

        except Exception as e:
            logger.error("Amplifier setup not finished, error: %s" % e)
            raise e

    def wss_setup(self):
        """
        WaveShaper setup.
        Sets the configuration file, central wavelength, bandwidth and attenuation/phase per port of a WaveShaper.
        """
        try:
            result = self.api.wSSConfiguration(self.wss_operations)
            return result

        except Exception as e:
            logger.error("WSS setup not finished, error: %s" % e)
            raise e

    def setup(self, freq, bn, En, eq):
        """
        Laser and DAC/OSC setup by setting frequency, constellation and equalization.

            - Laser setup.
            - DAC/OSC setup.

        :param freq: frequency
        :param freq: float
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
            self.laser_setup(freq)

            # DAC/OSC setup
            result = self.dac_setup(bn, En, eq)
            logger.debug("DAC setup finished with SNR = {} and average BER = {}".format(result[0], result[1]))
            return result

        except Exception as e:
            logger.error("Configuration of a DRoF failed, error: %s" % e)
            raise e

    def disable_laser(self):
        """
        Disable Laser.
        """
        yenista = Laser(self.ip_laser, self.addr_laser)
        yenista.enable(self.channel_laser, False)
        logger.debug("Laser {} on channel {} disabled".format(self.ip_laser, self.channel_laser))

    def disable_amplifier(self):
        """
        Disable Amplifier.
        """
        manlight = Amplifier(self.ip_amplifier, self.addr_amplifier)
        manlight.enable(False)
        logger.debug("Amplifier %s disabled" % self.ip_amplifier)

    def disconnect(self):
        """
        Disable Laser and remove the logical associations between DAC and OSC.
        """
        try:
            self.disable_laser()

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
