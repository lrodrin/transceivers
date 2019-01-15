import numpy as np
import scipy.signal as sgn

import lib.constellationV2 as modulation
import lib.ofdm as ofdm

METRO_DAC_INPUTS_ENABLE_TXT = "metro_dac_inputs_enable.txt"

SLEEP_TIME = 100

LOADING_ALGORITHM = 'LCRA_QAM'

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat> and Laia Nadal <laia.nadal@cttc.cat> "
__copyright__ = "Copyright 2018, CTTC"


class DAC:
    """
    This is a class for DAC configuration.

    """

    def __init__(self, trx_mode, tx_ID):
        """
        The constructor for DAC class.
        Define and initialize the DAC default parameters:
            - Preemphasis.
            - gapdB
            - loading_algorithm
            - Number of carriers.
            - Constellation.
            - Bits per symbol.
            - Cyclic prefix.
            - Number of training symbols.
            - BER[kosnr]No. of symbols without TS.
            - No. of symbols with TS.
            - No of OFDM symbols / frames
            - Samples per symbol.
            - Sampling frequency DAC

        :param trx_mode: Identify the mode of a transceiver (0 for METRO_1 scenario or 1 for METRO_2 scenario)
        :param tx_ID: Identify the channel of the DAC to be used and the local files to use for storing data.
        :type trx_mode: int
        :type tx_ID: int
        """
        self.trx_mode = trx_mode
        self.tx_ID = tx_ID
        self.Preemphasis = 'True'
        # Algorithm parameters
        self.gapdB = 9.8
        self.Loading_algorithm = LOADING_ALGORITHM
        # Parameters for the OFDM signal definition
        self.Ncarriers = 512
        self.constellation = "QAM"
        self.bps = 2
        self.CP = 0.019
        self.NTS = 4
        self.Nsymbols = 16 * 3 * 1024
        self.NsymbolsTS = self.Nsymbols + self.NTS * self.Ncarriers
        self.Nframes = self.NsymbolsTS / self.Ncarriers
        self.sps = 3.2
        self.fs = 64e9

    def transmitter(self, SNR_estimation):
        """

        :param SNR_estimation: SNR estimation.
        :type SNR_estimation: bool
        :return: 0
        """
        Niterations = 10  # Number of iterations
        SNRT = np.zeros((self.Ncarriers,), dtype=float)
        SNR_in = np.empty((self.Ncarriers,), dtype=float)
        e_fec = np.true_divide(7, 100)  # FEC overhead

        BWs = self.fs / self.sps  # BW electrical signal
        print('Signal bandwidth:', BWs / 1e9, 'GHz')

        if not SNR_estimation:
            print('Implementing loading algorithm...')
            gap = 10 ** (self.gapdB / 10.)
            if self.tx_ID == 0:
                SNR_in = np.load('ChannelGain.npy')
            else:
                SNR_in = np.load('ChannelGain2.npy')

            Load = ofdm.Loading(self.Ncarriers, BWs)
            if self.Loading_algorithm == 'LCMA_QAM':
                BitRate = 20e9
                (En, bn) = Load.LCMA_QAM(gap, BitRate / float(BWs), SNR_in)
            if self.Loading_algorithm == 'LCRA_QAM':
                (En, bn, BitRate) = Load.LCRA_QAM(gap, SNR_in)

            bps = np.sum(bn) / float(len(bn))

        else:
            bn = self.bps * np.ones(self.Ncarriers) # bn[240:240+30] = np.zeros(30)
            bps = np.sum(bn) / float(len(bn))
            BitRate = BWs * bps  # Net data rate

        print('BitRate=', BitRate / 1e9, 'Gb/s', 'BW=', BWs / 1e9, 'GHz')
        # plt.plot(bn)
        # plt.show()

        fc = BWs / 2
        BitStream = np.ma.empty(self.NsymbolsTS * bps)  # Initialize BitStream
        ttime = (1 / self.fs) * np.ones((self.sps * self.Nframes * (self.Ncarriers + np.round(self.CP * self.Ncarriers)),))
        ttt = ttime.cumsum()

        if self.tx_ID == 0:
            np.random.seed(42)
        else:
            np.random.seed(36)

        data = np.random.randint(0, 2, bps * self.Nsymbols)
        TS = np.random.randint(0, 2, self.NTS * bps * self.Ncarriers)
        BitStream = np.array(np.zeros(self.Nframes * np.sum(bn)), int)
        BitStream = np.r_[TS, data]
        BitStream = BitStream.reshape((self.Nframes, np.sum(bn)))
        cdatar = np.array(np.zeros((self.Nframes, self.Ncarriers)), complex)

        cumBit = 0
        for k in range(0, self.Ncarriers):
            (FormatM, bitOriginal) = modulation.Format(self.constellation, bn[k])
            cdatar[:, k] = modulation.Modulator(BitStream[:, cumBit:cumBit + bn[k]], FormatM, bitOriginal, bn[k])
            cumBit = cumBit + bn[k]

        if SNR_estimation == 'False':  # Power loading
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
        # k_clip=3.16 # 256QAM
        # k_clip=2.66 # optimum for 32QAM
        k_clip = 2.8  # optimum for 64QAM
        Cx_clip = Cx.clip(min=-k_clip * deviation, max=k_clip * deviation)

        # resample
        Cx_up = sgn.resample(Cx_clip, self.sps * Cx_clip.size)

        # print G+ 'Upconversion...'
        Cx_up2 = Cx_up.real * np.cos(2 * np.math.pi * fc * ttt) + Cx_up.imag * np.sin(2 * np.math.pi * fc * ttt)

        if self.Preemphasis == 'True':
            print('preemphasis...')
            # Pre-emphasis (inverted gaussian) filter
            BW = 25e9
            # BW=20e9;
            n = 2
            sigma = BW / (2 * np.sqrt(2 * np.log10(2)))
            stepfs = self.fs / len(Cx_up2)
            freq1 = np.arange(stepfs, self.fs / 2 - stepfs, stepfs)
            freq2 = np.arange(-self.fs / 2, 0, stepfs)
            freq = np.r_[freq1, 0, freq2, self.fs / 2 - stepfs]
            emphfilt = np.exp(.5 * np.abs(freq / sigma) ** n) # Just a gaussian filter inverted
            Cx_up2 = np.real(np.fft.ifft(emphfilt * np.fft.fft(Cx_up2)))

        Qt = 255  # Quantization steps
        Cx_bias = Cx_up2 - np.min(Cx_up2)
        Cx_LEIA = np.around(Cx_bias / np.max(Cx_bias) * Qt - np.ceil(Qt / 2))  # Signal to download to LEIA_DAC
        Cx_bias_up = Cx_up - np.min(Cx_up)
        Cx_up = np.around(Cx_bias_up / np.max(Cx_bias_up) * Qt - np.ceil(Qt / 2))

        print('Initializing LEIA...')
        f = open("CLK.txt", "w")
        f.write("2.0\n")  # freq. synth. control [GHz] (60GS/s--> 1.87, 64GS/s--->2GHz)
        f = open("CLK_ref.txt", "w")
        f.write("10\n")  # 10MHz or 50MHz Ref frequency
        np.savetxt(METRO_DAC_INPUTS_ENABLE_TXT, Cx_LEIA)  # .txt with the OFDM signal

        if self.tx_ID == 0:
            np.save('params_tx', (bn, cdatar, data, Cx_up, Cx_up2))
        else:
            np.save('params_tx2', (bn, cdatar, data, Cx_up, Cx_up2))

        return 0


if __name__ == '__main__':
    # TODO create a main test
    # configuration 1a scenario (METRO_, OpenConfig client)
    trx_mode = 0
    tx_ID = 0
    tx = DAC(trx_mode, tx_ID)
    ack = tx.transmitter(True)
    print('ACK= ', ack)
