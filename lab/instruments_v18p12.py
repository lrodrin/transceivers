# -*- coding: utf-8 -*-
import visa
import time
import socket
import wsapi
import numpy as np
import logging
import matplotlib.pyplot as plt
import pyserial as ser


# def LEIA_Ini(path,MatClient,frequency,freqRef):
#    MatClient.open()
#    port='cd \''+path+'\''
#    MatClient.eval(port)
#    MatClient.put({'frequency':frequency,'freqRef':freqRef}) 
#    MatClient.eval('disp(\'hello world\');')
#    print 'HEllo'
#    MatClient.eval('Leia_initialize(frequency,freqRef);')
#
#
# def write_LEIA(MatClient, hi,hq,vi,vq):
#    MatClient.put({'hi':hi,'hq': hq,'vi':vi,'vq':vq}) 
#    MatClient.eval('WriteLeia(hi,hq,vi,vq);')
#    
#    
# def LEIA_close(path,MatClient):
#    MatClient.eval('cd \''+path+'\'')
#    #Client.eval('Leia_close')
#    MatClient.close()

class ws():
    def __init__(self, name, configfile):
        self.name = name  # Name of the waveshaper
        self.filename = configfile  # configuration file of the waveshaper
        self.wavelength = np.ones([4, 1], dtype=float)  # wavelengths array
        self.bandwidth = np.zeros([4, 1], dtype=float)  # bandwidths array
        self.phase = np.zeros([4, 1], dtype=float)  # phases array
        self.attenuation = 60 * np.ones([4, 1], dtype=float)  # attenuations array
        self.open()

    def open(self):
        # Create and open the waveshaper
        wsapi.ws_create_waveshaper(self.name, self.filename)
        wsapi.ws_open_waveshaper(self.name)

    def close(self):
        # Close and delete the waveshaper
        wsapi.ws_close_waveshaper(self.name)
        wsapi.ws_delete_waveshaper(self.name)

    def execute(self):
        # Load the desired profile according to the specifications
        profiletext = ""
        freq = 299792.458 / self.wavelength
        startfreq = freq - self.bandwidth * 0.5 * 1e-3  # startfreq in THz
        stopfreq = freq + self.bandwidth * 0.5 * 1e-3  # stropfreq in THz

        for frequency in np.arange(191.250, 196.274, 0.001, dtype=float):
            for k in range(1):
                if self.wavelength[k] > 1 and frequency > startfreq[k] and frequency < stopfreq[k]:
                    profiletext = profiletext + "%.3f %.1f %.1f %d\n" % (
                    frequency, self.attenuation[k], self.phase[k], k + 1)
                else:
                    profiletext = profiletext + "%.3f 60.0 0.0 0\n" % (frequency)

        rc = wsapi.ws_load_profile(self.name, profiletext)
        if rc < 0:
            print wsapi.ws_get_result_description(rc)

    def execute_wss(profile):
        # Load the desired profile according to the specifications
        profiletext = ""

        for frequency in np.arange(191.250, 196.274, 0.001, dtype=float):
            profiletext = profiletext + "%.3f %.1f %.1f %d\n" % (frequency, profile, 0, 1)

        rc = wsapi.ws_load_profile(self.name, profiletext)
        if rc < 0:
            print wsapi.ws_get_result_description(rc)


