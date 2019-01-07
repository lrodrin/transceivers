from __future__ import print_function

from socket import SOCK_STREAM, IPPROTO_TCP, socket, AF_INET, timeout


# import time


class Laser:
    """
    This is a class for Laser configuration.

    """

    def __init__(self):
        """
        The constructor for Laser class.

        """
        self.open()

    def open(self):
        """
        The function to initialize the Laser default parameters:
            - Set IP address of GPIB-ETHERNET
            - Set GPIB address
            - Set mode as CONTROLLER
            - Set GPIB address

        """

        # Set IP address of GPIB-ETHERNET
        ip = '10.1.1.7'

        # Set GPIB address
        addr = '11'

        # Open TCP connect to port 1234 of GPIB-ETHERNET
        self.sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        self.sock.settimeout(1)
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
        """
        Just as test, ask for instrument ID according to SCPI API

        :return: s
        """
        self.sock.send("*IDN?\n")
        self.sock.send("++read eoi\n")
        s = None
        # TODO local variable s is not used
        try:
            s = self.sock.recv(100)

        except timeout:
            s = ""

        return s

    def wavelength(self, ch, lambda0):
        """
        Define wavelength in nm

        :param ch: channel
        :param lambda0: wavelength
        :type ch: int
        :type lambda0: float
        """
        cmd = "CH%d:NM" % ch
        self.sock.send(cmd + "\n")  # set units in nm
        cmd = "CH%d:L=%.3f" % (ch, lambda0)
        self.sock.send(cmd + "\n")  # set wavelength

    def power(self, ch, power):
        """
        Define power in dBm

        :param ch: channel
        :param power: power
        :type ch: int
        :type power: float
        """
        cmd = "CH%d:DBM" % ch
        self.sock.send(cmd + "\n")  # set units in dBm
        cmd = "CH%d:P=%.3f" % (ch, power)
        self.sock.send(cmd + "\n")  # set power

    def enable(self, ch, stat=False):
        """
        Enable / Disable Laser

        :param ch: channel
        :param stat: status
        :type ch: int
        :type stat: bool
        """
        if stat:
            cmd = "CH%d:ENABLE" % ch
            self.sock.send(cmd + "\n")  # enable laser
        else:
            cmd = "CH%d:DISABLE" % ch
            self.sock.send(cmd + "\n")  # disable laser

    def status(self, ch):
        """
            - Check status (enable/disable) and put it into the variable 'stat' (True/False)
            - Check wavelength and put it into the variable 'lambda0' in nm
            - Check power and put it into the variable 'power' in dBm (-60 indicates DISABLED)

        :param ch: channel
        :type ch: int
        :rtype: list
        :return: status, wavelength, power
        """
        # Check status (enable/disable) and put it into the variable 'stat' (True/False)
        cmd = "CH%d:ENABLE?\n" % ch
        self.sock.send(cmd)
        self.sock.send("++read eoi\n")
        s = None
        # TODO local variable s is not used
        try:
            s = self.sock.recv(100)

        except timeout:
            s = ""

        if str.split(s, ":")[1] == "ENABLED\n":
            stat = True
        else:
            stat = False

        # Check wavelength and put it into the variable 'lambda0' in nm
        cmd = "CH%d:L?\n" % ch
        self.sock.send(cmd)
        self.sock.send("++read eoi\n")
        s = None
        # TODO local variable s is not used
        try:
            s = self.sock.recv(100)

        except timeout:
            s = ""

        lambda0 = float(str.split(s, "=")[1])

        # Check power and put it into the variable 'power' in dBm (-60 indicates DISABLED)
        cmd = "CH%d:P?\n" % ch
        self.sock.send(cmd)
        self.sock.send("++read eoi\n")
        s = None
        # TODO local variable s is not used
        try:
            s = self.sock.recv(100)

        except timeout:
            s = ""
        if stat:
            power = float(str.split(s, "=")[1])
        else:
            power = -60

        # Return status, wavelength, power
        return [stat, lambda0, power]

    def close(self):
        """
        Close and delete the laser

        """
        self.sock.close()

    def checkerror(self):
        """
        Check system error

        :return: s
        """
        self.sock.send("SYST:ERR?\n")
        self.sock.send("++read eoi\n")
        s = None
        # TODO local variable s is not used
        try:
            s = self.sock.recv(100)

        except timeout:

            s = ""

        return s

# if __name__ == '__main__':
#     yenista = Laser()
#     yenista.wavelength(3, 1550.12)
#     yenista.power(3, 14.5)
#     yenista.enable(3, True)
#     time.sleep(5)
#     print(yenista.status(3)[0])
#     print(yenista.test())
#     yenista.close()
