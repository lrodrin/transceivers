"""This is the DAC module.
"""
import logging
from subprocess import Popen, PIPE

import numpy as np
import scipy.signal as sgn

import lib.constellationV2 as modulation
import lib.ofdm as ofdm

logger = logging.getLogger("DAC")
logger.addHandler(logging.NullHandler())


class DAC:
    """
    This is the class for DAC module.
    """
    folder = "C:/Users/cttc/Desktop/agent-bvt/conf/"  # Folder that stores all the configuration files
    clock_ref_file = folder + "CLK_ref.txt"  # File to save the clock_ref for the DAC
    clock_file = folder + "CLK.txt"  # File to save the clock value for the DAC
    temp_file = folder + "TEMP.txt"  # File to save the OFDM signal that will be uploaded to LEIA DAC
    leia_up_filename = "Leia_DAC_up.m"  # File with the generated OFDM signal to be uploaded to the LEIA DAC
    leia_down_filename = "Leia_DAC_dowm.m"  # File with the generated OFDM signal to be uploaded to the LEIA DAC

    Preemphasis = True
    BW_filter = 25e9
    N_filter = 2
    Ncarriers = 512
    Constellation = "QAM"
    CP = 0.019
    NTS = 4
    Nsymbols = 16 * 3 * 1024
    sps = 3.2
    fs = 64e9
    k_clip = 2.8
    Qt = 255
    bps = 2

    def __init__(self):
        """
        The constructor for the DAC class.
        Define and initialize the DAC default parameters:

            - Preemphasis (bool): Enable preemphasis.
            - BW_filter (int): Set bandwidth of the preemphasis filter.
            - N_filter (int): Set order of the preemphasis filter.
            - Ncarriers (int): Set number of carriers.
            - Constellation (str): Set modulation format.
            - CP (float): Set cyclic prefix.
            - NTS (int): Set number of training symbols.
            - Nsymbols (int): Set number of generated symbols.
            - NsymbolsTS (int): Set number of generated symbols without TS.
            - Nframes (int): Set number of OFDM frames.
            - sps (float): Set samples per symbol for the DAC.
            - fs (int): Set DAC frequency sampling.
            - k_clip (float): Set factor for clipping the OFDM signal.
                - 3.16 optimum for 256 QAM.
                - 2.66 optimum for 32 QAM.
                - 2.8 optimum for 64 QAM.
            - Qt (int): Set quantization steps.
            - bps (int): Set number of bits per symbol.
            - BWs (int): Set bandwidth of electrical signal.
        """
        self.Preemphasis = DAC.Preemphasis

        # Preemphasis parameters
        self.BW_filter = DAC.BW_filter
        self.N_filter = DAC.N_filter

        # Parameters for the OFDM signal definition
        self.Ncarriers = DAC.Ncarriers
        self.Constellation = DAC.Constellation
        self.CP = DAC.CP
        self.NTS = DAC.NTS
        self.Nsymbols = DAC.Nsymbols
        self.NsymbolsTS = self.Nsymbols + self.NTS * self.Ncarriers
        self.Nframes = self.NsymbolsTS / self.Ncarriers
        self.sps = DAC.sps
        self.fs = DAC.fs
        self.k_clip = DAC.k_clip
        self.Qt = DAC.Qt
        self.bps = DAC.bps
        self.BWs = self.fs / self.sps

    def transmitter(self, dac_out, bn, En):
        """
        Generate a BitStream and creates the OFDM signal to be uploaded into the DAC.

        :param dac_out: input port
        :type dac_out: int
        :param bn: array of Ncarriers positions that contains the bits per symbol per subcarrier
        :type bn: int array of 512 positions
        :param En: array of Ncarriers positions that contains the power per subcarrier figure
        :type En: float array of 512 positions
        """
        try:
            f_clock = self.BWs / 2
            tt = (1 / self.fs) * np.ones(
                (self.sps * self.Nframes * (self.Ncarriers + np.round(self.CP * self.Ncarriers)),))
            ttt = tt.cumsum()

            logger.debug("Generating data")  # Generate data with different seed for the different users/clients
            if dac_out % 2 != 0:  # TODO Esta be?
                np.random.seed(36)
            elif dac_out % 2 == 0:
                np.random.seed(42)

            data = np.random.randint(0, 2, self.bps * self.Nsymbols)

            logger.debug("Trainning symbols")
            TS = np.random.randint(0, 2, self.NTS * self.bps * self.Ncarriers)
            BitStream = np.r_[TS, data]
            BitStream = BitStream.reshape((self.Nframes, np.sum(bn)))
            cdatar = np.array(np.zeros((self.Nframes, self.Ncarriers)), complex)

            logger.debug("Mapping data")
            cumBit = 0
            for k in range(0, self.Ncarriers):
                (FormatM, bitOriginal) = modulation.Format(self.Constellation, bn[k])
                cdatar[:, k] = modulation.Modulator(BitStream[:, cumBit:cumBit + bn[k]], FormatM, bitOriginal, bn[k])
                cumBit = cumBit + bn[k]

            cdatary = cdatar * np.sqrt(En)  # Include power loading results
            logger.debug("Implementing the IFFT")
            FHTdatatx = ofdm.ifft(cdatary, self.Ncarriers)  # Perform the IFFT required in OFDM
            logger.debug("Add cyclic prefix")
            FHTdata_cp = np.concatenate((FHTdatatx, FHTdatatx[:, 0:np.round(self.CP * self.Ncarriers)]), axis=1)

            Cx = FHTdata_cp.reshape(FHTdata_cp.size, )  # Serialize
            logger.debug("Clipping the signal")
            deviation = np.std(Cx)
            Cx_clip = Cx.clip(min=-self.k_clip * deviation, max=self.k_clip * deviation)
            Cx_up = sgn.resample(Cx_clip, self.sps * Cx_clip.size)  # Resample
            Cx_up2 = Cx_up.real * np.cos(2 * np.math.pi * f_clock * ttt) + Cx_up.imag * np.sin(
                2 * np.math.pi * f_clock * ttt)  # Upconvert the signal to create a real signal

            if self.Preemphasis:
                logger.debug("Preemphasis")
                # Pre-emphasis (inverted gaussian) filter
                sigma = self.BW_filter / (2 * np.sqrt(2 * np.log10(2)))
                stepfs = self.fs / len(Cx_up2)
                freq1 = np.arange(stepfs, self.fs / 2 - stepfs, stepfs)
                freq2 = np.arange(-self.fs / 2, 0, stepfs)
                freq = np.r_[freq1, 0, freq2, self.fs / 2 - stepfs]
                emphfilt = np.exp(.5 * np.abs(freq / sigma) ** self.N_filter)  # Just a Gaussian filter inverted
                Cx_up2 = np.real(np.fft.ifft(emphfilt * np.fft.fft(Cx_up2)))

            Cx_bias = Cx_up2 - np.min(Cx_up2)
            # Quantize the OFDM signal
            Cx_LEIA = np.around(
                Cx_bias / np.max(Cx_bias) * self.Qt - np.ceil(self.Qt / 2))  # Signal to download to LEIA

            logger.debug("OFDM signal is created")

            logger.debug("Initializing LEIA")
            f_clock = open(self.clock_file, "w")
            f_clock.write("2.0\n")  # freq. synth. control [GHz] (60GS/s--> 1.87, 64GS/s--->2GHz)
            f_clock_ref = open(self.clock_ref_file, "w")
            f_clock_ref.write("10\n")  # 10MHz or 50MHz Ref frequency
            np.savetxt(self.temp_file, Cx_LEIA)  # .txt with the OFDM signal

            self.enable_channel(dac_out)

        except Exception as error:
            logger.error("DAC transmitter method, {}".format(error))

    def enable_channel(self, dac_out):
        """
        Enable the DAC channel. Sets 1 to the active Leia output and 0 to the remaining outputs.

        :param dac_out: input port
        :type dac_out: int
        """
        seq = ""
        leia_file = ""
        try:
            temp_file = open(self.temp_file, "w")
            if dac_out % 2 != 0:
                logger.debug("Enable Hi channel")
                seq = "1\n 0\n 0\n 0\n"  # Hi_en, Hq_en, Vi_en, Vq_en
                leia_file = self.leia_up_filename

            elif dac_out % 2 == 0:
                logger.debug("Enable Hq channel")
                seq = "0\n 1\n 0\n 0\n"  # Hi_en, Hq_en, Vi_en, Vq_en
                leia_file = self.leia_down_filename

            temp_file.write(seq)
            self.execute_matlab(leia_file)

        except Exception as error:
            logger.error("DAC enable_channel method, {}".format(error))

    def execute_matlab(self, leia_file):
        """
        Call MATLAB program to process the OFDM signal uploaded to the Leia DAC.

        :param leia_file: file with the generated OFDM signal to be uploaded to the LEIA DAC
        :type leia_file: str    (Leia_DAC_up.m or Leia_DAC_down.m)
        """
        matlab = 'C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe'
        options = '-nodisplay -nosplash -nodesktop -wait'
        try:
            command = """{} {} -r "cd(fullfile('{}')), {}" """.format(matlab, options, self.folder, leia_file)
            proc = Popen(command, stdout=PIPE, stderr=PIPE)
            out, err = proc.communicate()
            if proc.returncode == 0:
                logger.debug("MATLAB call {} succeeded, exit-code = {} returned".format(command, proc.returncode))
            else:
                logger.error(
                    "MATLAB call {} failed, exit-code = {} returned, error = {}".format(command, proc.returncode,
                                                                                        str(err)))
        except OSError as error:
            logger.error("Failed to execute MATLAB, error = %s" % error)
