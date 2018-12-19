import numpy as np
import cmath as math
from pylab import *


def fft(data, Ncarriers):
    return np.fft.fft(data, Ncarriers)


def ifft(data, Ncarriers):
    return np.fft.ifft(data, Ncarriers)


def equalize_fft(datarx, datatx, Ncarriers, NTS):
    TS2 = datatx[0:NTS, :]

    Hs = datarx[0:NTS, :]

    Hs2 = Hs / TS2

    H = sum(Hs2, axis=0) / NTS

    # Build diagonal

    W = diag(H)
    # W[0,0]=H[0]/TS2[0]

    # equalize
    IW = np.linalg.inv(W)
    data_eq_NTS = np.inner(datarx, IW)
    data_eq = data_eq_NTS[NTS:, ]

    return data_eq


def equalize_LMS(datarx, datatx, Ncarriers, NTS):
    TS2 = datatx[0:NTS, :]
    a = np.array(np.zeros(Ncarriers))
    b = np.array(np.zeros(Ncarriers))
    for i in range(0, Ncarriers):
        a[i] = np.sum(
            np.real(datarx[0:NTS, i]) * np.real(TS2[:, i]) + np.imag(datarx[0:NTS, i]) * np.imag(TS2[:, i])) / np.sum(
            np.real(datarx[0:NTS, i]) ** 2 + np.imag(datarx[0:NTS, i]) ** 2)
        b[i] = np.sum(
            np.real(datarx[0:NTS, i]) * np.imag(TS2[:, i]) - np.imag(datarx[0:NTS, i]) * np.real(TS2[:, i])) / np.sum(
            np.real(datarx[0:NTS, i]) ** 2 + np.imag(datarx[0:NTS, i]) ** 2)
    data_eq_NTS = (a + 1j * b) * datarx
    data_eq = data_eq_NTS[NTS:, ]
    return data_eq


def fht(data, Ncarriers):
    X = np.fft.fft(data, Ncarriers)
    return (X.real - X.imag) / np.sqrt(Ncarriers)


def equalize_fht(datarx, datatx, Ncarriers, NTS):
    TS2 = datatx[0, :]

    Hs = datarx[0:NTS, :]

    H = sum(Hs, axis=0) / NTS

    TSRxrev = flipud(H)

    # Build A
    A = np.zeros((Ncarriers - 1,))
    A1 = (H[1:Ncarriers / 2]) / TS2[1:Ncarriers / 2]
    A[0:Ncarriers / 2 - 1] = A1
    A[Ncarriers / 2 - 1] = 0
    A[Ncarriers / 2:len(A)] = flipud(A1)

    # Build B
    B1 = TSRxrev[0:Ncarriers / 2 - 1] / TS2[0:Ncarriers / 2 - 1];
    B = np.zeros((Ncarriers - 1,))
    B[0:Ncarriers / 2 - 1] = -B1
    B[Ncarriers / 2 - 1] = 0
    B[Ncarriers / 2:len(A)] = flipud(B1)

    AA = diag(A)
    BB = fliplr(diag(B))
    A0 = H[0] / TS2[0]

    # Build W (eq matrix)
    W = np.zeros((Ncarriers, Ncarriers))
    W[1:Ncarriers, 1:Ncarriers] = AA + BB
    W[Ncarriers / 2, Ncarriers / 2] = 1
    W[0, 0] = H[0] / TS2[0]

    # equalize
    IW = np.linalg.inv(W)
    data_eq_NTS = np.inner(datarx, IW)
    data_eq = data_eq_NTS[NTS:, ]

    return data_eq


def SNR_estimation(x, yeq, NFrames, Ncarriers):
    e = np.array(np.zeros((Ncarriers, NFrames), complex))
    SNR = np.array(np.zeros(Ncarriers))
    Px = np.array(np.zeros(Ncarriers))
    Pe = np.array(np.zeros(Ncarriers))
    for k in range(0, Ncarriers):
        Px[k] = np.sum(np.abs(x[:, k]) ** 2) / len(x)
        e[k, :] = yeq[:, k] - x[:, k]
        Pe[k] = np.sum(np.abs(e[k, :]) ** 2) / len(e)
        SNR[k] = Px[k] / float(Pe[k])  # Px is 1

    return (SNR)


