"""This is the WSS module.
"""
import logging
import numpy as np

from matplotlib.pyplot import figure, plot, show

logger = logging.getLogger("WSS")
logger.addHandler(logging.NullHandler())

from lib.wss import wsapi


class Wss:
    """
    This is a class for Waveshaper module.
    """
    # TODO documentar variables constants de la classe
    step = 0.001  # TODO
    frequency_end = 196.274  # TODO
    frequency_start = 191.250  # TODO
    speed_of_light = 299792.458

    def __init__(self, name, configfile):
        """
        The constructor for the Waveshaper class.

        :param name: name of the Waveshaper
        :type name: str
        :param configfile: configuration file of the Waveshaper
        :type configfile: str
        """
        self.name = name
        self.filename = configfile
        self.initialization()
        self.open()

    def initialization(self):
        """
        Initialize the Waveshaper default parameters:

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
        Create and Open the Waveshaper.
        """
        name = self.name
        filename = self.filename
        try:
            wsapi.ws_create_waveshaper(name, filename)
            logger.debug("Waveshaper {} created with configuration file {}".format(name, filename))
            try:
                wsapi.ws_open_waveshaper(name)
                logger.debug("Waveshaper %s opened" % name)

            except Exception as e:
                logger.error("Waveshaper {} not opened, {}".format(name, e))
                raise e

        except Exception as e:
            logger.error("Waveshaper {} not created, {}".format(name, e))
            raise e

    def close(self):
        """
        Close and Delete the Waveshaper.
        """
        name = self.name
        try:
            wsapi.ws_close_waveshaper(name)
            logger.debug("Waveshaper %s closed" % name)
            try:
                wsapi.ws_delete_waveshaper(self.name)
                logger.debug("Waveshaper %s deleted" % name)

            except Exception as e:
                logger.error("Waveshaper {} not closed, {}".format(name, e))
                raise e

        except Exception as e:
            logger.error("Waveshaper {} not deleted, {}".format(name, e))
            raise e

    def execute(self):
        """
        Load the desired profile according to the Waveshaper wavelength, port attenuation, phase and bandwidth for the
        filter configuration.
        """
        profiletext = ""
        freq = Wss.speed_of_light / self.wavelength
        startfreq = freq - self.bandwidth * 0.5 * 1e-3  # start frequency in THz
        stopfreq = freq + self.bandwidth * 0.5 * 1e-3  # strop frequency in THz
        # TODO extract * 0.5 * 1e-3

        for frequency in np.arange(startfreq, stopfreq, Wss.step, dtype=float):
            for k in range(1):
                if self.wavelength[k] > 1 and startfreq[k] < frequency < stopfreq[k]:
                    profiletext += "%.3f\t%.1f\t%.1f\t%d\n" % (frequency, self.attenuation[k], self.phase[k], k + 1)
                else:
                    profiletext += "%.3f\t60.0\t0.0\t0\n" % frequency

        # TODO treure rc per try and except pero s'ha de modificar la llibreria wsapi
        # TODO logger
        rc = wsapi.ws_load_profile(self.name, profiletext)
        if rc < 0:
            print(wsapi.ws_get_result_description(rc))

    def execute_wss(self, profile):
        """
        Load the desired profile to the Waveshaper.

        :param profile: # TODO
        :type profile # TODO
        """
        profiletext = ""
        for frequency in np.arange(Wss.frequency_start, Wss.frequency_end, Wss.step, dtype=float):
            profiletext += "%.3f\t%.1f\t%.1f\t%d\n" % (frequency, profile, 0, 1)

        # TODO treure rc per try and except pero s'ha de modificar la llibreria wsapi
        # TODO logger
        rc = wsapi.ws_load_profile(self.name, profiletext)
        if rc < 0:
            print(wsapi.ws_get_result_description(rc))

    def check_profile(self):
        """
        Check the loaded profile.

        :return: bandwidth and attenuation
        :rtype: list
        """
        profiletext = ""
        check_BW_wss = 0
        check_att = []
        for frequency in np.arange(FREQUENCY_START, FREQUENCY_END, STEP, dtype=float):
            for k in range(1):
                profiletext = profiletext + "%.3f\t60.0\t0.0\t0\n" % frequency

        rc = wsapi.ws_get_profile(self.name, profiletext, len(profiletext))  # TODO ws_get_profile not implemented
        if rc < 0:
            print(wsapi.ws_get_result_description(rc))

        profiletext_out = profiletext.split("\n")
        profile_wss = np.array(np.zeros(len(profiletext_out) * 4)).reshape((len(profiletext_out), 4))
        # profile_wss = profile_wss.reshape((len(profiletext_out), 4))
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
            print('ERROR: All the attenuation values are set to 60dB')

        return check_BW_wss, check_att
