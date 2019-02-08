import numpy as np

import lib.ofdm as ofdm
from lib.dac.dac import DAC


def switch_configuration():
    pass

def mode(SNR, BER, FEC):
    gapdB = 9.6
    En = np.array(np.zeros(DAC.Ncarriers))
    bn = np.array(np.zeros(DAC.Ncarriers))

    if trx_mode == 0:
        bn = DAC.bps * np.ones((DAC.Ncarriers,))
        En = np.ones((DAC.Ncarriers,))
        # SNR_f, BER = call al agent del receptor amb el valor de SNR
        # edit SNR inside agent configuration
    else:
        print('Implementing loading algorithm...')
        gap = 10 ** (DAC.gapdB / 10.)
        Load = ofdm.Loading(DAC.Ncarriers, DAC.BWs)
        (En, bn, BitRate) = Load.LCRA_QAM(gap, SNR_f)
        # SNR, BER = call al agent del receptor amb el valor de BER

        if FEC == 'HD-FEC':
        # refinar la BER segons la FEC

        else:
            # refinar la BER segons la FEC


    bps = np.sum(bn) / float(len(bn))
    BitRate = self.BWs * bps  # Net data rate
    print('BitRate = ', BitRate / 1e9, 'Gb/s', 'BW = ', self.BWs / 1e9, 'GHz')
    return [bn, En, SNR_f]






# variables

Loading_algorithm = 'LCRA_QAM'
 - gapdB (float): Set SNR gap.
- Loading_algorithm (str): Set type of loading algorithm (e.g. LC_RA or LC_MA).

if __name__ == '__main__':
    FEC = 'HD-FEC'  # SD-FEC or HD-FEC
    trx_mode = 0 # 0 estimation 1 transmission
    bn, En = mode(trx_mode, BER, FEC)