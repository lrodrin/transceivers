import numpy as np
import scipy.signal as sgn
import visa

import lib.constellationV2 as modulation
import lib.ofdm as ofdm

# TODO error control
NUM_ITERATIONS = 5


def acquire(channel_ID, npoints, fs):
    """

    :param channel_ID:
    :param npoints:
    :param fs:
    :return:
    """
    dpo = visa.instrument("TCPIP::10.1.1.14::4000::SOCKET")
    # dpo = visa.instrument("TCPIP0::10.1.1.14::inst0::INSTR")

    dpo.write('HOR:MODE:RECO %d' % npoints)  # Set the record length to npoints
    dpo.write('HOR:MODE:SAMPLER %d' % fs)  # Set the sample rate to fs

    # print "Acquiring channel %d from %s" % (channel_ID, dpo.ask('*IDN?'))

    dpo.write('DAT:SOU CH%d' % channel_ID)
    dpo.write('DAT:ENC ASCII')
    # dpo.write('DAT:ENC SFPbinary')
    # print dpo.ask('DAT:ENC?')
    dpo.write('DAT:STAR %d' % 1)
    dpo.write('DAT:STOP %d' % npoints)

    aux = dpo.ask('CURV?')

    dpo.close()

    return np.fromstring(aux, dtype=float, sep=',')


