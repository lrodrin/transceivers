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
    """
    frequency_start = 191.250  # Start frequency
    frequency_end = 196.274  # End frequency
    step = 0.001  # Frequency step
    speed_of_light = 299792.458
    time_sleep = 5  # Time needed to load the WaveShaper profile before returning the bandwidth and port attenuation.
    folder = "C:/Users/CTTC/Desktop/agent-bvt/conf/"  # Folder that contains the configuration files
    configfile_1 = "SN042561.wsconfig"  # Configuration file of the WaveShaper 1
    configfile_2 = "SN042562.wsconfig"  # Configuration file of the WaveShaper 2

    def __init__(self, id, n, m):
        """
        The constructor for the WaveShaper class.

        :param id: id of the WaveShaper
        :type id: int
        :param n: number to identify the input port
        :type n: int
        :param m: number to identify the output port
        :type m: int
        """
        self.id = id
        if id == 1:
            self.filename = WSS.folder + WSS.configfile_1
        elif id == 2:
            self.filename = WSS.folder + WSS.configfile_2

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
        """
        profiletext = ""
        freq = WSS.speed_of_light / self.wavelength
        startfreq = freq - self.bandwidth * 0.5 * 1e-3  # start frequency in THz
        stopfreq = freq + self.bandwidth * 0.5 * 1e-3  # strop frequency in THz

        for frequency in np.arange(WSS.frequency_start, WSS.frequency_end, WSS.step, dtype=float):
            for k in range(self.n):
                if self.wavelength[k] > 1 and startfreq[k] < frequency < stopfreq[k]:
                    profiletext += "%.3f\t%.1f\t%.1f\t%d\n" % (
                        frequency, self.attenuation[k], self.phase[k], k + 1)
                else:
                    profiletext += "%.3f\t60.0\t0.0\t0\n" % frequency

        logger.debug("WaveShaper profile created")
        rc = wsapi.ws_load_profile(self.id, profiletext)
        if rc < 0:
            logger.error("Profile not loaded to the WaveShaper, %s" % wsapi.ws_get_result_description(rc))
        else:
            logger.debug("Profile loaded to the WaveShaper")

    def execute_wss(self, profile):
        """
        Load the desired profile to the WaveShaper.

        :param profile: contains the frequency response to be uploaded to the WaveShaper
        :type profile: float array
        """
        profiletext = ""
        for frequency in np.arange(WSS.frequency_start, WSS.frequency_end, WSS.step, dtype=float):
            profiletext += "%.3f\t%.1f\t%.1f\t%d\n" % (frequency, profile, 0, 1)

        logger.debug("WaveShaper profile created")
        rc = wsapi.ws_load_profile(self.id, profiletext)
        if rc < 0:
            logger.error("Profile not uploaded to the WaveShaper, %s" % wsapi.ws_get_result_description(rc))
        else:
            logger.debug("Profile uploaded to the WaveShaper")

    # def check_profile(self):
    #     """
    #     Check the loaded profile.
    #
    #     :return: bandwidth and port attenuation
    #     :rtype: list
    #     """
    #     profiletext = ""
    #     for frequency in np.arange(WSS.frequency_start, WSS.frequency_end, WSS.step, dtype=float):
    #         for k in range(1):
    #             profiletext += "%.3f\t60.0\t0.0\t0\n" % frequency
    #
    #     # TODO ws_get_profile not implemented
    #     # rc = wsapi.ws_get_profile(self.name, profiletext, len(profiletext))
    #     # if rc < 0:
    #     #     print(wsapi.ws_get_result_description(rc))
    #
    #     logger.debug("WaveShaper profile successfully readed")
    #     profiletext_out = profiletext.split("\n")
    #     profile_wss = np.array(np.zeros(len(profiletext_out) * 4)).reshape((len(profiletext_out), 4))
    #
    #     for index in range(0, len(profiletext_out) - 1):
    #         profile_wss[index] = profiletext_out[index].split("\t")
    #
    #     profile_wss = profile_wss[0:len(profile_wss) - 1, :]
    #     peakind = np.nonzero(profile_wss[:, 1] == self.attenuation[0])
    #     if not peakind:
    #         data = profile_wss[peakind]
    #         check_BW_wss = (data[-1, 0] - data[0, 0]) * 1e3  # in GHz
    #         check_att = data[:, 1]
    #         figure()
    #         plot(profile_wss[:, 0], profile_wss[:, 1])
    #         show()
    #         logger.debug("WaveShaper profile successfully checked")
    #         return [check_BW_wss, check_att]
    #
    #     else:
    #         logger.error("WaveShaper profile not successfully checked. All the attenuation values are set to 60 dB")

    @staticmethod
    def configuration(wss_id, operation):
        """
        WaveShaper configuration:

            - Set the wavelength, port attenuation, phase and bandwidth for the filter configuration of the WaveShaper.
            - Load the desired profile according to the WaveShaper values of filter configuration.

        :param wss_id: id of the WaveShaper
        :type wss_id: int
        :param operation: number of input port of the WaveShaper
        :type operation: list of dict
        """
        logger.debug("WaveShaper configuration started")
        n = len(operation)
        m = 1
        print(n, m)
        try:
            wss_tx = WSS(wss_id, n, m)
            for op in operation:
                pos_x = op['port_in'] - 1
                pos_y = op['port_out'] - 1
                print(pos_x, pos_y)
                wss_tx.wavelength[pos_x][pos_y] = op['lambda0']
                wss_tx.attenuation[pos_x][pos_y] = op['att']
                wss_tx.phase[pos_x][pos_y] = op['phase']
                wss_tx.bandwidth[pos_x][pos_y] = op['bw']

            wss_tx.execute()
            time.sleep(WSS.time_sleep)
            wss_tx.close()
            logger.debug("WaveShaper configuration finished")

        except Exception as error:
            logger.error("WaveShaper configuration method, {}".format(error))
