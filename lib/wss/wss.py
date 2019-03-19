"""This is the WSS module.
"""
import logging
import time

import matplotlib.pyplot as plt
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
    speed_of_light = 299792.458
    time_sleep = 5
    folder = "C:/Users/CTTC/Desktop/agent-bvt/config/"
    configfile_1 = "SN042561.wsconfig"
    configfile_2 = "SN200162.wsconfig"

    def __init__(self, id, n, m):
        """
        The constructor for the WaveShaper class.
        Initialize the WaveShaper default parameters:

            - wavelength (float): Central frequency. The range of wavelength takes 1528'773 to 1566'723 nm.
            - attenuation (float): Port attenuation.
            - phase (float): Phase.
            - bandwidth (float): Bandwidth.

        :param id: id of the WaveShaper
        :type id: int
        :param n: max number of the input ports
        :type n: int
        :param m: max number of the output ports
        :type m: int
        """
        self.id = id
        if id == 1:
            self.filename = self.folder + self.configfile_1
        elif id == 2:
            self.filename = self.folder + self.configfile_2

        self.n = n
        self.m = m
        self.wavelength = np.ones(shape=(self.n, self.m), dtype=float)
        self.attenuation = 60 * np.ones(shape=(self.n, self.m), dtype=float)
        self.phase = np.zeros(shape=(self.n, self.m), dtype=float)
        self.bandwidth = np.zeros(shape=(self.n, self.m), dtype=float)
        self.open()

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

    def execute(self, profiletext, k):
        """
        Create and update the desired profile according to the WaveShaper wavelength, port attenuation,
        phase and bandwidth for the filter configuration.

        :param profiletext: text to save frequency, attenuation, phase for each input port specified by k
        :rtype profiletext: str
        :param k: input port
        :rtype k: int
        :return: profiletext
        :rtype: str
        """
        freq = self.speed_of_light / self.wavelength
        startfreq = freq - self.bandwidth * 0.5 * 1e-3  # start frequency in THz
        stopfreq = freq + self.bandwidth * 0.5 * 1e-3  # stop frequency in THz

        for frequency in np.arange(self.frequency_start, self.frequency_end, self.step, dtype=float):
            if self.wavelength[k-1] > 1 and startfreq[k-1] < frequency < stopfreq[k-1]:
                profiletext += "%.3f\t%.1f\t%.1f\t%d\n" % (
                    frequency, self.attenuation[k-1], self.phase[k-1], k)
            else:
                profiletext += "%.3f\t60.0\t0.0\t0\n" % frequency

        ################DELETE######################################
        profiletext_out = profiletext.split("\n")
        profile_wss = np.array(np.zeros(len(profiletext_out) * 4))
        profile_wss = profile_wss.reshape((len(profiletext_out), 4))
        for index in range(0, len(profiletext_out) - 1):
            profile_wss[index] = profiletext_out[index].split("\t")

        profile_wss = profile_wss[0:len(profile_wss) - 1, :]

        plt.figure()
        plt.plot(profile_wss[:, 0], profile_wss[:, 1])
        plt.show()
        #################DELETE######################################

        logger.debug("WaveShaper %s profile updated for input port %s" % (str(self.id), str(k)))
        return profiletext

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

    def configuration(self, operations):
        """
        WaveShaper configuration:

            - Set the wavelength, port attenuation, phase and bandwidth for the filter configuration.
            - Load the desired profile according to the WaveShaper filter configuration.

        :param operations: operations to configure the filter of the WaveShaper
        :type operations: list
        """
        profiletext = str()
        wss_id = str(self.id)
        try:
            for i in range(len(operations)):  # for each operation
                x = operations[i]['port_in'] - 1
                y = operations[i]['port_out'] - 1
                self.wavelength[x][y] = operations[i]['lambda0']
                self.attenuation[x][y] = operations[i]['att']
                self.phase[x][y] = operations[i]['phase']
                self.bandwidth[x][y] = operations[i]['bw']

                profiletext += self.execute(profiletext, x)  # update profile

        except Exception as error:
            logger.error("WaveShaper {} filter configuration failed, error: {}".format(wss_id, error))
            raise error

        finally:
            rc = wsapi.ws_load_profile(wss_id, profiletext)
            if rc < 0:
                logger.error("WaveShaper {} profile not loaded, description: {}".format(wss_id,
                                                                                        wsapi.ws_get_result_description(
                                                                                            rc)))
            else:
                logger.debug("WaveShaper %s profile loaded" % wss_id)
                time.sleep(self.time_sleep)
                self.close()
                logger.debug("WaveShaper %s configuration finished" % wss_id)