class OSC:
    """
    This is a class for Oscilloscope configuration.

    """

    def __init__(self, trx_mode, rx_ID, FEC, bps, pps):
        """
        The constructor for Oscilloscope class.

        Define and initialize the Oscilloscope default parameters:

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
            - name: f_DCO.
              description: Frew mostreig de OSC.
              type: int
            - name: Loading_algorithm.
              description: 0 == Rate adaptiv if SNR_estimation==True:e , 1 == Margin adaptive.
              type: string
            - name: Niter.
              description: Number of iterations.
              type: int
            - name: nsamplesrx.
              description:
              type: int


        :param rx_ID: Identify the channel of the OSC to be used and the local files to use for storing data.
        :param trx_mode: (0 or 1), for identifying the mode of the transceiver: 0 for estimation mode and 1 for
        transmission mode.+
        :param FEC: (HD-FEC, SD-FEC), in order to identifiy the channel encoding to be used (TBI).
        :param bps: array of 512 positions. It contains the bits per symbol per subcarrier.
        :param pps: array of 512 positions. It contains the power per subcarrier figure.
        :type trx_mode: int
        :type rx_ID: int
        :type FEC: string
        :type bps:int array
        :type pps: float array

        """
        self.trx_mode = trx_mode
        self.rx_ID = rx_ID
        self.FEC = FEC
        self.bps = bps
        self.pps = pps

        # Parameters for the OFDM signal definition
        self.Ncarriers = 512
        self.constellation = 'QAM'
        self.CP = 0.019
        self.NTS = 4
        self.Nsymbols = 16 * 3 * 1024
        self.NsymbolsTS = self.Nsymbols + self.NTS * self.Ncarriers
        self.Nframes = self.NsymbolsTS / self.Ncarriers
        self.sps = 3.2
        self.fs = 64e9

        self.f_DCO = 100e9
        # self.Tx_success = False
        self.Loading_algorithm = 'LCRA_QAM'
        self.Niter = NUM_ITERATIONS

        self.nsamplesrx = 2 * self.sps * self.Nframes * (self.Ncarriers + np.round(self.CP * self.Ncarriers))
        # nsamplesrx must be multiple of 4

    def receiver(self):
        """

        :return: ACK (0 for OK and -1 in case there is some error), SNR and BER.
        :rtype: list
        """
        if self.rx_ID == 0:
            (bn, cdatar, data, Cx_up, Cx_up2) = np.load('params_tx.npy')  # TODO link to file
        else:
            (bn, cdatar, data, Cx_up, Cx_up2) = np.load('params_tx2.npy')  # TODO link to file

        BWs = self.fs / self.sps  # BW electrical signal
        print('Signal bandwidth:', BWs / 1e9, 'GHz')

        R = self.f_DCO / self.fs  # ?
        fc = BWs / 2
        ttime2 = (1 / self.fs) * np.ones((self.nsamplesrx,))  # ?
        ttt2 = ttime2.cumsum()
        Subzero = np.array(np.where(bn == 0))
        SNRT = 0
        BERT = 0
        cdatar = np.delete(cdatar, Subzero, axis=1)
        bn = np.delete(bn, Subzero)
        Runs = 0

        for run in range(1, self.Niter + 1):
            Ncarriers_eq = self.Ncarriers
            print('adquire...')
            if self.rx_ID == 0:
                data_acqT = acquire(1, R * self.nsamplesrx, self.f_DCO)
            else:
                data_acqT = acquire(3, R * self.nsamplesrx, self.f_DCO)

            data_acqT = data_acqT - np.mean(data_acqT)
            data_acq2 = sgn.resample(data_acqT, len(data_acqT) / float(R))

            I_rx_BB = data_acq2 * np.cos(2 * np.math.pi * fc * ttt2[0:data_acq2.size]) + 1j * data_acq2 * np.sin(
                2 * np.math.pi * fc * ttt2[0:data_acq2.size])
            # I_rx_BB=Cx_up2*np.cos(2*np.math.pi*fc*ttt2[0:Cx_up2.size])+1j*Cx_up2*np.sin(2*np.math.pi*fc*ttt2[0:Cx_up2.size])

            ref2 = Cx_up[0:self.sps * self.NTS * (Ncarriers_eq + np.round(self.CP * Ncarriers_eq))]

            Bfilt = sgn.firwin(2 ** 9, BWs / self.fs, 0)
            I_rx_BBf = sgn.filtfilt(Bfilt, [1], I_rx_BB)
            Rd = np.correlate(I_rx_BBf[0:self.nsamplesrx / 2], ref2)
            Rdlog = 20 * np.log10(np.abs(Rd))
            if Rdlog.max(0) < np.mean(Rdlog) + 20:
                print('Warning: Not able to sync!')
            else:
                peakind = (Rdlog == Rdlog.max(0)).nonzero()
                index = peakind[0][0]
                data_sync = I_rx_BBf[index:index + self.nsamplesrx / 2]

                Cx_down = sgn.resample(data_sync, (Ncarriers_eq + np.round(self.CP * Ncarriers_eq)) * self.Nframes)

                cdatarxr_CP = Cx_down.reshape(self.Nframes, Ncarriers_eq + np.round(self.CP * Ncarriers_eq))

                # Remove CP
                cdatarxr = cdatarxr_CP[:, 0:Ncarriers_eq]

                # Perform Transform
                FHTdatarx = ofdm.fft(cdatarxr, Ncarriers_eq)

                # Remove subcarriers set to 0 for equalization
                FHTdatarx = np.delete(FHTdatarx, Subzero, axis=1)
                Ncarriers_eq = Ncarriers_eq - Subzero.size

                # Equalize
                FHTdatarx_eq = ofdm.equalize_MMSE_LE(FHTdatarx, cdatar, Ncarriers_eq, self.NTS)
                SNR = ofdm.SNR_estimation(cdatar[self.NTS:, ], FHTdatarx_eq, self.Nframes - self.NTS, Ncarriers_eq)
                print(SNR.size)
                SNRT = SNR + SNRT
                if run == self.Niter:
                    SNR = SNRT / self.Niter
                    if self.rx_ID == 0:
                        np.save('ChannelGain', SNR)
                    else:
                        np.save('ChannelGain2', SNR)

                FHTdatarx_eq[:, Ncarriers_eq / 2] = cdatar[self.NTS:, Ncarriers_eq / 2]
                FHTdatarx_eq[:, 0] = cdatar[self.NTS:, 0]

                # Serialize
                bps2 = np.sum(bn) / float(len(bn))
                datarx = np.array(np.zeros((self.Nframes - self.NTS, np.round(Ncarriers_eq * bps2))))
                cumbit = 0

                # Bit decision
                for i in range(0, Ncarriers_eq):
                    (FormatM, bitOriginal) = modulation.Format(self.constellation, bn[i])
                    datarx[:, cumbit:cumbit + bn[i]] = modulation.Demod(FHTdatarx_eq[:, i], FormatM.reshape(1, -1),
                                                                        bitOriginal, bn[i])
                    cumbit = cumbit + bn[i]

                datarx = datarx.reshape(np.round(Ncarriers_eq * (self.Nframes - self.NTS) * bps2, ))
                diff = datarx - data

                # BER calculus
                Nerr = np.sum(np.sqrt(diff.real ** 2 + diff.imag ** 2))
                BER = np.true_divide(Nerr, data.size)
                print('BER = ', BER, 'iteration = ', run)
                BERT = BERT + BER
                Runs = Runs + 1

        BER = BERT / Runs

        # TODO bluespace return SNR
        SNR = None

        return SNR, BER

        # if BER > 4.6e-3:
        #     return SNR, BER
        # else:
        #     return SNR, BER
