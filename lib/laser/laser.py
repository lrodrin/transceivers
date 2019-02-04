"""This is the Laser module.

This module does stuff.
"""
import socket

# TODO import logging


class Laser:
    """
    This is a class for Laser module.
    """
    # TODO Laia's review
    # TODO documentar variables de la classe
    # TODO es podria fer un constants.py
    connection_port = 1234
    connection_timeout = 1
    mode = "++mode 1\n"
    read_after_write = "++auto 0\n"
    read_timeout = "++read_tmo_ms 500\n"
    eoi_1 = "++eoi 1\n"
    eos_3 = "++eos 3\n"

    buffer_size = 100
    read_eoi = "++read eoi\n"

    def __init__(self, ip, addr):
        """
        The constructor for the Laser class.

        :param ip: IP address of GPIB-ETHERNET
        :type ip: str
        :param addr: GPIB address
        :type addr: str
        """
        self.ip = ip
        self.addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.connect_and_initialization()

    def connect_and_initialization(self):
        """
        Open TCP connection to connection port of Laser IP address of GPIB-ETHERNET and initialize the Laser default
        parameters:

            - mode (str): Set mode as CONTROLLER.
            - addr_GPIB (str): Set GPIB address.
            - read_after_write (str): Turn off read-after-write to avoid "Query Unterminated" errors.
            - read_timeout (str): Read timeout is 500 ms.
            - eos_3 (str): Do not append CR or LF to GPIB data.
            - eoi_1 (str): Assert EOI with last byte to indicate end of data.
        """
        # Connection
        self.sock.settimeout(Laser.connection_timeout)
        ip = self.ip
        port = Laser.connection_port
        try:
            self.sock.connect((ip, port))
            print("Connection to laser {} on port {} opened".format(ip, port))
        except socket.error as e:
            print("ERROR: connection to laser refused, {}".format(e))

        # Initialization
        try:
            print("Init default parameters")
            self.sock.send(Laser.mode)
            addr_GPIB = "++addr " + self.addr + "\n"
            self.sock.send(addr_GPIB)
            self.sock.send(Laser.read_after_write)
            self.sock.send(Laser.read_timeout)
            self.sock.send(Laser.eos_3)
            self.sock.send(Laser.eoi_1)
        except socket.error as e:
            print("ERROR: in initialization default parameters, {}".format(e))

    def test(self):
        """
        Just as test, ask for instrument ID according to SCPI API.

        :return: instrument ID (e.g NetTest, OSICS, 0, 3.01)
        :rtype: str
        """
        try:
            self.sock.send("*IDN?\n")
            self.sock.send(Laser.read_eoi)
            return self.sock.recv(Laser.buffer_size)
        except socket.error as e:
            print("ERROR: testing, {}".format(e))

    def wavelength(self, ch, lambda0):
        """
        Define the wavelength of the Laser in nm.
        The range of wavelength takes 1527'55899 to 1565'544 nm.

        :param ch: channel
        :type ch: int
        :param lambda0: wavelength
        :type lambda0: float
        """
        try:
            print("Set wavelength %s" % lambda0)
            self.sock.send("CH%d:NM\n" % ch)  # set units in nm
            self.sock.send("CH%d:L=%.3f\n" % (ch, lambda0))
        except socket.error as e:
            print("ERROR: wavelength not configured, {}".format(e))

    def power(self, ch, power):
        """
        Define the power of the Laser in dBm.
        The range of power takes 6'03 to 14'50 dBm.

        :param ch: channel
        :type ch: int
        :param power: power
        :type power: float
        """
        try:
            print("Set power %s" % power)
            self.sock.send("CH%d:DBM\n" % ch)  # set units in dBm
            self.sock.send("CH%d:P=%.3f\n" % (ch, power))
        except socket.error as e:
            print("ERROR: power not configured, {}".format(e))

    def enable(self, ch, stat=False):
        """
        Enable or Disable the Laser.

        :param ch: channel
        :type ch: int
        :param stat: status
        :type stat: bool
        """
        msg = "Set status %s"
        if stat:
            print(msg % stat)
            try:
                self.sock.send("CH%d:ENABLE\n" % ch)
            except socket.error as e:
                print("ERROR: can't enable, {}".format(e))
        else:
            print(msg % stat)
            try:
                self.sock.send("CH%d:DISABLE\n" % ch)
            except socket.error as e:
                print("ERROR: can't disable, {}".format(e))

    def status(self, ch):
        """
        Check and return the Laser configured parameters:

            - Check status (enable/disable) and put it into the variable 'status' (True/False).
            - Check wavelength and put it into the variable 'wavelength' in nm.
            - Check power and put it into the variable 'power' in dBm (-60 indicates DISABLED).

        :param ch: channel
        :type ch: int
        :return: status, wavelength, power oh the Laser
        :rtype: list
        """
        status = False
        wavelength = 0.00
        power = 0.00

        # Check status
        try:
            self.sock.send("CH%d:ENABLE?\n" % ch)
            self.sock.send(Laser.read_eoi)
            s = self.sock.recv(Laser.buffer_size)
            if s.split(":")[1] == "ENABLED\n":
                status = True
        except socket.error as e:
            print("ERROR: checking status, {}".format(e))

        # Check wavelength
        try:
            self.sock.send("CH%d:L?\n" % ch)
            self.sock.send(Laser.read_eoi)
            s = self.sock.recv(Laser.buffer_size)
            wavelength = float(s.split("=")[1])
        except socket.error as e:
            print("ERROR: checking wavelength, {}".format(e))

        # Check power
        try:
            self.sock.send("CH%d:P?\n" % ch)
            self.sock.send(Laser.read_eoi)
            s = self.sock.recv(Laser.buffer_size)
            if status:
                power = float(s.split("=")[1])
            else:
                power = -60
        except socket.error as e:
            print("ERROR: checking power, {}".format(e))

        return [status, wavelength, power]

    def close(self):
        """
        Close and delete connection of the Laser.
        """
        try:
            print("Connection to laser closed")
            self.sock.close()
        except socket.error as e:
            print("ERROR: connection not closed, {}".format(e))

    def checkerror(self):
        """
        Check system errors in the Laser.

        # TODO define return
        :return: ?
        :rtype: str
        """
        try:
            self.sock.send("SYST:ERR?\n")
            self.sock.send(Laser.read_eoi)
            return self.sock.recv(Laser.buffer_size)
        except socket.error as e:
            print("ERROR: system error, {}".format(e))
