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

    def __init__(self, ip_laser, addr_laser, channel_laser, power_laser, losses_laser, ip_amplifier, addr_amplifier,
                 mode_amplifier, power_amplifier, wss_operations, logical_associations, ip_rest_server):
        """
        The constructor for the Agent Core class.

        :param ip_laser: IP address of GPIB-ETHERNET of the Laser
        :type ip_laser: str
        :param addr_laser: GPIB address of the Laser
        :type addr_laser: str
        :param channel_laser: channel of the Laser
        :type channel_laser: int
        :param power_laser: power of the Laser in dBm
        :type power_laser: float
        :param losses_laser: power losses of the Laser in dBm
        :type losses_laser: float
        :param ip_amplifier: IP address of GPIB-ETHERNET of the Amplifier
        :type ip_amplifier: str
        :param addr_amplifier: GPIB address of the Amplifier
        :type addr_amplifier: str
        :param mode_amplifier: mode of the Amplifier
        :type mode_amplifier: str
        :param power_amplifier: power of the Amplifier in dBm
        :type power_amplifier: float
        :param wss_operations: operations to be configured on the WaveShaper
        :type wss_operations: dict
        :param logical_associations: transmission between DAC and OSC
        :type logical_associations: list
        :param ip_rest_server: IP address of GPIB-ETHERNET of the DAC/OSC REST Server
        :type ip_rest_server: str
        """
        # Laser parameters
        self.ip_laser = ip_laser
        self.addr_laser = str(addr_laser)
        self.channel_laser = channel_laser
        self.power_laser = power_laser
        self.losses_laser = losses_laser

        # OA parameters
        self.ip_amplifier = ip_amplifier
        self.addr_amplifier = str(addr_amplifier)
        self.mode_amplifier = mode_amplifier
        self.power_amplifier = power_amplifier

        # WSS parameters
        self.wss_operations = wss_operations

        # DAC/OSC parameters
        if logical_associations is not None:
            self.logical_associations = list(logical_associations)
        else:
            self.logical_associations = list()

        # REST API
        self.ip_rest_server = ip_rest_server
        self.api = RestApi(self.ip_rest_server)

    def laser_setup(self, freq, power):
        """
        Laser setup.

            - Calculate lambda0 from frequency specified by freq.
            - Set wavelength of the Laser.
            - Set the power of the Laser.

        :param freq: frequency
        :type freq: float
        :param power: power
        :type power: float
        """
        try:
            lambda0 = (299792.458 / (freq * 1e6)) * 1e9
            Laser.configuration(self.ip_laser, self.addr_laser, self.channel_laser, lambda0, power)

        except Exception as e:
            logger.error("Laser setup failed, error: %s" % e)
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
            # add bn, En and eq to logical associations between DAC and OSC
            for i in range(len(self.logical_associations)):
                self.logical_associations[i]['bn'] = bn
                self.logical_associations[i]['En'] = En
                self.logical_associations[i]['eq'] = eq

            result = self.api.dacOscConfiguration(self.logical_associations)
            return result

        except Exception as e:
            logger.error("DAC/OSC setup failed, error: %s" % e)
            raise e

    def amplifier_setup(self):
        """
        Amplifier setup.

            - Set mode of the Amplifier.
            - Set power of the Amplifier.
        """
        try:
            Amplifier.configuration(self.ip_amplifier, self.addr_amplifier, self.mode_amplifier, self.power_amplifier)

        except Exception as e:
            logger.error("Amplifier setup failed, error: %s" % e)
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
            logger.error("WSS setup failed, error: %s" % e)
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

    def remove_logical_associations(self):
        """
        Remove logical associations between DAC and OSC.
        """
        try:
            for i in range(len(self.logical_associations)):
                assoc_id = self.logical_associations[i]['id']
                dac_out = self.logical_associations[i]['dac_out']
                osc_in = self.logical_associations[i]['osc_in']
                self.api.deleteDACOSCOperationsById(assoc_id)
                logger.debug(
                    "Logical associations {} between DAC {} and OSC {} removed".format(assoc_id, dac_out, osc_in))

        except Exception as e:
            logger.error(e)
            raise e
