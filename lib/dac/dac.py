"""This is the DAC module.

This module does stuff.
"""
import numpy as np
import scipy.signal as sgn

import lib.constellationV2 as modulation
import lib.ofdm as ofdm

# TODO import logging


class DAC:
    """
    This is the class for DAC module.
    """
    clock_ref_file = "CLK_ref.txt"  # TODO moure a carpeta X els fitxers txt
    clock_file = "CLK.txt"
    temp_file = "TEMP.txt"
    sleep_time = 130

    SNR_estimation = False  # TODO passar com a param
    preemphasis = True
    BW_filter = 25e9
    N_filter = 2
    gapdB = 9.6
    loading_algorithm = 'LCRA_QAM'
    Ncarriers = 512
    constellation = 'QAM'
    CP = 0.019
    NTS = 4
    Nsymbols = 16 * 3 * 1024
    sps = 3.2
    fs = 64e9
    k_clip = 2.8
    Qt = 255
    Niters = 10

    # def __init__(self, trx_mode, tx_ID, FEC, bps, pps):
    #     """
    #     The constructor for the DAC class.
    #
    #     :param trx_mode: (0 or 1), for identifying the mode of the transceiver: 0 for estimation mode and 1 for
    #     transmission mode.
    #     :type trx_mode: int
    #     :param tx_ID: Identify the channel of the DAC to be used and the local files to use for storing data.
    #     :type tx_ID: int
    #     :param FEC: (HD-FEC, SD-FEC), in order to identifiy the channel encoding to be used (TBI).
    #     :type FEC: string
    #     :param bps: array of 512 positions. It contains the bits per symbol per subcarrier.
    #     :type bps:int array
    #     :param pps: array of 512 positions. It contains the power per subcarrier figure.
    #     :type pps: float array
    #     """
    #     self.trx_mode = trx_mode
    #     self.tx_ID = tx_ID
    #     self.FEC = FEC
    #     # self.bps = 2
    #     self.bps = bps
    #     self.pps = pps
    #     self.initialization()

    def __init__(self):
        """
        Define and initialize the DAC default parameters:

            - SNR_estimation (str): ?
            - preemphasis (str): ?
            - Preemphasis parameters:
                - BW_filter (int): Set preemphasis filter bandwidth.
                - N_filter (int): Set preemphasis filter order.

            - Loading algorithm parameters:
                - gapdB (float): Set SNR gap.
                - loading_algorithm (str): Set loading algorithm type (e.g. LC_RA or LC_MA).

            - Parameters for the OFDM signal definition:
                - Ncarriers (int): Set number of carriers.
                - constellation (str): Set QAM.
                - CP (float): Set cyclic prefix.
                - NTS (int): Set number of training symbols.
                - Nsymbols (float): Set number of symbols without TS.
                - NsymbolsTS (float): Set number of symbols with TS.
                - Nframes (float): Set number of OFDM symbols/frames.
                - sps (float): Set samples per symbol.
                - fs (int): Set sampling frequency.
                - k_clip (float): Set clipping level.
                    - 3.16 optimum for 256QAM.
                    - 2.66 optimum for 32QAM.
                    - 2.8 optimum for 64QAM.
                - Qt (int): Set LEIA Quantization steps.
        """
        self.SNR_estimation = DAC.SNR_estimation
        self.preemphasis = DAC.preemphasis

        # Preemphasis parameters
        self.BW_filter = DAC.BW_filter
        self.N_filter = DAC.N_filter

        # loading_algorithm parameters
        self.gapdB = DAC.gapdB
        self.loading_algorithm = DAC.loading_algorithm

        # Parameters for the OFDM signal definition
        self.Ncarriers = DAC.Ncarriers
        self.constellation = DAC.constellation
        self.CP = DAC.CP
        self.NTS = DAC.NTS
        self.Nsymbols = DAC.Nsymbols
        self.NsymbolsTS = self.Nsymbols + self.NTS * self.Ncarriers
        self.Nframes = self.NsymbolsTS / self.Ncarriers
        self.sps = DAC.sps
        self.fs = DAC.fs
        self.k_clip = DAC.k_clip
        self.Qt = DAC.Qt
        self.Niters = DAC.Niters

    def transmitter(self, trx_mode, tx_ID, FEC, bps, pps):
        """
        Generate a multi BitStream and creates the OFDM signal to be uploaded into the DAC. It also implements
        bit/power loading_algorithm.

        :param trx_mode: Identify the mode of the transceiver. 0 for estimation mode and 1 for transmission mode.
        :type trx_mode: int
        :param tx_ID: Identify the channel of the DAC to be used and the local files to use for storing data.
        :type tx_ID: int
        :param FEC: HD-FEC or SD-FEC). Identify the channel encoding to be used (TBI).
        :type FEC: str
        :param bps: Array of 512 positions that contains the bits per symbol per subcarrier.
        :type bps:int array
        :param pps: Array of 512 positions that contains the power per subcarrier figure.
        :type pps: float array
        """
        BWs = self.fs / self.sps  # BW electrical signal
        print('Signal bandwidth:', BWs / 1e9, 'GHz')

        if trx_mode == 0 or trx_mode == 1:
            BitRate = 0
            En = np.array(np.zeros(self.Ncarriers))
            bn = np.array(np.zeros(self.Ncarriers))
            if not self.SNR_estimation:
                print('Implementing loading algorithm...')
                gap = 10 ** (self.gapdB / 10.)
                if tx_ID == 0:
                    SNR_in = np.load('ChannelGain.npy')  # TODO link to file
                else:
                    SNR_in = np.load('ChannelGain2.npy')  # TODO link to file

                Load = ofdm.Loading(self.Ncarriers, BWs)
                if self.loading_algorithm == 'LCMA_QAM':
                    BitRate = 20e9
                    (En, bn) = Load.LCMA_QAM(gap, BitRate / float(BWs), SNR_in)
                if self.loading_algorithm == 'LCRA_QAM':
                    (En, bn, BitRate) = Load.LCRA_QAM(gap, SNR_in)
                bps = np.sum(bn) / float(len(bn))
                self.Niters = 5

            else:
                bn = bps * np.ones(self.Ncarriers)  # bn[240:240+30] = np.zeros(30)
                bps = np.sum(bn) / float(len(bn))
                BitRate = BWs * bps  # Net data rate
            print('BitRate = ', BitRate / 1e9, 'Gb/s', 'BW = ', BWs / 1e9, 'GHz')

        elif trx_mode == 2:
            bn = bps
            En = pps

        fc = BWs / 2
        ttime = (1 / self.fs) * np.ones(
            (self.sps * self.Nframes * (self.Ncarriers + np.round(self.CP * self.Ncarriers)),))
        ttt = ttime.cumsum()

        if tx_ID == 0:
            np.random.seed(42)
        else:
            np.random.seed(36)

        data = np.random.randint(0, 2, bps * self.Nsymbols)
        TS = np.random.randint(0, 2, self.NTS * bps * self.Ncarriers)
        # BitStream = np.array(np.zeros(self.Nframes * np.sum(bn)), int)
        BitStream = np.r_[TS, data]
        BitStream = BitStream.reshape((self.Nframes, np.sum(bn)))
        cdatar = np.array(np.zeros((self.Nframes, self.Ncarriers)), complex)

        cumBit = 0
        for k in range(0, self.Ncarriers):
            (FormatM, bitOriginal) = modulation.Format(self.constellation, bn[k])
            cdatar[:, k] = modulation.Modulator(BitStream[:, cumBit:cumBit + bn[k]], FormatM, bitOriginal, bn[k])
            cumBit = cumBit + bn[k]

        if not self.SNR_estimation:  # Power loading
            cdatary = cdatar * np.sqrt(En)
        else:
            cdatary = cdatar

        FHTdatatx = ofdm.ifft(cdatary, self.Ncarriers)
        # Add cyclic prefix
        FHTdata_cp = np.concatenate((FHTdatatx, FHTdatatx[:, 0:np.round(self.CP * self.Ncarriers)]), axis=1)
        # Serialize
        Cx = FHTdata_cp.reshape(FHTdata_cp.size, )
        # print 'Clipping the signal...'
        deviation = np.std(Cx)
        Cx_clip = Cx.clip(min=-self.k_clip * deviation, max=self.k_clip * deviation)
        # Resample
        Cx_up = sgn.resample(Cx_clip, self.sps * Cx_clip.size)
        # print G+ 'Upconversion...'
        Cx_up2 = Cx_up.real * np.cos(2 * np.math.pi * fc * ttt) + Cx_up.imag * np.sin(2 * np.math.pi * fc * ttt)

        if self.preemphasis:
            print('preemphasis...')
            # Pre-emphasis (inverted gaussian) filter
            sigma = self.BW_filter / (2 * np.sqrt(2 * np.log10(2)))
            stepfs = self.fs / len(Cx_up2)
            freq1 = np.arange(stepfs, self.fs / 2 - stepfs, stepfs)
            freq2 = np.arange(-self.fs / 2, 0, stepfs)
            freq = np.r_[freq1, 0, freq2, self.fs / 2 - stepfs]
            emphfilt = np.exp(.5 * np.abs(freq / sigma) ** self.N_filter)  # Just a Gaussian filter inverted
            Cx_up2 = np.real(np.fft.ifft(emphfilt * np.fft.fft(Cx_up2)))

        Cx_bias = Cx_up2 - np.min(Cx_up2)
        Cx_LEIA = np.around(
            Cx_bias / np.max(Cx_bias) * self.Qt - np.ceil(self.Qt / 2))  # Signal to download to LEIA_DAC
        Cx_bias_up = Cx_up - np.min(Cx_up)
        Cx_up = np.around(Cx_bias_up / np.max(Cx_bias_up) * self.Qt - np.ceil(self.Qt / 2))

        print('Initializing LEIA...')
        f = open(DAC.clock_file, "w")
        f.write("2.0\n")  # freq. synth. control [GHz] (60GS/s--> 1.87, 64GS/s--->2GHz)
        f = open(DAC.clock_ref_file, "w")
        f.write("10\n")  # 10MHz or 50MHz Ref frequency
        np.savetxt(DAC.temp_file, Cx_LEIA)  # .txt with the OFDM signal

        if tx_ID == 0:
            np.save('params_tx', (bn, cdatar, data, Cx_up, Cx_up2))
        else:
            np.save('params_tx2', (bn, cdatar, data, Cx_up, Cx_up2))