class nettest():
    def __init__(self):
        self.open()

    def open(self):
        # Set IP address of GPIB-ETHERNET
        ip = '10.1.1.7'

        # Set GPIB address
        addr = '10'
        # Open TCP connect to poet 1234 of GPIB-ETHERNET
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.sock.settimeout(0.1)
        self.sock.connect((ip, 1234))

        # Set mode as CONTROLLER
        self.sock.send("++mode 1\n")

        # Set TUNICS GPIB address
        self.sock.send("++addr " + addr + "\n")

        # Turn off read-after-write to avoid "Query Unterminated" errors
        self.sock.send("++auto 0\n")

        # Read timeout is 500 msec
        self.sock.send("++read_tmo_ms 500\n")

        # Do not append CR or LF to GPIB data
        self.sock.send("++eos 3\n")

        # Assert EOI with last byte to indicate end of data
        self.sock.send("++eoi 1\n")

    def wavelength(self, l):
        # SCPI command
        cmd = ":SOURce:WAVelength %.3f nm;" % l  # Change wavelength
        self.sock.send(cmd + "\n")

        time.sleep(1.0)

    def power(self, p):
        cmd = ":SOURce:POWer:UNI DBM;"  # Change power units to dBm
        self.sock.send(cmd + "\n")
        cmd = ":SOUR:POW %.2f;" % p  # Change power value
        self.sock.send(cmd + "\n")
        time.sleep(1.0)

    def state(self, enable):
        cmd = ":SOUR:POW:STAT %d;" % enable  # Change the power state (on/off 1/0)
        self.sock.send(cmd + "\n")
        time.sleep(1.0)

    def checkfreq(self):
        self.sock.send(":SOUR:FREQ?\n")
        self.sock.send("++read eoi\n")
        time.sleep(1.0)
        s = None

        try:
            s = self.sock.recv(100)
        except socket.timeout:
            s = ""
        # print s
        return float(s)

    def setfreq(self, freq):
        cmd = ":SOUR:FREQ %d HZ;" % freq  # Change the frequency Hz
        self.sock.send(cmd + "\n")
        time.sleep(1.0)

    def close(self):
        self.sock.close()

    def checkerror(self):
        self.sock.send("SYST:ERR?\n")
        self.sock.send("++read eoi\n")

        s = None

        try:
            s = self.sock.recv(100)
        except socket.timeout:
            s = ""

        print s


def acquire(channel_ID, npoints, fs):
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


def acquire_complex(channel_ID, npoints, fs):
    dpo = visa.instrument("TCPIP::10.1.1.14::4000::SOCKET")

    # Make a single acquisition
    dpo.write('ACQUIRE:STOPAFTER SEQUENCE')
    dpo.write('ACQUIRE:STATE 1')

    dpo.close()

    # Then request the signals acquired at the same time
    Icompx = acquire(channel_ID[0], npoints, fs)
    Qcompx = acquire(channel_ID[1], npoints, fs)
    Icompy = acquire(channel_ID[2], npoints, fs)
    Qcompy = acquire(channel_ID[3], npoints, fs)

    return (Icompx, Qcompx, Icompy, Qcompy)


def generate(channel_ID, tempfile, fs, path, DACres=10):
    awg = visa.instrument("TCPIP::10.1.1.20::4000::SOCKET")
    waveform_name = 'temp'
    waveform_name = tempfile
    # path="Z:\EOS_experiments\Components_characterization\20140117_CoherentRxAssembly"
    # datastring=np.array2string(data)

    print "Generating channel %d from %s" % (channel_ID, awg.ask('*IDN?'))

    # Set the sampling rate

    # Set the resolution of the DAC
    awg.write('SOURCE%d:DAC:RES %d' % (channel_ID, DACres))

    # Set the output waveform
    # awg.write('WLIST:WAVEFORM:NEW \"%s\", %d, INT' % (waveform_name, data.size))

    awg.write('MMEM:MSIS \"Z:\"')
    # wg.write('MMEM:CDIR \"/EOS_experiments/CO-OFDM/IQ-OFDM\"')
    awg.write('MMEM:CDIR \"%s\"' % path)

    awg.write('MMEM:IMPORT:PAR:NORM FSC')

    # awg.write('MMEM:IMPORT \"TEMP\", \"%s\", txt' %  tempfile)
    awg.write('MMEM:IMPORT \"%s\", \"%s\", txt' % (waveform_name, tempfile))

    awg.write('SOURCE%d:FREQ %f' % (channel_ID, fs))
    # awg.write('WLIST:WAVEFORM:DATA %s, %s'% (waveform_name, datastring))
    awg.write('SOURCE%d:WAVEFORM \"%s\"' % (channel_ID, waveform_name))

    # Run
    awg.write('AWGCONTROL:RUN')

    # Set ON/OFF the outputs
    awg.write('OUTPUT%d:STATE 1' % channel_ID)

    awg.close()


