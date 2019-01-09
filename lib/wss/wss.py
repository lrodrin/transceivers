import time
import numpy as np

from matplotlib.pyplot import figure, plot, show
from lib.wss import wsapi

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


class Wss:
    """
       This is a class for Waveshaper configuration.

       """

    def __init__(self, name, configfile):
        """
        The constructor for Wss class.

        Initializes the Wss default parameters:
            - Set name
            - Set configuration file
            - Set wavelength
            - Set bandwidth
            - Set phase
            - Set attenuation

        :param name: name of the waveshaper
        :param configfile: configuration file of the waveshaper
        :type name: str
        :type configfile: str
        """
        self.name = name
        self.filename = configfile
        self.wavelength = np.ones([4, 1], dtype=float)  # wavelengths array
        self.bandwidth = np.zeros([4, 1], dtype=float)  # bandwidths array
        self.phase = np.zeros([4, 1], dtype=float)  # phases array
        self.attenuation = 60 * np.ones([4, 1], dtype=float)  # attenuations array
        self.open()

    def open(self):
        """
        Create and open the waveshaper

        """
        wsapi.ws_create_waveshaper(self.name, self.filename)
        wsapi.ws_open_waveshaper(self.name)

    def close(self):
        """
        Close and delete the waveshaper

        """
        wsapi.ws_close_waveshaper(self.name)
        wsapi.ws_delete_waveshaper(self.name)

    def execute(self):
        """
        Load the desired profile according to the specifications

        """

        profiletext = ""
        freq = 299792.458 / self.wavelength
        startfreq = freq - self.bandwidth * 0.5 * 1e-3  # startfreq in THz
        stopfreq = freq + self.bandwidth * 0.5 * 1e-3  # stropfreq in THz

        for frequency in np.arange(191.250, 196.274, 0.001, dtype=float):
            for k in range(1):
                if self.wavelength[k] > 1 and startfreq[k] < frequency < stopfreq[k]:
                    profiletext = profiletext + "%.3f\t%.1f\t%.1f\t%d\n" % (
                        frequency, self.attenuation[k], self.phase[k], k + 1)
                else:
                    profiletext = profiletext + "%.3f\t60.0\t0.0\t0\n" % frequency

        rc = wsapi.ws_load_profile(self.name, profiletext)
        if rc < 0:
            print(wsapi.ws_get_result_description(rc))

        # return(profiletext)

    def execute_wss(self, profile):
        """
        Load the desired profile according to the specifications

        """
        profiletext = ""

        for frequency in np.arange(191.250, 196.274, 0.001, dtype=float):
            profiletext = profiletext + "%.3f\t%.1f\t%.1f\t%d\n" % (frequency, profile, 0, 1)

        rc = wsapi.ws_load_profile(self.name, profiletext)

        if rc < 0:
            print(wsapi.ws_get_result_description(rc))

        # return(profiletext)

    def check_profile(self):
        """
        Check the loaded profile

        :return: bandwidth and attenuation checked
        """
        profiletext = ""
        check_BW_wss = 0
        check_att = []
        for frequency in np.arange(191.250, 196.274, 0.001, dtype=float):
            for k in range(1):
                profiletext = profiletext + "%.3f\t60.0\t0.0\t0\n" % frequency

        rc = wsapi.ws_get_profile(self.name, profiletext, len(profiletext))
        # TODO ws_get_profile not implemented
        if rc < 0:
            print(wsapi.ws_get_result_description(rc))

        profiletext_out = profiletext.split("\n")
        profile_wss = np.array(np.zeros(len(profiletext_out) * 4))
        profile_wss = profile_wss.reshape((len(profiletext_out), 4))
        for index in range(0, len(profiletext_out) - 1):
            profile_wss[index] = profiletext_out[index].split("\t")

        # print profile_wss[0]
        profile_wss = profile_wss[0:len(profile_wss) - 1, :]
        # peakind = (profile_wss[:, 1] == self.attenuation[0]).nonzero()
        # La funcio nonzero() aixi no existeix. He fer servir la de numpy
        peakind = np.nonzero(profile_wss[:, 1] == self.attenuation[0])
        # print profile_wss[2138]

        if not peakind:
            data = profile_wss[peakind]
            check_BW_wss = (data[-1, 0] - data[0, 0]) * 1e3  # in GHz
            check_att = data[:, 1]

            figure()
            plot(profile_wss[:, 0], profile_wss[:, 1])
            show()

        else:
            print('Error: All the attenuation values are set to 60dB')  # No ha llegit el perfil del wss ha agafat
            # l'inicial que hem creat

        return check_BW_wss, check_att


if __name__ == '__main__':
    # edfa = manlight()
    # edfa.test()
    # edfa.status(False)
    # edfa.mode("AGC", 30)
    # edfa.close()
    wavelength = 1550.12  # wavelength (nm)
    wstx = Wss("wstx", "SN042561.wsconfig")
    wstx.open()
    wstx.attenuation[0] = 0.0
    wstx.phase[0] = 0.0
    wstx.bandwidth[0] = 25
    wstx.wavelength[0] = wavelength
    wstx.execute()
    time.sleep(1)
    [BW_wss, read_att] = wstx.check_profile()
    print('Bw', BW_wss)
    wstx.close()
