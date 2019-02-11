import numpy as np

import lib.ofdm as ofdm
from lib.dac.dac import DAC


def loading(SNR, BER):
    tx = DAC()
    BitRate = 20e9
    En = np.array(np.zeros(DAC.Ncarriers))
    bn = np.array(np.zeros(DAC.Ncarriers))

    print('Implementing loading algorithm...')
    gapdB = 9.8 # SNR gap
    gap = 10 ** (gapdB / 10.)
    Load = ofdm.Loading(DAC.Ncarriers, tx.BWs)
    (En, bn) = Load.LCMA_QAM(gap, BitRate / float(tx.BWs), SNR)
    
    print('BitRate = ', BitRate / 1e9, 'Gb/s', 'BW = ', tx.BWs / 1e9, 'GHz')

    return [bn, En]


if __name__ == '__main__':
    bn, En = loading("osc snr", "ber osc")