def generate_intlv(tempfile, fs, path, DACres=10, phase=5):
    awg = visa.instrument("TCPIP::10.1.1.20::4000::SOCKET")

    print "Generating interleaved channel on %s" % (awg.ask('*IDN?'))

    awg.write('AWGCONTROL:INTERLEAVE 1')

    awg.write('AWGCONTROL:INTERLEAVE:ADJUSTMENT:PHASE %d' % (phase))

    awg.close()

    generate(1, tempfile, fs, path, DACres)


def acquire_csa(fs, npoints):
    result = np.zeros((4, npoints), dtype=float)

    csa = visa.instrument("TCPIP::10.1.1.17::INSTR")

    print csa.ask('*IDN?')

    # csa.write('HOR:MODE:RECO %d' % npoints) # Set the record length to npoints
    csa.write('ACQUIRE:REPET 0')  # Set the OSC to realtime
    csa.write('HORIZONTAL:RECORDLENGTH %d' % npoints)
    # csa.write('HORIZONTAL:MAIN:INTERPRATIO 1') # Set the sample rate to fs
    csa.write('HORIZONTAL:MAIN:SAMPLERATE %.2f' % fs)

    # print csa.ask('HORIZONTAL:MAIN:SAMPLERATE?')
    # print csa.ask('HORIZONTAL?')
    # print "Acquiring from %s" % csa.ask('*IDN?')
    csa.write('ACQuire:STOPAfter SEQUENCE')
    csa.write('ACQUIRE:STATE ON')

    csa.write('DAT:ENC ASCII')
    csa.write('DAT:STAR %d' % 1)
    csa.write('DAT:STOP %d' % npoints)

    for kch in range(4):
        csa.write('DAT:SOU CH%d' % (kch + 1))
        aux = np.fromstring(csa.ask('CURV?')[7:-1], dtype=float, sep=',')
        result[kch][0:aux.size] = aux
    csa.close()

    return result


# create logger
log = logging.getLogger(__name__)

if (len(log.handlers) == 0):  # check if the logger already exists
    # create logger
    log.setLevel(logging.INFO)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    log.addHandler(ch)


class BOSA:
    """ class OSA: driver used to communicate with OSA equipment"""

    def __init__(self, interfaceType, location, portNo=10000, IDN=True, Reset=False):
        """create the OSA object and tries to establish a connection with the equipment
            Parameters:
                interfaceType -> LAN, GPIB interface utilyzed in connection
                location      -> IP address or GPIB address of equipment.
                portN         -> no of the port where the interface is open (LAN)
        """
        self.interfaceType = interfaceType
        self.location = location
        self.portNo = portNo

        self.activeTrace = None

        if (interfaceType.lower() == "lan"):

            log.info("Connection to OSA using Lan interface on %r", location)
            try:
                self.connectLan()
            except Exception as e:
                log.exception("Could not connect to OSA device")
                print e
                raise e
                return
        elif (interfaceType.lower() == "gpib"):
            log.info("GPIB interface chosen to connect OSA on %r", location)
            try:
                self.interface = visa.GpibInstrument(location)
            except Exception as e:
                log.exception("couldn't connect to device")
                print e
                raise e
                return
            log.info("Connected to device.")
        else:
            log.error("Interface Type " + interfaceType + " not valid")
            raise Exception("interface type invalid")
            return
        if (IDN):
            try:
                log.debug("Sending IDN to device...")
                self.write("*IDN?")
            except Exception as e:
                log.exception("Could not send *IDN? device")
                print e
                raise e

            log.debug("IDN send, waiting response...")
            try:
                response = self.read()
            except Exception as e:
                log.exception("Could read response from device")
                print e
                raise e

            print("IDN= " + response)

        if (Reset):
            try:
                log.info("resting device")
                self.write("*RST")
            except Exception as e:
                log.exception("Could not reset device")
                print e
                raise e

    def __del__(self):
        try:
            if (self.interfaceType == "LAN"):
                self.interface.close()
            elif (self.interfaceType == "GPIB"):
                self.interface.close()
        except Exception as e:
            log.warning("could not close interface correctly: exception %r", e.message)

    def connectLan(self):
        """ connect the instrument to a LAN """
        log.debug("creating socket")
        self.interface = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.interface.settimeout(30)
        try:
            log.debug("Connecting to remote socket...")
            self.interface.connect((self.location, self.portNo))
        except Exception as e:
            log.exception("Could not connection to remote socket")
            print e
            raise e

        log.debug("Connected to remote socket")
        log.info("OSA ready!")

    def write(self, command):
        """ write to equiment: independent of the interface
            Parameters:
                command -> data to send to device + \r\n
        """
        if (self.interfaceType.lower() == "lan"):
            log.debug("Sending command '" + command + "' using LAN interface...")
            try:
                self.interface.sendall(command + "\r\n")
            except Exception as e:
                log.exception("Could not send data, command %r", command)
                print e
                raise e
        elif (self.interfaceType.lower() == "gpib"):
            log.debug("Sending command '" + command + "' using GPIB interface...")
            try:
                self.interface.write(command + "\r\n")
            except Exception as e:
                log.exception("Could not send data, command %r", command)
                print e
                raise e

    def read(self):
        """ read something from device"""
        message = ""
        if (self.interfaceType.lower() == "lan"):
            log.debug("Reading data using LAN interface...")
            while (1):
                try:
                    message += self.interface.recv(19200)
                except Exception as e:
                    log.exception("Could not read data")
                    print e
                    raise e
                if ("\n" in message):
                    break
            log.debug("All data readed!")
        elif (self.interfaceType.lower() == "gpib"):
            log.debug("Reading data using GPIB interface...")
            while (1):
                try:
                    message = self.interface.read()
                except Exception as e:
                    log.exception("Could not read data")
                    print e
                    raise e
                if ("\n" in message):
                    break
            log.debug("All data readed!")
        log.debug("Data received: " + message)
        return message

    def ask(self, command):
        """ writes and reads data"""
        data = ""
        self.write(command)
        data = self.read()
        return data


