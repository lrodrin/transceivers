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

speed_of_light = 299792.458


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
        self.ip_laser = ip_laser
        self.addr_laser = addr_laser
        self.channel_laser = channel_laser
        self.power_laser = power_laser

        # OA parameters
        self.ip_amplifier = ip_amplifier
        self.addr_amplifier = addr_amplifier
        self.mode_amplifier = mode_amplifier
        self.power_amplifier = power_amplifier

        # WSS parameters
        self.wss_operations = dict(wss_operations)

        # DAC/OSC parameters
        self.logical_associations = list(logical_associations)

        # REST API
        self.ip_rest_server = ip_rest_server
        self.api = RestApi(self.ip_rest_server)

    def blueStartup(self, NCF, bn, En, eq):  # CALLED FROM netconf_server.py
        """
        Configuration of an Optical Channel by setting nominal central frequency, constellation and equalization.

        :param NCF: nominal central frequency
        :param NCF: float
        :param bn: bits per symbol
        :type bn: float array of 512 positions
        :param En: power per symbol
        :type En: float array of 512 positions
        :param eq: equalization
        :type eq: str
        """
        try:
            lambda0 = (speed_of_light / (NCF * 1e6)) * 1e9  # calculate lambda0 with NCF
            params = Laser.configuration(self.ip_laser, self.addr_laser, self.channel_laser, lambda0, self.power_laser)
            logger.debug(
                "Laser parameters - status: {}, wavelength: {}, power: {}".format(params[0], params[1], params[2]))
            if params is not None:
                try:
                    # TODO more than one association
                    # TODO store bn, En and eq to logical_associations
                    SNR, BER = self.api.dacOscConfiguration(self.logical_associations)
                    logger.debug("SNR = %s" % SNR)

                except Exception as e:
                    logger.error(e)
                    raise e
            else:
                error_msg = "Parameters returned from Laser are not correct"
                logger.error(error_msg)
                raise ValueError(error_msg)

        except Exception as e:
            logger.error(e)
            raise e

    def metroStartup(self, och, freq, power, mode):  # CALLED FROM openconfig_server.py
        """
        Configuration of an Optical Channel by setting frequency, power and mode.

            - WSS startup.
            - Amplifier startup.
            - Laser startup.
            - DAC/OSC startup.

        :param och: id to identify the optical channel
        :type och: str
        :param freq: frequency of the optical channel expressed in MHz. 193.3e6 (1550.99 nm) for channel 1 or 193.4e6
        (1550.12 nm) for channel 2
        :type freq: float
        :param power: target output power level of the optical channel expressed in increments of 0.01 dBm.
        3.20 dBm for uniform loading or 0.4 dBm for loading
        :type power: float
        :param mode: vendor-specific mode identifier for identify the operational mode of the optical channel. SD-FEC
        or HD-FEC
        :type mode: str
        """
        try:
            # WSS startup
            result = self.api.wSSConfiguration(self.wss_operations)
            logging.debug(result)
            try:
                # OA startup
                params = Amplifier.configuration(self.ip_amplifier, self.addr_amplifier, self.mode_amplifier,
                                                 self.power_amplifier)
                logger.debug(
                    "Amplifier parameters - status: {}, mode: {}, power: {}".format(params[0], params[1], params[2]))
                if params is not None:
                    try:
                        # Laser startup
                        lambda0 = (speed_of_light / (freq * 1e6)) * 1e9  # calculate lambda0 with freq
                        self.power_laser = power + 9  # considering the losses of the modulation MZM
                        params = Laser.configuration(self.ip_laser, self.addr_laser, self.channel_laser, lambda0,
                                                     self.power_laser)
                        logger.debug(
                            "Laser parameters - status: {}, wavelength: {}, power: {}".format(params[0], params[1],
                                                                                              params[2]))
                        if params is not None:
                            try:
                                # DAC/OSC startup
                                # TODO more than one association
                                # TODO store bn, En and eq to logical_associations
                                SNR, BER = self.api.dacOscConfiguration(self.logical_associations)
                                logger.debug("BER = %s" % BER)

                            except Exception as e:
                                logger.error(e)
                                raise e
                        else:
                            error_msg = "Parameters returned from Laser are not correct"
                            logger.error(error_msg)
                            raise ValueError(error_msg)

                    except Exception as e:
                        logger.error(e)
                        raise e
                else:
                    error_msg = "Parameters returned from Amplifier are not correct"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

            except Exception as e:
                logger.error(e)
                raise e

        except Exception as e:
            logger.error(e)
            raise e

    @staticmethod
    def channelAssignment(client, och):
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

    def getSNR(self, bn, En, eq):  # CALLED FROM netconf_server.py
        """
        Return the estimated SNR per subcarrier.

        :param bn: bits per symbol
        :type bn: float array of 512 positions
        :param En: power per symbol
        :type En: float array of 512 positions
        :param eq: equalization
        :type eq: str
        :return: estimated SNR per subcarrier
        :rtype: list of floats
        """
        try:
            # TODO more than one association
            # TODO store bn, En and eq to logical_associations
            SNR, BER = self.api.dacOscConfiguration(self.logical_associations)
            logger.debug("SNR = %s" % SNR)
            return SNR

        except Exception as e:
            logger.error(e)
            raise e

    def blueStop(self):  # CALLED FROM netconf_server.py
        """
        Disable Laser.
        # TODO delete DAC/OSC associations
        """
        try:
            yenista = Laser(self.ip_laser, self.addr_laser)
            yenista.enable(self.channel_laser, False)
            logger.debug("Laser {} on channel {} disabled".format(self.ip_laser, self.channel_laser))

        except Exception as e:
            logger.error("Laser {} on channel {} not disabled, Error: {}".format(self.ip_laser, self.channel_laser, e))
            raise e

    def metroStop(self):  # CALLED FROM openconfig_server.py
        """
        Disable Laser and Amplifier.
        # TODO delete WSS operations
        # TODO delete DAC/OSC associations
        """
        try:
            yenista = Laser(self.ip_laser, self.addr_laser)
            yenista.enable(self.channel_laser, False)
            logger.debug("Laser {} on channel {} disabled".format(self.ip_laser, self.channel_laser))
            try:
                manlight = Amplifier(self.ip_amplifier, self.addr_amplifier)
                manlight.enable(False)
                logger.debug("Amplifier %s disabled" % self.ip_amplifier)

            except Exception as e:
                logger.error("Amplifier {} not disabled, error: {}".format(self.ip_amplifier, e))
                raise e

        except Exception as e:
            logger.error("Laser {} on channel {} not disabled, error: {}".format(self.ip_laser, self.channel_laser, e))
            raise e
