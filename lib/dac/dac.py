import os
import time

import numpy as np
import scipy.signal as sgn

import lib.constellationV2 as modulation
import lib.ofdm as of

METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN = '"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash ' \
                                           '-nodesktop -r '"Leia_DAC_down; "

METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_UP = '"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash ' \
                                         '-nodesktop -r '"Leia_DAC_up; "
TEMP_TXT = 'TEMP.txt'

LEIA_DAC_DOWN = "Leia_DAC_down"

LEIA_DAC_UP = "Leia_DAC_up"

SLEEP_TIME = 100

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat> and Laia Nadal <laia.nadal@cttc.cat> "
__copyright__ = "Copyright 2018, CTTC"


class DAC:
    """
    This is a class for DAC configuration.

    """

    def __init__(self, trx_mode, tx_ID):
        """
        The constructor for DAC class.

        :param trx_mode: Identify the mode of a transceiver (0 for METRO_1 scenario or 1 for METRO_2 scenario)
        :param tx_ID: Identify the channel of the DAC to be used and the local files to use for storing data.
        :type trx_mode: int
        :type tx_ID: int
        """
        self.trx_mode = trx_mode
        self.tx_ID = tx_ID

    def mode(self):
        # TODO posar la logica al flask_server.py i esborrar el metode
        """
        Sets the operational mode for a channel.

            - Configuration 1a:
                - To demonstrate bidirectionality.
                - Simple scheme: An OpenConfig terminal device comprises BVTx+BVTRx of a single client.

            - Configuration 1b:
                - The S-BVT architecture is used for a single client creating a superchannel.
                - Up to 2 slices can be enabled to increase data rate according to the bandwith requirements.
                - The superchannel central wavelength is configured/set by the OpenConfig agent.

            - Configuration 2:
                - The S-BVT consist of 2 clients (C1 and C2) that are part of a single OpenConfig terminal device.
                - There is another S-BVT with 2 more clients (C3, C4) or a BVT with a single client C3 at another point
                  of the network that corresponds to another OpenConfig terminal.
                - The superchannel central wavelength is configured/set by the OpenConfig agent.
                - Two clients are assigned to a single optical channel, corresponding to two logical optical channels.
                - We can not demonstrate bidirectionality due to hardware limitations.

        :return: ACK (0 or -1). 0 for OK and -1 in case there is some error.
        :rtype: int
        """
        global ACK
        file = open("Inputs_enable.txt", "w")
        file_uploaded_message = 'Leia initialized and SPI file uploaded'
        if self.trx_mode == 0:  # Configuration 1
            self.transmitter()
            if self.tx_ID == 0:  # Configuration 1a
                file.write("1\n 0\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_UP)  # MATLAB call with file Leia_DAC_up.m
            else:  # Configuration 1b
                file.write("0\n 1\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN)  # MATLAB call with file Leia_DAC_down.m

            time.sleep(SLEEP_TIME)
            print(file_uploaded_message)
            ACK = 0

        elif self.trx_mode == 1:  # Configuration 2
            # self.tx_ID = 0
            self.transmitter()
            file.write("1\n 0\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
            os.system(METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_UP)  # MATLAB call with file Leia_DAC_up.m
            time.sleep(SLEEP_TIME)
            print(file_uploaded_message)
            # ACK = 0

            # self.tx_ID = 1
            self.transmitter()
            file.write("0\n 1\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
            os.system(METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN)  # MATLAB call with file Leia_DAC_down.m
            time.sleep(SLEEP_TIME)
            print(file_uploaded_message)
            ACK = 0

        return ACK

    def transmitter(self, SNR_estimation):
        Preemphasis = 'True'
        # Algorithm parameters
        gapdB = 9.8
        Loading_algorithm = 'LCRA_QAM'

        # Parameters for the OFDM signal definition

        Ncarriers = 512  # Number of carriers
        SNRT = np.zeros((Ncarriers,), dtype=float)
        SNR_in = np.empty((Ncarriers,), dtype=float)
        constellation = "QAM"
        bps = 2  # Bit per symbol
        CP = 0.019  # Cyclic prefix
        NTS = 4  # Number of training symbols
        Nsymbols = 16 * 3 * 1024  # BER[kosnr]No. of symbols without TS
        NsymbolsTS = Nsymbols + NTS * Ncarriers  # No. of symbols with TS
        Nframes = NsymbolsTS / Ncarriers  # No of OFDM symbols / frames
        e_fec = np.true_divide(7, 100)  # FEC overhead
        sps = 3.2  # Samples per symbol
        fs = 64e9  # Sampling frequency DAC
        BWs = fs / sps  # BW electrical signal
        print('Signal bandwidth:', BWs / 1e9, 'GHz')

        if SNR_estimation == False:
            print('Implementing loading algorithm...')
            gap = 10 ** (gapdB / 10.)
            if self.tx_ID == 0:
                SNR_in = np.load('ChannelGain.npy')
            else:
                SNR_in = np.load('ChannelGain2.npy')
            Load = of.Loading(Ncarriers, BWs)
            if Loading_algorithm == 'LCMA_QAM':
                BitRate=20e9
                (En, bn) = Load.LCMA_QAM(gap, BitRate / float(BWs), SNR_in)
            if Loading_algorithm == 'LCRA_QAM':
                (En, bn, BitRate) = Load.LCRA_QAM(gap, SNR_in)
            bps = np.sum(bn) / float(len(bn))
        else:
            bn = bps * np.ones(Ncarriers)
            # bn[240:240+30]=np.zeros(30)
            bps = np.sum(bn) / float(len(bn))
            BitRate = BWs * bps  # Net data rate
        print('BitRate=', BitRate / 1e9, 'Gb/s', 'BW=', BWs / 1e9, 'GHz')
        # plt.plot(bn)
        # plt.show()
        fc = BWs / 2
        BitStream = np.ma.empty(NsymbolsTS * bps)  # Initialize BitStream
        ttime = (1 / fs) * np.ones((sps * Nframes * (Ncarriers + np.round(CP * Ncarriers)),))
        ttt = ttime.cumsum()

        if self.tx_ID == 0:
            np.random.seed(42)
        else:
            np.random.seed(36)
        data = np.random.randint(0, 2, bps * Nsymbols)
        TS = np.random.randint(0, 2, NTS * bps * Ncarriers)
        BitStream = np.array(np.zeros(Nframes * np.sum(bn)), int)
        BitStream = np.r_[TS, data]
        BitStream = BitStream.reshape((Nframes, np.sum(bn)))
        cdatar = np.array(np.zeros((Nframes, Ncarriers)), complex)

        cumBit = 0
        for k in range(0, Ncarriers):
            (FormatM, bitOriginal) = modulation.Format(constellation, bn[k])
            cdatar[:, k] = modulation.Modulator(BitStream[:, cumBit:cumBit + bn[k]], FormatM, bitOriginal, bn[k])
            cumBit = cumBit + bn[k]
        if SNR_estimation == 'False':  # Power loading
            cdatary = cdatar * np.sqrt(En)
        else:
            cdatary = cdatar

        FHTdatatx = of.ifft(cdatary, Ncarriers)
        # add cyclic prefix
        FHTdata_cp = np.concatenate((FHTdatatx, FHTdatatx[:, 0:np.round(CP * Ncarriers)]), axis=1)

        # Serialize
        Cx = FHTdata_cp.reshape(FHTdata_cp.size, )

        # print 'Clipping the signal...'
        deviation = np.std(Cx)
        # k_clip=3.16 # 256QAM
        # k_clip=2.66 # optimum for 32QAM
        k_clip = 2.8  # optimum for 64QAM
        Cx_clip = Cx.clip(min=-k_clip * deviation, max=k_clip * deviation)

        ## resample
        Cx_up = sgn.resample(Cx_clip, sps * Cx_clip.size)

        # print G+ 'Upconversion...'

        Cx_up2 = Cx_up.real * np.cos(2 * np.math.pi * fc * ttt) + Cx_up.imag * np.sin(2 * np.math.pi * fc * ttt)

        if Preemphasis == 'True':
            print('Preemphasis...')
            # Pre-emphasis (inverted gaussian) filter
            BW = 25e9
            # BW=20e9;
            n = 2
            sigma = BW / (2 * np.sqrt(2 * np.log10(2)))
            stepfs = fs / len(Cx_up2)
            freq1 = np.arange(stepfs, fs / 2 - stepfs, stepfs)
            freq2 = np.arange(-fs / 2, 0, stepfs)
            freq = np.r_[freq1, 0, freq2, fs / 2 - stepfs]
            emphfilt = np.exp(.5 * np.abs(freq / sigma) ** n);  # just a gaussian filter inverted
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
        np.savetxt(TEMP_TXT, Cx_LEIA)  # .txt with the OFDM signal

        if self.tx_ID == 0:
            np.save('params_tx', (bn, cdatar, data, Cx_up, Cx_up2))
        else:
            np.save('params_tx2', (bn, cdatar, data, Cx_up, Cx_up2))

        return 0


if __name__ == '__main__':
    # TODO create a main test like 9 slide information
    # configuration 1a scenario (METRO_, OpenConfig client)
    trx_mode = 0
    tx_ID = 0
    tx = DAC(trx_mode, tx_ID)

    ack = tx.mode()
    print('ACK= ', ack)