class agilentmeter():
    def __init__(self):
        self.open()

    def open(self):
        # Set IP address of GPIB-ETHERNET
        ip = '10.1.1.9'

        # Set GPIB address
        addr = '10'
        # Open TCP connect to port 1234 of GPIB-ETHERNET
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.sock.settimeout(0.1)
        self.sock.connect((ip, 1234))

        # Set mode as CONTROLLER
        self.sock.send("++mode 1\n")

        # Set GPIB address
        self.sock.send("++addr " + addr + "\n")

        # Turn off read-after-write to avoid "Query Unterminated" errors
        self.sock.send("++auto 0\n")

        # Read timeout is 500 msec
        self.sock.send("++read_tmo_ms 500\n")

        # Do not append CR or LF to GPIB data
        self.sock.send("++eos 3\n")

        # Assert EOI with last byte to indicate end of data
        self.sock.send("++eoi 1\n")

    def test(self):
        self.sock.send("*IDN?\n")
        self.sock.send("++read eoi\n")
        try:
            s = self.sock.recv(100)
        except socket.timeout:
            s = ""
        print s

    def power(self):
        s = ""
        while s == "":
            self.sock.send(":READ1:POW?\n")
            self.sock.send("++read eoi\n")
            try:
                s = self.sock.recv(1000)
            except socket.timeout:
                s = ""
            time.sleep(1.0)
        return float(s)

    def attenuation(self):
        s = ""
        while s == "":
            self.sock.send(":INP2:ATT?\n")
            self.sock.send("++read eoi\n")
            try:
                s = self.sock.recv(1000)
            except socket.timeout:
                s = ""
            time.sleep(1.0)
        return float(s)

    def set_attenuation(self, atten):
        self.sock.send(":INP2:ATT " + str(atten) + "\n")
        self.sock.send("++read eoi\n")

    def close(self):
        self.sock.close()

    def checkerror(self):
        self.sock.send("SYST:ERR?\n")
        self.sock.send("++read eoi\n")

        s = None

        try:
            s = self.sock.recv(100)
        except socket.timeout:
            s = ""

        print s


