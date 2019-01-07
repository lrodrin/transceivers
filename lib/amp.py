from __future__ import print_function

import socket
import time


class Amp:
    """
    This is a class for Amplifier configuration.

    """

    def __init__(self, ip):
        """
        The constructor for Amp class.

        :param ip: IP address of GPIB-ETHERNET
        :type ip: string
        """
        self.ip = ip
        self.open()

    def open(self):
        """
        The function to initialize the Amp default parameters:
            - Set GPIB address
            - Set mode as CONTROLLER
            - Set GPIB address

        """

        # Set GPIB address
        addr = '3'

        # Open TCP connect to port 1234 of GPIB-ETHERNET
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.sock.settimeout(2)  # readjusted the timeout in order to allow a propper GPIB -> Eth conversion
        self.sock.connect((self.ip, 1234))

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

        except socket.timeout:
            s = ""

        return s

    def enable(self, stat=False):
        """
        Enable / Disable EDFA

        :param stat: status
        :type stat: bool
        """
        if stat:
            self.sock.send("POW:ON\n")  # enable EDFA
        else:
            self.sock.send("POW:OFF\n")  # disable EDFA

        time.sleep(1)

    def mode(self, mod, param=0):
        """
        Define mode AGC / APC

        :param mod: mode type
        :param param: power or gain
        :type mod: string
        :type param: int
        """
        if mod == "AGC":
            self.sock.send("MODE:AGC\n")  # set the mode to AGC
            cmd = "SEL:GM:%.2f\n" % param
            time.sleep(1)
            self.sock.send(cmd + "\n")  # set the gain

        elif mod == "APC":
            self.sock.send("MODE:APC\n")  # set the mode to APC
            cmd = "SEL:PM:%.2f\n" % param
            time.sleep(1)
            self.sock.send(cmd + "\n")  # set the power

    def status(self):
        """
            - Check mode (power/gain) and put it into the variable 'param' as float
            - Check status (enable/disable) and put it into the variable 'stat' (True/False)

        :rtype list
        :return: status, mode, power
        """
        # First ask for the mode
        self.sock.send("MODE\n")
        self.sock.send("++read eoi\n")
        s = None
        # TODO local variable s is not used
        try:
            s = self.sock.recv(100)

        except socket.timeout:
            s = ""

        mod = str.split(s, " ")[1]  # Store mode in variable 'mod' as string
        param = float(str.split(s, " ")[2])  # Store parameter (power/gain) in variable 'param' as float

        # Then ask for the status (enable/disable) and put it into the variable 'stat' (True/False)
        self.sock.send("POW\n")
        self.sock.send("++read eoi\n")
        s = None
        # TODO local variable s is not used
        try:
            s = self.sock.recv(100)

        except socket.timeout:
            s = ""

        stat = False
        if str.find(s, "OFF") == -1:
            stat = True

        # Return status, mode, power
        return [stat, mod, param]

    def close(self):
        """
            Close and delete the amplifier

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

        except socket.timeout:

            s = ""

        print(s)


# if __name__ == '__main__':
#     manlight_1 = Amp('10.1.1.15')
#     manlight_2 = Amp('10.1.1.16')
#     print(manlight_1.test())
#     print(manlight_2.test())
#     manlight_1.mode("APC", 5)
#     manlight_2.mode("APC", 3)
#     manlight_1.enable(True)
#     manlight_2.enable(True)
#     time.sleep(10)
#     print(manlight_1.status())
#     print(manlight_2.status())
#     manlight_1.close()
#     manlight_2.close()
