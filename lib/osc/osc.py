import numpy as np
import scipy.signal as sgn

import lib.dac.constellationV2 as modulation
import lib.instruments_v18p02 as inst
import lib.ofdm as ofdm


class OSC:
    def __init__(self, trx_mode, rx_ID):
        self.trx_mode = trx_mode  # For identifying the mode of the transceiver: 0 for METRO_1 scenario or 1 for
        # METRO_2 scenario
        self.rx_ID = rx_ID  # To identify the channel of the DAC to be used and the local files to use for storing
        # data. Tx_id when Mode 0 (METRO_1 scenario) is equivalent to select the Openconfig client. Tx_id when Mode 1
        # (METRO_2 scenario) is equivalent to select the S_BVT, which includes 2 clients multiplexed in a single
        # optical channel. Due to hardware limitations in this last case (METRO2 scenario) tx_ID will be always 0.

    def mode(self):
        # TODO cap a flask server
        if self.trx_mode == 0:
            (Tx_success, BER) = self.receiver()
            if Tx_success:
                ACK = 0
            else:
                ACK = -1
        else:
            self.rx_ID = 0
            (Tx_success_S0, BER) = self.receiver()
            self.rx_ID = 1
            (Tx_success_S1, BER) = self.receiver()
            if Tx_success_S0 and Tx_success_S1:
                ACK = 0
            else:
                ACK = -1
        return ACK

    def receiver(self):
        # TODO link cap a carpeta params*.npy
        if self.rx_ID == 0:
            (bn, cdatar, data, Cx_up, Cx_up2) = np.load('params_tx.npy')
        else:
            (bn, cdatar, data, Cx_up, Cx_up2) = np.load('params_tx2.npy')

        ##############################
        Ncarriers = 512  # Number of carriers
        constellation = "QAM"
        CP = 0.019  # Cyclic prefix
        NTS = 4  # Number of training symbols
        Nsymbols = 16 * 3 * 1024  # BER[kosnr]No. of symbols without TS
        NsymbolsTS = Nsymbols + NTS * Ncarriers  # No. of symbols with TS
        Nframes = NsymbolsTS / Ncarriers  # No of OFDM symbols / frames
        sps = 3.2  # Samples per symbol
        fs = 64e9  # Sampling frequency DAC

        f_DCO = 100e9 # frew mostreig de osc
        Tx_success = False
        Algorithm = 'LCRA_QAM'  # 0 == Rate adaptiv if SNR_estimation==True:e , 1 == Margin adaptive
        Numiter = 5  # Number of iterations

        SNRT = np.zeros((512,), dtype=float)
        SNR_B = np.empty((512,), dtype=float)
        nsamplesrx = 2 * sps * Nframes * (Ncarriers + np.round(CP * Ncarriers))  # nsamplesrx must be multiple of 4

        ###################
        BWs = fs / sps  # BW electrical signal
        R = f_DCO / fs
        fc = BWs / 2
        ttime2 = (1 / fs) * np.ones((nsamplesrx,))
        ttt2 = ttime2.cumsum()
        Subzero = np.array(np.where(bn == 0))
        SNRT = 0
        SNR = 0
        BERT = 0
        BER = 0.5
        cdatar = np.delete(cdatar, Subzero, axis=1)
        bn = np.delete(bn, Subzero)
        Runs = 0

        for run in range(1, Numiter + 1):
            Ncarriers_eq = Ncarriers
            print('Adquire')
            if self.rx_ID == 0:
                data_acqT = inst.acquire(1, R * nsamplesrx, f_DCO)
            else:
                data_acqT = inst.acquire(3, R * nsamplesrx, f_DCO)

            data_acqT = data_acqT - np.mean(data_acqT)
            data_acq2 = sgn.resample(data_acqT, len(data_acqT) / float(R))

            I_rx_BB = data_acq2 * np.cos(2 * np.math.pi * fc * ttt2[0:data_acq2.size]) + 1j * data_acq2 * np.sin(
                2 * np.math.pi * fc * ttt2[0:data_acq2.size])
            # I_rx_BB=Cx_up2*np.cos(2*np.math.pi*fc*ttt2[0:Cx_up2.size])+1j*Cx_up2*np.sin(2*np.math.pi*fc*ttt2[0:Cx_up2.size])

            ref2 = Cx_up[0:sps * NTS * (Ncarriers_eq + np.round(CP * Ncarriers_eq))]

            Bfilt = sgn.firwin(2 ** 9, BWs / fs, 0)
            I_rx_BBf = sgn.filtfilt(Bfilt, [1], I_rx_BB)
            Rd = np.correlate(I_rx_BBf[0:nsamplesrx / 2], ref2)
            Rdlog = 20 * np.log10(np.abs(Rd))
            # plt.plot(Rdlog)
            # plt.show()
            if Rdlog.max(0) < np.mean(Rdlog) + 20:
                print('Warning: Not able to sync!')
            # Runs=Runs+1
            else:
                # if run==Numiter:
                # plt.plot(Rdlog)
                # plt.show()

                # print 'Xcorrelation made!'
                peakind = (Rdlog == Rdlog.max(0)).nonzero()
                index = peakind[0][0]
                data_sync = I_rx_BBf[index:index + nsamplesrx / 2]

                Cx_down = sgn.resample(data_sync, (Ncarriers_eq + np.round(CP * Ncarriers_eq)) * Nframes)

                cdatarxr_CP = Cx_down.reshape(Nframes, Ncarriers_eq + np.round(CP * Ncarriers_eq))

                # Remove CP
                cdatarxr = cdatarxr_CP[:, 0:Ncarriers_eq]

                # Perform Transform
                FHTdatarx = ofdm.fft(cdatarxr, Ncarriers_eq)
                # remove subcarriers set to 0 for equalization

                FHTdatarx = np.delete(FHTdatarx, Subzero, axis=1)
                Ncarriers_eq = Ncarriers_eq - Subzero.size

                # Equalize
                # FHTdatarx_eq=of.equalize_fft(FHTdatarx, cdatar, Ncarriers_eq, NTS)
                # print FHTdatarx.size
                # print Ncarriers
                # print cdatar.size
                FHTdatarx_eq = ofdm.equalize_MMSE_LE(FHTdatarx, cdatar, Ncarriers_eq, NTS)
                # FHTdatarx_eq=of.equalize_LMS(FHTdatarx, cdatar, Ncarriers, NTS)
                # FHTdatarx_eq=FHTdatarx_eq
                # FHTdatarx_eq=np.delete(FHTdatarx_eq,Subzero,axis=1)
                # cdatar_eq=np.delete(cdatar,Subzero,axis=1)
                # Ncarriers_eq=Ncarriers_eq-Subzero.size
                # SNR estimation
                # if SNR_estimation==True:
                SNR = ofdm.SNR_estimation(cdatar[NTS:, ], FHTdatarx_eq, Nframes - NTS, Ncarriers_eq)
                print(SNR.size)
                SNRT = SNR + SNRT
                if run == Numiter:
                    SNR = SNRT / Numiter
                    if self.rx_ID == 0:
                        np.save('ChannelGain', SNR)
                    else:
                        np.save('ChannelGain2', SNR)
                # x=np.arange(0,Ncarriers_eq)
                # plt.plot(x,10*np.log10(SNR))
                # plt.show()
                # just a trick for not taking into account
                # Neither the N/2 carrier nor the first carrier
                FHTdatarx_eq[:, Ncarriers_eq / 2] = cdatar[NTS:, Ncarriers_eq / 2]
                FHTdatarx_eq[:, 0] = cdatar[NTS:, 0]

                # Serialize
                bps2 = np.sum(bn) / float(len(bn))
                datarx = np.array(np.zeros((Nframes - NTS, np.round(Ncarriers_eq * bps2))))
                cumbit = 0
                # Bit decision
                for i in range(0, Ncarriers_eq):
                    (FormatM, bitOriginal) = modulation.Format(constellation, bn[i])
                    datarx[:, cumbit:cumbit + bn[i]] = modulation.Demod(FHTdatarx_eq[:, i], FormatM.reshape(1, -1),
                                                                        bitOriginal, bn[i])
                    # datarx[:,cumbit:cumbit+bn[i]]=modulation.Demod(FHTdatarx_eq[:,i],FormatM,bitOriginal,bn[i])
                    cumbit = cumbit + bn[i]
                datarx = datarx.reshape(np.round(Ncarriers_eq * (Nframes - NTS) * bps2, ))
                # modulation.dibuixar_constelacions(np.real(RxConst),np.imag(RxConst))
                diff = datarx - data

                # BER calculus
                Nerr = np.sum(np.sqrt(diff.real ** 2 + diff.imag ** 2))
                BER = np.true_divide(Nerr, data.size)
                print('BER=', BER, 'iteration=', run)
                # if BER< 1e-1:
                BERT = BERT + BER
                Runs = Runs + 1

        BER = BERT / Runs
        # print'Average BER=', BER
        # print 'BER size', BERT.size

        if BER > 4.6e-3:
            Tx_success = False
        else:
            Tx_success = True

        return Tx_success, BER


# if __name__ == '__main__':
#     Tx = OSC(1, 0)
#     ACK = Tx.mode()
#     print('ACK=', ACK)
