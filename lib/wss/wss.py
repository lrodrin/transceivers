"""This is the WSS module.
"""
import logging
import time
import wsapi
import numpy as np

from matplotlib.pyplot import figure, plot, show

logger = logging.getLogger("WSS")
logger.addHandler(logging.NullHandler())


class Wss:
    """
    This is a class for WaveShaper module.
    """
    step = 0.001  # Frequency step
    frequency_end = 196.274  # End frequency 
    frequency_start = 191.250  # Start frequency
    speed_of_light = 299792.458
    time_sleep = 5  # Time needed to load the WaveShaper profile before returning the bandwidth and port attenuation.

    def __init__(self, name, configfile):
        """
        The constructor for the WaveShaper class.

        :param name: name of the WaveShaper
        :type name: str
        :param configfile: configuration file of the WaveShaper
        :type configfile: str
        """
        self.name = name
        self.filename = configfile
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
        self.wavelength = np.ones([4, 1], dtype=float)
        self.bandwidth = np.zeros([4, 1], dtype=float)
        self.phase = np.zeros([4, 1], dtype=float)
        self.attenuation = 60 * np.ones([4, 1], dtype=float)

    def open(self):
        """
        Create and open the WaveShaper.
        """
        name = self.name
        filename = self.filename
        try:
            wsapi.ws_create_waveshaper(name, filename)
            logger.debug("WaveShaper {} created with configuration file {}".format(name, filename))
            try:
                wsapi.ws_open_waveshaper(name)
                logger.debug("WaveShaper %s opened" % name)

            except Exception as e:
                logger.error("WaveShaper {} not opened, {}".format(name, e))
                raise e

        except Exception as e:
            logger.error("WaveShaper {} not created, {}".format(name, e))
            raise e

    def close(self):
        """
        Close and Delete the WaveShaper.
        """
        name = self.name
        try:
            wsapi.ws_close_waveshaper(name)
            logger.debug("WaveShaper %s closed" % name)
            try:
                wsapi.ws_delete_waveshaper(self.name)
                logger.debug("WaveShaper %s deleted" % name)

            except Exception as e:
                logger.error("WaveShaper {} not closed, {}".format(name, e))
                raise e

        except Exception as e:
            logger.error("WaveShaper {} not deleted, {}".format(name, e))
            raise e

    def execute(self):
        """
        Load the desired profile according to the WaveShaper wavelength, port attenuation, phase and bandwidth for the
        filter configuration.
        """
        profiletext = ""
        freq = Wss.speed_of_light / self.wavelength
        startfreq = freq - self.bandwidth * 0.5 * 1e-3  # start frequency in THz
        stopfreq = freq + self.bandwidth * 0.5 * 1e-3  # strop frequency in THz
        # TODO extract * 0.5 * 1e-3

        for frequency in np.arange(Wss.frequency_start, Wss.frequency_end, Wss.step, dtype=float):
            for k in range(1):
                if self.wavelength[k] > 1 and startfreq[k] < frequency < stopfreq[k]:
                    profiletext = profiletext + "%.3f\t%.1f\t%.1f\t%d\n" % (
                    frequency, self.attenuation[k], self.phase[k], k + 1)
                else:
                    profiletext = profiletext + "%.3f\t60.0\t0.0\t0\n" % frequency

        logger.debug("WSS profile created")  # TODO try and except
        rc = wsapi.ws_load_profile(self.name, profiletext)
        if rc < 0:
            logger.error("Profile not loaded to the WaveShaper, description: %s" % wsapi.ws_get_result_description(rc))
        else:
            logger.debug("Profile loaded to the WaveShaper")

    def execute_wss(self, profile):
        """
        Load the desired profile to the WaveShaper.

        :param profile: contains the frequency response to be uploaded to the WaveShaper
        :type profile: float array
        """
        profiletext = ""
        for frequency in np.arange(Wss.frequency_start, Wss.frequency_end, Wss.step, dtype=float):
            profiletext = profiletext + "%.3f\t%.1f\t%.1f\t%d\n" % (frequency, profile, 0, 1)

        logger.debug("WSS profile created")  # TODO try and except
        rc = wsapi.ws_load_profile(self.name, profiletext)
        if rc < 0:
            logger.error("WaveShaper profile not uploaded, description: %s" % wsapi.ws_get_result_description(rc))
        else:
            logger.debug("WaveShaper profile uploaded")

    def check_profile(self):
        """
        Check the loaded profile.

        :return: bandwidth and port attenuation
        :rtype: list
        """
        profiletext = ""
        check_BW_wss = 0
        check_att = []
        for frequency in np.arange(Wss.frequency_start, Wss.frequency_end, Wss.step, dtype=float):
            for k in range(1):
                profiletext = profiletext + "%.3f\t60.0\t0.0\t0\n" % frequency

        # TODO ws_get_profile not implemented
        # rc = wsapi.ws_get_profile(self.name, profiletext, len(profiletext))
        # if rc < 0:
        #     print(wsapi.ws_get_result_description(rc))

        logger.debug("WSS profile successfully read")
        profiletext_out = profiletext.split("\n")
        profile_wss = np.array(np.zeros(len(profiletext_out) * 4)).reshape((len(profiletext_out), 4))

        for index in range(0, len(profiletext_out) - 1):
            profile_wss[index] = profiletext_out[index].split("\t")

        profile_wss = profile_wss[0:len(profile_wss) - 1, :]
        peakind = np.nonzero(profile_wss[:, 1] == self.attenuation[0])
        if not peakind:
            data = profile_wss[peakind]
            check_BW_wss = (data[-1, 0] - data[0, 0]) * 1e3  # in GHz
            check_att = data[:, 1]
            figure()
            plot(profile_wss[:, 0], profile_wss[:, 1])
            show()

        else:
            logger.error("All the attenuation values are set to 60dB")

        return [check_BW_wss, check_att]

    @staticmethod
    def configuration(name, configfile, lambda0, att, phase, bw):
        """
        WaveShaper configuration:

            - Set the wavelength, port attenuation, phase and bandwidth for the filter configuration of the WaveShaper.
            - Load the desired profile according to the WaveShaper values of filter configuration.

        :param name: name of the WaveShaper
        :type name: str
        :param configfile: configuration file of the WaveShaper
        :type configfile: str
        :param lambda0: wavelength of the WaveShaper
        :type lambda0: float
        :param att: port attenuation of the WaveShaper
        :type att: float
        :param phase: phase of the WaveShaper
        :type phase: float
        :param bw: bandwidth of the WaveShaper
        :type bw: float
        """
        try:
            wss_tx = Wss(name, configfile)
            wss_tx.wavelength[0] = lambda0
            wss_tx.attenuation[0] = att
            wss_tx.phase[0] = phase
            wss_tx.bandwidth[0] = bw
            wss_tx.execute()
            time.sleep(Wss.time_sleep)
            params = wss_tx.check_profile()
            print('BW = ', params[0])
            # logger.debug("WaveShaper parameters - BW = {}, ATT = {}".format(params[0], params[1]))
            wss_tx.close()

        except Exception as error:
            logger.error("WaveShaper configuration method, {}".format(error))
            raise error