class agilentpsupply():
    def __init__(self):
        self.open()

    def open(self):
        # Set IP address of GPIB-ETHERNET
        ip = '10.1.1.4'

        # Set GPIB address
        addr = '5'
        # Open TCP connect to port 1234 of GPIB-ETHERNET
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.sock.settimeout(0.1)
        self.sock.connect((ip, 1234))

        # Set mode as CONTROLLER
        self.sock.send("++mode 1\n")

        # Set GPIB address
        self.sock.send("++addr " + addr + "\n")

        # Turn off read-after-write to avoid "Query Unterminated" errors
        self.sock.send("++auto 0\n")

        # Read timeout is 1 sec
        self.sock.send("++read_tmo_ms 1000\n")

        # Do not append CR or LF to GPIB data
        self.sock.send("++eos 3\n")

        # Assert EOI with last byte to indicate end of data
        self.sock.send("++eoi 1\n")

    def test(self):
        self.sock.send("*IDN?\n")
        self.sock.send("++read eoi\n")
        try:
            s = self.sock.recv(100)
        except socket.timeout:
            s = ""
        print s

    def status(self):
        self.sock.send("OUTP?\n")
        self.sock.send("++read eoi\n")
        try:
            s = self.sock.recv(100)
        except socket.timeout:
            s = ""
        return int(s)

    def enable(self, status):
        # enable / disable
        # input: status 1/0
        cmd = "OUTP %d\n" % status  # Change the power state (on/off 1/0)
        self.sock.send(cmd)
        self.sock.send("++read eoi\n")

    def write(self, channel, voltage):
        cmd = "INST:NSEL %d\n" % channel  # select the channel (1 or 2)
        self.sock.send(cmd)
        self.sock.send("++read eoi\n")
        cmd = "VOLT %.2f\n" % voltage  # set the voltage of the selected channel
        self.sock.send(cmd)
        self.sock.send("++read eoi\n")

    def close(self):
        self.sock.close()

    def checkerror(self):
        self.sock.send("SYST:ERR?\n")
        self.sock.send("++read eoi\n")

        s = None

        try:
            s = self.sock.recv(100)
        except socket.timeout:
            s = ""

        print s


class ando():
    def __init__(self):
        self.open()

    def open(self):
        # Set IP address of GPIB-ETHERNET
        ip = '10.1.1.21'

        # Set GPIB address
        addr = '2'
        # Open TCP connect to port 1234 of GPIB-ETHERNET
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.sock.settimeout(0.1)
        self.sock.connect((ip, 1234))

        # Set mode as CONTROLLER
        self.sock.send("++mode 1\n")

        # Set GPIB address
        self.sock.send("++addr " + addr + "\n")

        # Turn off read-after-write to avoid "Query Unterminated" errors
        self.sock.send("++auto 0\n")

        # Read timeout is 500 msec
        self.sock.send("++read_tmo_ms 500\n")

        # Do not append CR or LF to GPIB data
        self.sock.send("++eos 3\n")

        # Assert EOI with last byte to indicate end of data
        self.sock.send("++eoi 1\n")

    def test(self):

        self.sock.send("*IDN?\n")
        self.sock.send("++read eoi\n")
        try:
            s = self.sock.recv(100)
        except socket.timeout:
            s = ""

        print s

    def trace(self):
        s = ""
        while s == "":
            self.sock.send("LDATA\n")
            self.sock.send("++read eoi\n")
            try:
                s = self.sock.recv(100000)
            except socket.timeout:
                s = ""
            time.sleep(1.0)
        return np.fromstring(s, dtype=float, sep=',')

    def wav(self):
        s = ""
        while s == "":
            self.sock.send("WDATA\n")
            self.sock.send("++read eoi\n")
            try:
                s = self.sock.recv(100000)
            except socket.timeout:
                s = ""
            time.sleep(1.0)
        return np.fromstring(s, dtype=float, sep=',')

    def close(self):
        self.sock.close()

    def checkerror(self):
        self.sock.send("SYST:ERR?\n")
        self.sock.send("++read eoi\n")

        s = None

        try:
            s = self.sock.recv(100)
        except socket.timeout:
            s = ""

        print s


