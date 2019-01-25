import numpy as np
from matplotlib.pyplot import figure, plot, show

from lib.wss import wsapi

STEP = 0.001
FREQUENCY_END = 196.274
FREQUENCY_START = 191.250
SPEED_OF_LIGHT = 299792.458


# TODO error control

class Wss:
    """
       This is a class for Waveshaper configuration.

       """

    def __init__(self, name, configfile):
        """
        The constructor for Waveshaper class.

        Initialize the Waveshaper default parameters:

            - Set wavelength. 1528'773 to 1566'723 nm.
            - Set bandwidth.
            - Set phase.
            - Set attenuation.

        :param name: name of the waveshaper
        :param configfile: configuration file of the waveshaper
        :type name: str
        :type configfile: str
        """
        self.attenuation = 60 * np.ones([4, 1], dtype=float)
        self.phase = np.zeros([4, 1], dtype=float)
        self.bandwidth = np.zeros([4, 1], dtype=float)
        self.wavelength = np.ones([4, 1], dtype=float)
        self.name = name
        self.filename = configfile
        self.open()

    def open(self):
        """
        Create and open the Waveshaper.

        """
        wsapi.ws_create_waveshaper(self.name, self.filename)
        wsapi.ws_open_waveshaper(self.name)

    def close(self):
        """
        Close and delete the Waveshaper.

        """
        wsapi.ws_close_waveshaper(self.name)
        wsapi.ws_delete_waveshaper(self.name)

    def execute(self):
        """
        Load the desired profile according to the Waveshaper specifications.

        """
        profiletext = ""
        freq = SPEED_OF_LIGHT / self.wavelength
        startfreq = freq - self.bandwidth * 0.5 * 1e-3  # startfreq in THz
        stopfreq = freq + self.bandwidth * 0.5 * 1e-3  # stropfreq in THz
        # TODO extract * 0.5 * 1e-3

        # for frequency in np.arange(191.250, 196.274, 0.001, dtype=float):
        for frequency in np.arange(FREQUENCY_START, FREQUENCY_END, STEP, dtype=float):
            for k in range(1):
                if self.wavelength[k] > 1 and startfreq[k] < frequency < stopfreq[k]:
                    profiletext = profiletext + "%.3f\t%.1f\t%.1f\t%d\n" % (
                        frequency, self.attenuation[k], self.phase[k], k + 1)
                else:
                    profiletext = profiletext + "%.3f\t60.0\t0.0\t0\n" % frequency

        rc = wsapi.ws_load_profile(self.name, profiletext)
        if rc < 0:
            print(wsapi.ws_get_result_description(rc))

    # TODO diferencia entre execute i execute_wss ?

    def execute_wss(self, profile):
        """
        Load the desired profile according to the Waveshaper specifications.

        """
        profiletext = ""
        for frequency in np.arange(FREQUENCY_START, FREQUENCY_END, STEP, dtype=float):
            profiletext = profiletext + "%.3f\t%.1f\t%.1f\t%d\n" % (frequency, profile, 0, 1)

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
