"""This is the WSS module.
"""
import logging
import time

import numpy as np

from lib.wss import wsapi

logger = logging.getLogger("WSS")
logger.addHandler(logging.NullHandler())


class WSS:
    """
    This is a class for WaveShaper module.

    :var float frequency_start: Start frequency
    :var float frequency_end: End frequency
    :var float step: Frequency step
    :var float speed_of_light: Speed of light in m/s
    :var int time_sleep: Time needed to load the WaveShaper profile before returning the bandwidth and port attenuation
    :var str folder: Folder that contains the configuration files
    :var str configfile_1: Configuration file for the WaveShaper 1
    :var str configfile_2: Configuration file for the WaveShaper 2
    """
    frequency_start = 191.250
    frequency_end = 196.274
    step = 0.001
    speed_of_light = 299792458
    time_sleep = 5
    folder = "C:/Users/CTTC/Desktop/agent-bvt/conf/"
    configfile_1 = "SN042561.wsconfig"
    configfile_2 = "SN200162.wsconfig"

    def __init__(self, id, n, m):
        """
        The constructor for the WaveShaper class.

        :param id: id of the WaveShaper
        :type id: int
        :param n: number to identify the input ports
        :type n: int
        :param m: number to identify the output ports
        :type m: int
        """
        self.id = id
        if id == 1:
            self.filename = self.folder + self.configfile_1
        elif id == 2:
            self.filename = self.folder + self.configfile_2

        self.n = n
        self.m = m
        self.initialization()
        self.open()

    def initialization(self):
        """
        Initialize the WaveShaper default parameters:

            - wavelength (float): Set central frequency. The range of wavelength takes 1528'773 to 1566'723 nm.
            - bandwidth (float): Set bandwidth.
            - phase (float): Set phase.
            - attenuation (float): Set port attenuation.
        """
        self.wavelength = np.ones([self.n, self.m], dtype=float)
        self.bandwidth = np.zeros([self.n, self.m], dtype=float)
        self.phase = np.zeros([self.n, self.m], dtype=float)
        self.attenuation = 60 * np.ones([self.n, self.m], dtype=float)

    def open(self):
        """
        Create and open the WaveShaper.
        """
        name = str(self.id)
        filename = self.filename
        try:
            wsapi.ws_create_waveshaper(name, filename)
            logger.debug("WaveShaper {} created with configuration file {}".format(name, filename))
            try:
                wsapi.ws_open_waveshaper(name)
                logger.debug("WaveShaper %s opened" % name)

            except Exception as e:
                logger.error("WaveShaper {} not opened, {}".format(name, e))

        except Exception as e:
            logger.error("WaveShaper {} not created, {}".format(name, e))

    def close(self):
        """
        Close and delete the WaveShaper.
        """
        name = str(self.id)
        try:
            wsapi.ws_close_waveshaper(name)
            logger.debug("WaveShaper %s closed" % name)
            try:
                wsapi.ws_delete_waveshaper(name)
                logger.debug("WaveShaper %s deleted" % name)

            except Exception as e:
                logger.error("WaveShaper {} not closed, {}".format(name, e))

        except Exception as e:
            logger.error("WaveShaper {} not deleted, {}".format(name, e))

    def execute(self):
        """
        Load the desired profile according to the WaveShaper wavelength, port attenuation, phase and bandwidth for the
        filter configuration.

        :return: 0 if profile was loaded and -1 otherwise
        :rtype: int
        """
        profiletext = ""
        freq = self.speed_of_light / self.wavelength
        startfreq = freq - self.bandwidth * 0.5 * 1e-3  # start frequency in THz
        stopfreq = freq + self.bandwidth * 0.5 * 1e-3  # strop frequency in THz

        for frequency in np.arange(self.frequency_start, self.frequency_end, self.step, dtype=float):
            for k in range(self.n):  # for each input port
                if self.wavelength[k] > 1 and startfreq[k] < frequency < stopfreq[k]:
                    profiletext += "%.3f\t%.1f\t%.1f\t%d\n" % (
                        frequency, self.attenuation[k], self.phase[k], k + 1)
                else:
                    profiletext += "%.3f\t60.0\t0.0\t0\n" % frequency

        logger.debug("WaveShaper %s profile created" % str(self.id))
        return wsapi.ws_load_profile(str(self.id), profiletext)

    def execute_wss(self, profile):
        """
        Load the desired profile to the WaveShaper.

        :param profile: contains the frequency response to be uploaded to the WaveShaper
        :type profile: float array
        :return: 0 if profile was loaded and -1 otherwise
        :rtype: int
        """
        profiletext = ""
        for frequency in np.arange(self.frequency_start, self.frequency_end, self.step, dtype=float):
            profiletext += "%.3f\t%.1f\t%.1f\t%d\n" % (frequency, profile, 0, 1)

        logger.debug("WaveShaper %s profile created" % str(self.id))
        return wsapi.ws_load_profile(str(self.id), profiletext)

    def configuration(self, operation):
        """
        WaveShaper configuration:

            - Set the wavelength, port attenuation, phase and bandwidth for the filter configuration of the WaveShaper.
            - Load the desired profile according to the WaveShaper values of filter configuration.

        :param operation: operation to configure the WaveShaper
        :type operation: list
        """
        wss_id = str(self.id)
        for i in range(self.n):  # for each number of input ports
            for j in range(self.m):  # for each number of output ports
                self.wavelength[i][j] = operation[i]['lambda0']
                self.attenuation[i][j] = operation[i]['att']
                self.phase[i][j] = operation[i]['phase']
                self.bandwidth[i][j] = operation[i]['bw']

        try:
            rc = self.execute()
            if rc < 0:
                logger.error("WaveShaper {} profile not loaded, {}".format(wss_id, wsapi.ws_get_result_description(rc)))
            else:
                logger.debug("WaveShaper %s profile loaded" % wss_id)
                time.sleep(self.time_sleep)
                self.close()

        except Exception as error:
            logger.error("WaveShaper configuration method, {}".format(error))
            raise error