class yenista():
    def __init__(self):
        self.open()

    def open(self):
        # Set IP address of GPIB-ETHERNET
        ip = '10.1.1.7'

        # Set GPIB address
        addr = '11'
        # Open TCP connect to port 1234 of GPIB-ETHERNET
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.sock.settimeout(0.1)
        self.sock.connect((ip, 1234))

        # Set mode as CONTROLLER
        self.sock.send("++mode 1\n")

        # Set GPIB address
        self.sock.send("++addr " + addr + "\n")

        # Turn off read-after-write to avoid "Query Unterminated" errors
        self.sock.send("++auto 0\n")

        # Read timeout is 500 msec
        self.sock.send("++read_tmo_ms 500\n")

        # Do not append CR or LF to GPIB data
        self.sock.send("++eos 3\n")

        # Assert EOI with last byte to indicate end of data
        self.sock.send("++eoi 1\n")

    def test(self):

        self.sock.send("*IDN?\n")
        self.sock.send("++read eoi\n")
        try:
            s = self.sock.recv(100)
        except socket.timeout:
            s = ""

        print s

    def wavelength(self, ch, lambda0):
        cmd = "CH%d:NM" % ch
        self.sock.send(cmd + "\n");  # set units in nm
        cmd = "CH%d:L=%.3f" % (ch, lambda0)
        self.sock.send(cmd + "\n");  # set wavelength

    def power(self, ch, power):
        cmd = "CH%d:DBM" % ch
        self.sock.send(cmd + "\n");  # set units in dBm
        cmd = "CH%d:P=%.3f" % (ch, power)
        self.sock.send(cmd + "\n");  # set power

    def status(self, ch, stat=False):
        if (stat == True):
            cmd = "CH%d:ENABLE" % ch
            self.sock.send(cmd + "\n");  # enable laser
        else:
            cmd = "CH%d:DISABLE" % ch
            self.sock.send(cmd + "\n");  # disable laser

    def close(self):
        self.sock.close()

    def checkerror(self):
        self.sock.send("SYST:ERR?\n")
        self.sock.send("++read eoi\n")

        s = None

        try:
            s = self.sock.recv(100)
        except socket.timeout:
            s = ""

        print s


class manlight():
    def __init__(self):
        self.open()

    def open(self):
        # Set IP address of GPIB-ETHERNET
        ip = '10.1.1.15'

        # Set GPIB address
        addr = '3'
        # Open TCP connect to port 1234 of GPIB-ETHERNET
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.sock.settimeout(1)  # readjusted the timeout in order to allow a propper GPIB -> Eth conversion
        self.sock.connect((ip, 1234))

        # Set mode as CONTROLLER
        self.sock.send("++mode 1\n")

        # Set GPIB address
        self.sock.send("++addr " + addr + "\n")

        # Turn off read-after-write to avoid "Query Unterminated" errors
        self.sock.send("++auto 0\n")

        # Read timeout is 500 msec
        self.sock.send("++read_tmo_ms 500\n")

        # Do not append CR or LF to GPIB data
        self.sock.send("++eos 3\n")

        # Assert EOI with last byte to indicate end of data
        self.sock.send("++eoi 1\n")

    def test(self):

        self.sock.send("*IDN?\n")
        self.sock.send("++read eoi\n")
        try:
            s = self.sock.recv(100)
        except socket.timeout:
            s = ""

        print s

    def status(self, stat=False):

        if (stat == True):
            self.sock.send("POW:ON\n");  # enable EDFA
        else:
            self.sock.send("POW:OFF\n");  # disable EDFA
        time.sleep(1)

    def mode(self, mod, param=0):
        if (mod == "AGC"):
            self.sock.send("MODE:AGC\n");  # set the mode to AGC
            cmd = "SEL:GM:%.2f\n" % param
            time.sleep(1)
            self.sock.send(cmd + "\n");  # set the gain
        elif (mod == "APC"):
            self.sock.send("MODE:APC\n");  # set the mode to APC
            cmd = "SEL:PM:%.2f\n" % param
            time.sleep(1)
            self.sock.send(cmd + "\n");  # set the power

    def close(self):
        self.sock.close()

    def checkerror(self):
        self.sock.send("SYST:ERR?\n")
        self.sock.send("++read eoi\n")

        s = None

        try:
            s = self.sock.recv(100)
        except socket.timeout:
            s = ""

        print s


if __name__ == '__main__':
    edfa = manlight()
    edfa.test()
    edfa.status(False)
    edfa.mode("AGC", 30)
    edfa.close()
