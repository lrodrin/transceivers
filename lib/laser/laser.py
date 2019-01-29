"""This is the Laser module.

This module does stuff.
"""
import socket


# import string


class Laser:
    """
    This is a class for Laser module.
    """
    buffer_size = 100
    read_eoi = "++read eoi\n"
    connection_port = 1234
    connection_timeout = 1
    eoi_1 = "++eoi 1\n"
    eos_3 = "++eos 3\n"
    read_timeout = "++read_tmo_ms 500\n"
    read_after_write = "++auto 0\n"
    mode = "++mode 1\n"

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
        Connect to the Laser and initialize the Laser default parameters:

            - mode (str): Set mode as CONTROLLER.
            - addr_GPIB (str): Set GPIB address.
            - read_after_write (str): Turn off read_after_write to avoid "Query Unterminated" errors.
            - read_timeout (str): Read timeout is 500 ms.
            - eos_3 (str): Do not append CR or LF to GPIB data.
            - eoi_1 (str): Assert eoi_1 with last byte to indicate end of data.
        """
        # connection
        self.sock.settimeout(Laser.connection_timeout)
        self.sock.connect((self.ip, Laser.connection_port))
        # initialization
        self.sock.send(Laser.mode)
        addr_GPIB = "++addr " + self.addr + "\n"
        self.sock.send(addr_GPIB)
        self.sock.send(Laser.read_after_write)
        self.sock.send(Laser.read_timeout)
        self.sock.send(Laser.eos_3)
        self.sock.send(Laser.eoi_1)

    def test(self):
        """
        Just as test, ask for instrument ID according to SCPI API.

        :return: instrument ID (e.g NetTest, OSICS, 0, 3.01)
        :rtype: str
        """
        self.sock.send("*IDN?\n")
        self.sock.send(Laser.read_eoi)
        try:
            instrument_id = self.sock.recv(Laser.buffer_size)

        except socket.timeout:
            instrument_id = ""

        return instrument_id

    def wavelength(self, ch, lambda0):
        """
        Define wavelength in nm.
        The range of wavelength takes 1527'55899 to 1565'544 nm.

        :param ch: channel
        :type ch: int
        :param lambda0: wavelength
        :type lambda0: float
        """
        self.sock.send("CH%d:NM\n" % ch)  # set units in nm
        self.sock.send("CH%d:L=%.3f\n" % (ch, lambda0))  # set wavelength

    def power(self, ch, power):
        """
        Define power in dBm.
        The range of power takes 6'03 to 14'50 dBm.

        :param ch: channel
        :type ch: int
        :param power: power
        :type power: float
        """
        self.sock.send("CH%d:DBM\n" % ch)  # set units in dBm
        self.sock.send("CH%d:P=%.3f\n" % (ch, power))  # set power

    def enable(self, ch, stat=False):
        """
        Enable or Disable the Laser.

        :param ch: channel
        :param stat: status
        :type ch: int
        :type stat: bool
        """
        if stat:
            self.sock.send("CH%d:ENABLE\n" % ch)  # enable laser
        else:
            self.sock.send("CH%d:DISABLE\n" % ch)  # disable laser

    def status(self, ch):
        """
        Check and return the Laser configured parameters:

            - Check status (enable/disable) and put it into the variable 'stat' (True/False).
            - Check wavelength and put it into the variable 'lambda0' in nm.
            - Check power and put it into the variable 'power' in dBm (-60 indicates DISABLED).

        :param ch: channel
        :type ch: int
        :return: status, wavelength, power
        :rtype: list
        """

        # Check status
        self.sock.send("CH%d:ENABLE?\n" % ch)
        self.sock.send(Laser.read_eoi)
        try:
            s = self.sock.recv(Laser.buffer_size)
        except socket.timeout:
            s = ""

        # if string.split(s, ":")[1] == "ENABLED\n":
        if s.split(":")[1] == "ENABLED\n":
            stat = True
        else:
            stat = False

        # Check wavelength
        self.sock.send("CH%d:L?\n" % ch)
        self.sock.send(Laser.read_eoi)
        try:
            s = self.sock.recv(Laser.buffer_size)
        except socket.timeout:
            s = ""

        # lambda0 = float(string.split(s, "=")[1])
        lambda0 = float(s.split("=")[1])

        # Check power
        self.sock.send("CH%d:P?\n" % ch)
        self.sock.send(Laser.read_eoi)
        try:
            s = self.sock.recv(Laser.buffer_size)
        except socket.timeout:
            s = ""
        if stat:
            # power = float(string.split(s, "=")[1])
            power = float(s.split("=")[1])
        else:
            power = -60

        return [stat, lambda0, power]

    def close(self):
        """
        Close and delete the Laser connection.
        """
        self.sock.close()

    def checkerror(self):
        """
        Check system errors in the Laser.

        :return: s
        """
        self.sock.send("SYST:ERR?\n")
        self.sock.send(Laser.read_eoi)
        try:
            s = self.sock.recv(Laser.buffer_size)
        except socket.timeout:
            s = ""

        # TODO define s
        return s
