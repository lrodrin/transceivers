"""This is the OSC module.
"""
import logging

import numpy as np
import scipy.signal as sgn
import visa

import lib.constellationV2 as modulation
import lib.ofdm as ofdm

logger = logging.getLogger("OSC")
logger.addHandler(logging.NullHandler())


class OSC:
    """
    This is a class for Oscilloscope module.

    :ivar int Ncarriers: Number of carriers
    :ivar str Constellation: Modulation format
    :ivar float CP: Cyclic prefix
    :ivar int NTS: Number of training symbols
    :ivar int Nsymbols: Number of generated symbols
    :ivar int NsymbolsTS: Number of generated symbols without TS
    :ivar int Nframes: Number of OFDM frames
    :ivar float sps: Samples per symbol for the DAC
    :ivar int fs: DAC frequency sampling
    :ivar int Niters: Number of iterations for BER calculation
    :ivar int f_DCO: Sampling frequency of the DPO
    :ivar int nsamplesrx: Number of received samples. Must be multiple of 4
    :ivar int k_clip: factor for clipping the OFDM signal. 3.16 optimum for 256 QAM. 2.66 optimum for 32 QAM.
    2.8 optimum for 64 QAM.
    :ivar int Qt: Quantization steps
    :ivar int bps: Number of bits per symbol
    """
    Ncarriers = 512
    Constellation = "QAM"
    CP = 0.019
    NTS = 4
    Nsymbols = 16 * 3 * 1024
    NsymbolsTS = Nsymbols + NTS * Ncarriers
    Nframes = NsymbolsTS / Ncarriers
    sps = 3.2
    fs = 64e9
    Niters = 10
    f_DCO = 100e9
    nsamplesrx = 2 * sps * Nframes * (Ncarriers + np.round(CP * Ncarriers))
    k_clip = 2.8
    Qt = 255
    bps = 2

    def __init__(self):
        """
        The constructor for Oscilloscope class.
        Define and initialize the Oscilloscope default parameters for the OFDM signal definition:

            - Set number of carriers.
            - Set modulation format.
            - Set cyclic prefix.
            - Set number of training symbols.
            - Set number of generated symbols.
            - Set number of generated symbols without TS.
            - Set number of OFDM frames.
            - Set samples per symbol for the DAC.
            - Set DAC frequency sampling.
            - Set number of iterations for BER calculation.
            - Set sampling frequency of the DPO.
            - Set number of received samples. Must be multiple of 4.
            - Set factor for clipping the OFDM signal.
            - Set quantization steps.
            - Set number of bits per symbol.
        """
        self.Ncarriers = OSC.Ncarriers
        self.Constellation = OSC.Constellation
        self.CP = OSC.CP
        self.NTS = OSC.NTS
        self.Nsymbols = OSC.Nsymbols
        self.NsymbolsTS = OSC.NsymbolsTS
        self.Nframes = OSC.Nframes
        self.sps = OSC.sps
        self.fs = OSC.fs
        self.Niters = OSC.Niters
        self.f_DCO = OSC.f_DCO
        self.nsamplesrx = OSC.nsamplesrx
        self.k_clip = OSC.k_clip
        self.Qt = OSC.Qt
        self.bps = OSC.bps

    def receiver(self, dac_out, osc_in, bn, En, eq):
        """
        Adquires the OFDM signal received at the DPO and recovers by offline DSP the transmitted BitStream.

        :param dac_out: output port of DAC
        :type dac_out: int
        :param osc_in: input port
        :type osc_in: int
        :param bn: array of Ncarriers positions that contains the bits per symbol per subcarrier
        :type bn: int array of 512 positions
        :param En: array of Ncarriers positions that contains the power per subcarrier figure
        :type En: float array of 512 positions
        :param eq: select the type of equalization (ZF or MMSE)
        :type eq: str
        :return: estimated SNR per subcarrier and the BER of received data
        :rtype: list
        """
        try:
            cdatar, data, Cx_up = self.generated_data(dac_out, bn, En)

            BWs = self.fs / self.sps  # BW electrical signal
            R = self.f_DCO / self.fs  # Sampling factor for the receiver
            fc = BWs / 2  # Central frequency
            ttime2 = (1 / self.fs) * np.ones((self.nsamplesrx,))
            ttt2 = ttime2.cumsum()

            Subzero = np.array(np.where(bn == 0))
            SNRT = 0
            BERT = 0
            SNR = np.array(np.zeros(self.Ncarriers))
            cdatar = np.delete(cdatar, Subzero, axis=1)
            bn = np.delete(bn, Subzero)
            Runs = 0
            data_acqT = np.array(np.zeros(R * self.nsamplesrx))
            logger.debug("Iterating")
            for run in range(1, self.Niters + 1):
                Ncarriers_eq = self.Ncarriers

                if osc_in == 1:
                    data_acqT = self.acquire(1, R * self.nsamplesrx, self.f_DCO)  # Adquire signal in channel 1
                elif osc_in == 2:
                    data_acqT = self.acquire(4, R * self.nsamplesrx, self.f_DCO)  # Adquire signal in channel 4

                data_acqT = data_acqT - np.mean(data_acqT)
                data_acq2 = sgn.resample(data_acqT, len(data_acqT) / float(R))  # Recover the original signal length

                I_rx_BB = data_acq2 * np.cos(2 * np.math.pi * fc * ttt2[0:data_acq2.size]) + 1j * data_acq2 * np.sin(
                    2 * np.math.pi * fc * ttt2[0:data_acq2.size])

                ref2 = Cx_up[0:self.sps * self.NTS * (Ncarriers_eq + np.round(
                    self.CP * Ncarriers_eq))]  # Creating a reference signal for syncronization

                logger.debug("Synchronizing")
                Bfilt = sgn.firwin(2 ** 9, BWs / self.fs, 0)
                I_rx_BBf = sgn.filtfilt(Bfilt, [1], I_rx_BB)
                Rd = np.correlate(I_rx_BBf[0:self.nsamplesrx / 2], ref2)  # Look for the beginning of the OFDM frame
                Rdlog = 20 * np.log10(np.abs(Rd))

                if Rdlog.max(0) < np.mean(Rdlog) + 20:
                    logger.warning("Not able to sync!")
                else:
                    peakind = (Rdlog == Rdlog.max(0)).nonzero()
                    index = peakind[0][0]
                    data_sync = I_rx_BBf[index:index + self.nsamplesrx / 2]
                    logger.debug("Data is synchronized!")

                    Cx_down = sgn.resample(data_sync, (Ncarriers_eq + np.round(self.CP * Ncarriers_eq)) * self.Nframes)

                    cdatarxr_CP = Cx_down.reshape(self.Nframes, Ncarriers_eq + np.round(self.CP * Ncarriers_eq))

                    logger.debug("Remove CP")
                    cdatarxr = cdatarxr_CP[:, 0:Ncarriers_eq]

                    logger.debug("Perform FFT")
                    FHTdatarx = ofdm.fft(cdatarxr, Ncarriers_eq)

                    FHTdatarx = np.delete(FHTdatarx, Subzero, axis=1)
                    # Remove subcarriers set to 0 for equalization to avoid divide by 0
                    Ncarriers_eq = Ncarriers_eq - Subzero.size

                    logger.debug("Performing Equalization")
                    if eq == "MMSE":
                        FHTdatarx_eq = ofdm.equalize_MMSE_LE(FHTdatarx, cdatar, Ncarriers_eq, self.NTS)
                    else:
                        FHTdatarx_eq = ofdm.equalize_fft(FHTdatarx, cdatar, Ncarriers_eq, self.NTS)

                    logger.debug("Estimating SNR")
                    # TODO take into account in the controller that we only use the SNR corresponding to estimation
                    #  mode defined at the controller
                    SNR = ofdm.SNR_estimation(cdatar[self.NTS:, ], FHTdatarx_eq, self.Nframes - self.NTS,
                                              Ncarriers_eq)
                    SNRT = SNR + SNRT
                    if run == self.Niters:
                        SNR = SNRT / self.Niters

                    FHTdatarx_eq[:, Ncarriers_eq / 2] = cdatar[self.NTS:, Ncarriers_eq / 2]
                    FHTdatarx_eq[:, 0] = cdatar[self.NTS:, 0]

                    # Serialize
                    bps2 = np.sum(bn) / float(len(bn))
                    datarx = np.array(np.zeros((self.Nframes - self.NTS, np.round(Ncarriers_eq * bps2))))
                    cumbit = 0

                    logger.debug("Demmaping")
                    for i in range(0, Ncarriers_eq):
                        (FormatM, bitOriginal) = modulation.Format(self.Constellation, bn[i])
                        datarx[:, cumbit:cumbit + bn[i]] = modulation.Demod(FHTdatarx_eq[:, i], FormatM.reshape(1, -1),
                                                                            bitOriginal, bn[i])
                        cumbit = cumbit + bn[i]

                    logger.debug("Demmaping")
                    datarx = datarx.reshape(np.round(Ncarriers_eq * (self.Nframes - self.NTS) * bps2, ))
                    diff = datarx - data

                    logger.debug("Calculating BER")
                    Nerr = np.sum(np.sqrt(diff.real ** 2 + diff.imag ** 2))
                    BER = np.true_divide(Nerr, data.size)
                    logger.debug("BER = {}, iteration = {}".format(BER, run))
                    BERT = BERT + BER
                    Runs = Runs + 1

            BER = BERT / Runs
            return [SNR.tolist(), BER]

        except Exception as error:
            logger.error("OSC receiver method, {}".format(error))
            raise error

    @staticmethod
    def acquire(channel_ID, npoints, fs):
        """
        This function acquires the transmitted data from the specified OSC channel.

        :param channel_ID: DPO channel used to adquire data
        :type channel_ID: int
        :param npoints: number of points to adquire
        :type npoints: int 
        :param fs: sampling frequency of the DPO
        :type: int
        :return: adquired signal
        :rtype: float array
        """
        try:
            dpo = visa.instrument("TCPIP::10.1.1.14::4000::SOCKET")

            dpo.write("HOR:mode:RECO %d" % npoints)  # Set the record length to npoints
            dpo.write("HOR:mode:SAMPLER %d" % fs)  # Set the sample rate to fs
            logger.debug("Acquiring data...")

            dpo.write("DAT:SOU CH%d" % channel_ID)
            dpo.write("DAT:ENC ASCII")

            dpo.write("DAT:STAR %d" % 1)
            dpo.write("DAT:STOP %d" % npoints)

            aux = dpo.ask("CURV?")
            dpo.close()
            return np.fromstring(aux, dtype=float, sep=",")

        except Exception as error:
            logger.error("OSC acquire method, {}".format(error))
            raise error

    def generated_data(self, dac_out, bn, En):
        """
        Generate data with different seed for different users/clients.

        :param dac_out: output port of DAC
        :type dac_out: int
        :param bn: array of Ncarriers positions that contains the bits per symbol per subcarrier
        :type bn: int array of 512 positions
        :param En: array of Ncarriers positions that contains the power per subcarrier figure
        :type En: float array of 512 positions
        :return: Mapped data, transmitted bitstream and OFDM signal
        :rtype: list
        """
        try:
            self.bps = np.sum(bn) / float(len(bn))  # Recalculate bps
            logger.debug("Generating data")  # Generate data with different seed for the different output ports
            if dac_out == 1:
                np.random.seed(42)
            elif dac_out == 2:
                np.random.seed(36)
            elif dac_out == 3:
                np.random.seed(32)
            elif dac_out == 4:
                np.random.seed(46)

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
            Cx_bias_up = Cx_up - np.min(Cx_up)
            Cx_up = np.around(Cx_bias_up / np.max(Cx_bias_up) * self.Qt - np.ceil(self.Qt / 2))

            return [cdatar, data, Cx_up]

        except Exception as error:
            logger.error("OSC generated_data method, {}".format(error))
            raise error
