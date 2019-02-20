"""This is the WSS module.
"""
import logging
import time
import collections
import numpy as np

from lib.wss import wsapi

logger = logging.getLogger("WSS")
logger.addHandler(logging.NullHandler())


class WSS:
    """
    This is a class for WaveShaper module.
    """
    operations = collections.OrderedDict()  # operations to be configured on the WaveShaper
    frequency_start = 191.250  # Start frequency
    frequency_end = 196.274  # End frequency
    step = 0.001  # Frequency step
    speed_of_light = 299792.458
    time_sleep = 5  # Time needed to load the WaveShaper profile before returning the bandwidth and port attenuation.
    folder = "C:/Users/CTTC/Desktop/agent-bvt/conf/"  # Folder that contains the configuration files
    configfile_1 = "SN042561.wsconfig"  # Configuration file for the WaveShaper 1
    configfile_2 = "SN200162.wsconfig"  # Configuration file for the WaveShaper 2

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
        Close and Delete the WaveShaper.
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

        logger.debug("WaveShaper profile created")
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

        logger.debug("WaveShaper profile created")
        return wsapi.ws_load_profile(str(self.id), profiletext)

    def configuration(self, operation):
        """
        WaveShaper configuration:

            - Set the wavelength, port attenuation, phase and bandwidth for the filter configuration of the WaveShaper.
            - Load the desired profile according to the WaveShaper values of filter configuration.
            - Save the operation to configure the WaveShaper.

        :param operation: operation to configure the WaveShaper
        :type operation: list
        """
        wss_id = str(self.id)
        logger.debug("WaveShaper %s configuration started" % wss_id)
        for op in operation:
            pos_x = op['port_in'] - 1
            pos_y = op['port_out'] - 1
            self.wavelength[pos_x][pos_y] = op['lambda0']
            self.attenuation[pos_x][pos_y] = op['att']
            self.phase[pos_x][pos_y] = op['phase']
            self.bandwidth[pos_x][pos_y] = op['bw']

        try:
            rc = self.execute()
            if rc < 0:
                logger.error("Profile not loaded to the WaveShaper, %s" % wsapi.ws_get_result_description(rc))
            else:
                logger.debug("Profile loaded to the WaveShaper")
                time.sleep(self.time_sleep)
                self.close()
                # Adding new operation into the WaveShaper operations
                if wss_id not in self.operations.keys():
                    self.operations[wss_id] = operation
                else:
                    self.operations[wss_id] += operation

                logger.debug("WaveShaper %s configuration finished" % wss_id)

        except Exception as error:
            logger.error("WaveShaper configuration method, {}".format(error))
