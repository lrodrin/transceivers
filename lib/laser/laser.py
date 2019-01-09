import socket
import time
import string

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


BUFSIZE = 100

READ_EOI = "++read eoi\n"

CONNECTION_PORT = 1234

CONNECTION_TIMEOUT = 1

EOS_1 = "++eoi 1\n"

EOS_3 = "++eos 3\n"

TIMEOUT = "++read_tmo_ms 500\n"

READ_AFTER_WRITE = "++auto 0\n"

MODE = "++mode 1\n"


class Laser:
    """
    This is a class for Laser configuration.

    """

    def __init__(self, ip, addr):
        """
        The constructor for Laser class.

        :param ip: IP address of GPIB-ETHERNET
        :param addr: GPIB address
        :type ip: str
        :type addr: str
        """
        self.ip = ip
        self.addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.open()

    def open(self):
        """
        Connect to Laser and initialize the Laser default parameters:

            - Set MODE as CONTROLLER.
            - Set GPIB address.
            - Turn off READ_AFTER_WRITE to avoid "Query Unterminated" errors.
            - Read timeout is 500 ms.
            - Do not append CR or LF to GPIB data.
            - Assert EOI with last byte to indicate end of data.

        """
        # connection
        self.sock.settimeout(CONNECTION_TIMEOUT)
        self.sock.connect((self.ip, CONNECTION_PORT))
        # change parameters
        self.sock.send(MODE)
        addr_GPIB = "++addr " + self.addr + "\n"
        self.sock.send(addr_GPIB)
        self.sock.send(READ_AFTER_WRITE)
        self.sock.send(TIMEOUT)
        self.sock.send(EOS_3)
        self.sock.send(EOS_1)

    def test(self):
        """
        Just as test, ask for instrument ID according to SCPI API

        :return: s
        """
        self.sock.send("*IDN?\n")
        self.sock.send(READ_EOI)
        try:
            s = self.sock.recv(BUFSIZE)

        except socket.timeout:
            s = ""

        # TODO define s
        # NetTest,OSICS,0,3.01
        return s

    def wavelength(self, ch, lambda0):
        """
        Define wavelength in nm.
        The range of wavelength takes 1527'55899 to 1565'544 nm.

        :param ch: channel
        :param lambda0: wavelength
        :type ch: int
        :type lambda0: float
        """
        self.sock.send("CH%d:NM\n" % ch)  # set units in nm
        self.sock.send("CH%d:L=%.3f\n" % (ch, lambda0))  # set wavelength

    def power(self, ch, power):
        """
        Define power in dBm.
        The range of power takes 6'03 to 14'50 dBm.

        :param ch: channel
        :param power: power
        :type ch: int
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
        :rtype: list
        :return: status, wavelength, power
        """

        # Check status
        self.sock.send("CH%d:ENABLE?\n" % ch)
        self.sock.send(READ_EOI)
        try:
            s = self.sock.recv(BUFSIZE)
        except socket.timeout:
            s = ""

        if string.split(s, ":")[1] == "ENABLED\n":
            stat = True
        else:
            stat = False

        # Check wavelength
        self.sock.send("CH%d:L?\n" % ch)
        self.sock.send(READ_EOI)
        try:
            s = self.sock.recv(BUFSIZE)
        except socket.timeout:
            s = ""

        lambda0 = float(string.split(s, "=")[1])

        # Check power
        self.sock.send("CH%d:P?\n" % ch)
        self.sock.send(READ_EOI)
        try:
            s = self.sock.recv(BUFSIZE)
        except socket.timeout:
            s = ""
        if stat:
            power = float(string.split(s, "=")[1])
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
        self.sock.send(READ_EOI)
        try:
            s = self.sock.recv(BUFSIZE)
        except socket.timeout:
            s = ""

        # TODO define s
        return s


if __name__ == '__main__':
    ip_eth = '10.1.1.7'
    addr_gpib = '11'
    yenista = Laser(ip_eth, addr_gpib)
    yenista.wavelength(3, 1550.12)
    yenista.power(3, 14.5)
    yenista.enable(3, True)
    time.sleep(5)
    print(yenista.status(3))
    print(yenista.test())
    yenista.close()
