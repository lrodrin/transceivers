from __future__ import print_function
import numpy as np


class Loading:

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
        print('Margin=', margin, 'Rate=', Rate_check)
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
        print('Rate=', Rate_check / 1e9, 'Gb/s')
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
        print('Margin=', margin, 'Rate=', Rate_check)
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
        print('Rate=', Rate_check)
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