class Loading():
    def __init__(self, Ncarriers, BW):
        self.Ncarriers = Ncarriers
        self.BW = BW

    def LCMA_QAM(self, gapdB, Rate, gn):
        # initialization
        gap = 10 ** (gapdB / 10.)
        # gn=np.load('ChannelGain.npy')
        En = np.array(np.zeros(self.Ncarriers))
        bn = np.array(np.zeros(self.Ncarriers))
        table = np.array(np.zeros(self.Ncarriers))

        # decision table
        table = 2 * gap / gn
        while (1):
            y = np.min(table)
            index = np.argmin(table)
            if np.sum(bn) >= self.Ncarriers * Rate:
                break
            else:
                En[index] = En[index] + y
                bn[index] = bn[index] + 1
                table[index] = 2 * table[index]
                # check data rate
        Rate_check = self.BW * (np.sum(bn) / float(self.Ncarriers))
        # check margin
        margin = 10 * np.log10(self.Ncarriers / np.sum(En))
        print 'Margin=', margin, 'Rate=', Rate_check
        return En, bn

    def LCRA_QAM(self, gapdB, gn):
        # initialization
        gap = 10 ** (gapdB / 10)
        # gn=np.load('ChannelGain.npy')
        En = np.array(np.zeros(self.Ncarriers))
        bn = np.array(np.zeros(self.Ncarriers))
        table = np.array(np.zeros(self.Ncarriers))
        Enorm = 1
        Eused = 0  # used energy
        # decision table
        table = 2 * gap / gn
        while (1):
            y = np.min(table)
            index = np.argmin(table)
            Eused = Eused + y
            if Eused > self.Ncarriers * Enorm:
                break
            else:
                En[index] = En[index] + y
                bn[index] = bn[index] + 1
                table[index] = 2 * table[index]
                # check data rate
        Rate_check = self.BW * (np.sum(bn) / float(self.Ncarriers))
        print 'Rate=', Rate_check / 1e9, 'Gb/s'
        return En, bn, Rate_check

    def LCMA_PAM(self, gapdB, Rate):
        # initialization
        gap = 10 ** (gapdB / 10)
        gn = np.load('ChannelGain.npy')
        En = np.array(np.zeros(self.Ncarriers))
        bn = np.array(np.ones(self.Ncarriers))
        table = np.array(np.zeros(self.Ncarriers))

        # decision table
        table = gap * (2 ** (2 * bn) - 1) / gn
        while (1):
            y = np.min(table)
            index = np.argmin(table)
            if np.sum(bn) >= self.Ncarriers * Rate:
                break
            else:
                En[index] = En[index] + y
                bn[index] = bn[index] + 1
                table[index] = 4 * table[index]
        # check data rate
        Rate_check = (1 / self.Ncarriers) * np.sum(bn)
        # check margin
        margin = 10 * np.log10(self.Ncarriers / np.sum(En))
        print 'Margin=', margin, 'Rate=', Rate_check
        return En, bn

    def LCRA_PAM(self, gapdB):
        # initialization
        gap = 10 ** (gapdB / 10)
        gn = np.load('ChannelGain.npy')
        En = np.array(np.zeros(self.Ncarriers))
        bn = np.array(np.ones(self.Ncarriers))
        table = np.array(np.zeros(self.Ncarriers))
        Enorm = 1
        Eused = 0  # used energy
        # decision table
        table = gap * (2 ** (2 * bn) - 1) / gn
        while (1):
            y = np.min(table)
            index = np.argmin(table)
            Eused = Eused + y
            if Eused > self.Ncarriers * Enorm:
                break
            else:
                En[index] = En[index] + y
                bn[index] = bn[index] + 1
                table[index] = 4 * table[index]
                # check data rate
        Rate_check = (1 / self.Ncarriers) * np.sum(bn)
        print 'Rate=', Rate_check
        return En, bn

    def CCBMA_QAM(self, gapdB):
        gn = np.load('ChannelGain.npy')
        gap = 10 ** (gapdB / 10)
        gnOrdered = np.sort(gn)
        gnInvOrdered = gnOrdered[::-1]  # re-order gn
        # initialize
        Eaverage = 1
        btemp = np.array(np.zeros(Ncarriers))
        btemp[self.Ncarriers] = 0  # Tentative total bits
        i = Ncarriers  # Initial number of used carriers

        # Set equal energy on used tones
        while i > 0:
            SNR = np.array(np.zeros(i))
            En = self.Ncarriers * Eaverage / i
            for k in range(0, i):
                SNR[k] = gn[k] * En
            btemp[i] = np.sum(np.log2(1 + (SNR / gap)))
            if i < self.Ncarriers:  # In order to avoid the last subcarrier
                if btemp[i] < btemp[i + 1]:
                    bn = btemp[i + 1]
                    break  # close while we have the total number of bits
                else:
                    i = i - 1
            else:
                i = i - 1
        # check data rate
        Rate_check = (1 / self.Ncarriers) * np.sum(bn)
        return bn, En, Rate_check

    def CCBRA_QAM(self, gapdB):
        gn = np.load('ChannelGain.npy')
        gap = 10 ** (gapdB / 10)
        gnOrdered = np.sort(gn)
        gn = gnOrdered[::-1]  # re-order gn
        # initialize
        Eaverage = 1
        btemp = np.array(np.zeros(Ncarriers))
        btemp[self.Ncarriers] = 0  # Tentative total bits
        i = Ncarriers  # Initial number of used carriers

        # Set equal energy on used tones
        while i > 0:
            SNR = np.array(np.zeros(i))
            En = self.Ncarriers * Eaverage / i
            for k in range(0, i):
                SNR[k] = gn[k] * En
            btemp[i] = np.sum(np.log2(1 + (SNR / gap)))
            if i < self.Ncarriers:  # In order to avoid the last subcarrier
                if btemp[i] < btemp[i + 1]:
                    bn = btemp[i + 1]
                    break  # close while we have the total number of bits
                else:
                    i = i - 1
            else:
                i = i - 1
                # check data rate
        Rate_check = (1 / self.Ncarriers) * np.sum(bn)
        return bn, En, Rate_check

    def CCBMA_PAM(self, gapdB):
        gn = np.load('ChannelGain.npy')
        gap = 10 ** (gapdB / 10)
        gnOrdered = np.sort(gn)
        gn = gnOrdered[::-1]  # re-order gn
        # initialize
        Eaverage = 1
        btemp = np.array(np.zeros(Ncarriers))
        btemp[self.Ncarriers] = 0  # Tentative total bits
        i = Ncarriers  # Initial number of used carriers

        # Set equal energy on used tones
        while i > 0:
            SNR = np.array(np.zeros(i))
            En = self.Ncarriers * Eaverage / i
            for k in range(0, i):
                SNR[k] = gn[k] * En
            btemp[i] = np.sum((1 / 2.) * np.log2(1 + (SNR / gap)))
            if i < self.Ncarriers:  # In order to avoid the last subcarrier
                if btemp[i] < btemp[i + 1]:
                    bn = btemp[i + 1]
                    break  # close while we have the total number of bits
                else:
                    i = i - 1
            else:
                i = i - 1
                # check data rate
        Rate_check = (1 / self.Ncarriers) * np.sum(bn)
        return bn, En, Rate_check

    def CCBRA_PAM(self, gapdB):
        gn = np.load('ChannelGain.npy')
        gap = 10 ** (gapdB / 10)
        gnOrdered = np.sort(gn)
        gn = gnOrdered[::-1]  # re-order gn
        # initialize
        Eaverage = 1
        btemp = np.array(np.zeros(Ncarriers))
        btemp[self.Ncarriers] = 0  # Tentative total bits
        i = Ncarriers  # Initial number of used carriers

        # Set equal energy on used tones
        while i > 0:
            SNR = np.array(np.zeros(i))
            En = self.Ncarriers * Eaverage / i
            for k in range(0, i):
                SNR[k] = gn[k] * En
            btemp[i] = np.sum((1 / 2.) * np.log2(1 + (SNR / gap)))
            if i < self.Ncarriers:  # In order to avoid the last subcarrier
                if btemp[i] < btemp[i + 1]:
                    bn = btemp[i + 1]
                    break  # close while we have the total number of bits
                else:
                    i = i - 1
            else:
                i = i - 1
                # check data rate
        Rate_check = (1 / self.Ncarriers) * np.sum(bn)
        return bn, En, Rate_check
