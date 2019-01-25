import numpy as np
import scipy.signal as sgn

import lib.constellationV2 as modulation
import lib.ofdm as ofdm

CLOCK_REF_FILE = "CLK_ref.txt"
CLOCK_FILE = "CLK.txt"
DAC_INPUTS_ENABLE_FILE = "TEMP.txt"
SLEEP_TIME = 100


# TODO error control


class DAC:
    """
    This is a class for DAC configuration.

    """

    def __init__(self, trx_mode, tx_ID, FEC, bps, pps):
        """
        The constructor for DAC class.

        Define and initialize the DAC default parameters:

            - name: SNR_estimation.
              description:
              type: string
            - name: gapdB.
              description: SNR gap.
              type: float
            - name: Loading_algorithm.
              description: LC_RA or LC_MA.
              type: string
            - name: Preemphasis
              description:
                    - name: BW_filter
                      description: Preemphasis filter bandwidth.
                      type: int
                    - name: N_filter
                      description: Preemphasis filter order.
                      type: int
              type:
            - name: Ncarriers.
              description: Number of carriers.
              type: int
            - name: Constellation.
              description: QAM.
              type: string
            - name: CP.
              description: Cyclic prefix.
              type: float
            - name: NTS.
              description: Number of training symbols.
              type: int
            - name: Nsymbols.
              description: Number of symbols without TS.
              type: int
            - name: NsymbolsTS.
              description: Number of symbols with TS.
              type: int
            - name: Nframes.
              description: Number of OFDM symbols/frames.
              type: int
            - name: sps.
              description: Samples per symbol.
              type: float
            - name: fs.
              description: Sampling frequency DAC.
              type: int
            - name: k_clip.
              description: Clipping level.
                - 3.16 optimum for 256QAM.
                - 2.66 optimum for 32QAM.
                - 2.8 optimum for 64QAM.
              type: float
            - name: Qt.
              description: LEIA Quantization steps.
              type: int

        :param trx_mode: (0 or 1), for identifying the mode of the transceiver: 0 for estimation mode and 1 for
        transmission mode.
        :param tx_ID: Identify the channel of the DAC to be used and the local files to use for storing data.
        :param FEC: (HD-FEC, SD-FEC), in order to identifiy the channel encoding to be used (TBI).
        :param bps: array of 512 positions. It contains the bits per symbol per subcarrier.
        :param pps: array of 512 positions. It contains the power per subcarrier figure.
        :type trx_mode: int
        :type tx_ID: int
        :type FEC: string
        :type bps:int array
        :type pps: float array
        
        
        """
        self.trx_mode = trx_mode
        self.tx_ID = tx_ID
        self.FEC = FEC
        self.bps = bps
        self.pps = pps

        self.SNR_estimation = 'True'
        self.Preemphasis = 'True'

        # Preemphasis parameters
        self.BW_filter = 25e9
        self.N_filter = 2
        # Loading_algorithm parameters
        self.gapdB = 9.8
        self.Loading_algorithm = 'LCRA_QAM'

        # Parameters for the OFDM signal definition
        self.Ncarriers = 512
        self.constellation = 'QAM'
        # self.bps = 2
        self.CP = 0.019
        self.NTS = 4
        self.Nsymbols = 16 * 3 * 1024
        self.NsymbolsTS = self.Nsymbols + self.NTS * self.Ncarriers
        self.Nframes = self.NsymbolsTS / self.Ncarriers
        self.sps = 3.2
        self.fs = 64e9
        self.k_clip = 2.8
        self.Qt = 255

    def transmitter(self):
        """
        Generate a multi BitStream and creates the OFDM signal to be uploaded into the DAC. It also implements
        bit/power Loading_algorithm.

        """
        BWs = self.fs / self.sps  # BW electrical signal
        print('Signal bandwidth:', BWs / 1e9, 'GHz')

        BitRate = 0
        En = np.array(np.zeros(self.Ncarriers))
        bn = np.array(np.zeros(self.Ncarriers))
        if not self.SNR_estimation:
            print('Implementing loading algorithm...')
            gap = 10 ** (self.gapdB / 10.)
            if self.tx_ID == 0:
                SNR_in = np.load('ChannelGain.npy')  # TODO link to file
            else:
                SNR_in = np.load('ChannelGain2.npy')  # TODO link to file

            Load = ofdm.Loading(self.Ncarriers, BWs)
            if self.Loading_algorithm == 'LCMA_QAM':
                BitRate = 20e9
                (En, bn) = Load.LCMA_QAM(gap, BitRate / float(BWs), SNR_in)
            if self.Loading_algorithm == 'LCRA_QAM':
                (En, bn, BitRate) = Load.LCRA_QAM(gap, SNR_in)
            bps = np.sum(bn) / float(len(bn))

        else:
            bn = self.bps * np.ones(self.Ncarriers)  # bn[240:240+30] = np.zeros(30)
            bps = np.sum(bn) / float(len(bn))
            BitRate = BWs * bps  # Net data rate
        print('BitRate = ', BitRate / 1e9, 'Gb/s', 'BW = ', BWs / 1e9, 'GHz')

        fc = BWs / 2
        ttime = (1 / self.fs) * np.ones(
            (self.sps * self.Nframes * (self.Ncarriers + np.round(self.CP * self.Ncarriers)),))
        ttt = ttime.cumsum()

        if self.tx_ID == 0:
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

        if self.SNR_estimation == 'False':  # Power loading
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

        if self.Preemphasis == 'True':
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
        f = open(CLOCK_FILE, "w")
        f.write("2.0\n")  # freq. synth. control [GHz] (60GS/s--> 1.87, 64GS/s--->2GHz)
        f = open(CLOCK_REF_FILE, "w")
        f.write("10\n")  # 10MHz or 50MHz Ref frequency
        np.savetxt(DAC_INPUTS_ENABLE_FILE, Cx_LEIA)  # .txt with the OFDM signal

        if self.tx_ID == 0:
            np.save('params_tx', (bn, cdatar, data, Cx_up, Cx_up2))
        else:
            np.save('params_tx2', (bn, cdatar, data, Cx_up, Cx_up2))
