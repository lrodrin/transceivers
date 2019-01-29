"""This is the Amplifier module.

This module does stuff.
"""
# import string
import time
import socket


class Amplifier:
    """
    This is a class for Amplifier module.

    """
    buffer_size = 100
    read_eoi = "++read eoi\n"
    connection_port = 1234
    connection_timeout = 2
    eoi_1 = "++eoi 1\n"
    eos_3 = "++eos 3\n"
    read_timeout = "++read_tmo_ms 500\n"
    read_after_write = "++auto 0\n"
    controller_mode = "++mode 1\n"

    def __init__(self, ip, addr):
        """
        The constructor for the Amplifier class.

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
        Connect to Amplifier and initialize the Amplifier default parameters:

            - mode (str): Set mode as CONTROLLER.
            - addr_GPIB (str): Set GPIB address.
            - read_after_write (str): Turn off read_after_write to avoid "Query Unterminated" errors.
            - read_timeout (str): Read timeout is 500 ms.
            - eos_3 (str): Do not append CR or LF to GPIB data.
            - eoi_1 (str): Assert eoi_1 with last byte to indicate end of data.
        """
        # connection
        self.sock.settimeout(Amplifier.connection_timeout)
        self.sock.connect((self.ip, Amplifier.connection_port))
        # initialization
        self.sock.send(Amplifier.controller_mode)
        addr_GPIB = "++addr " + self.addr + "\n"
        self.sock.send(addr_GPIB)
        self.sock.send(Amplifier.read_after_write)
        self.sock.send(Amplifier.read_timeout)
        self.sock.send(Amplifier.eos_3)
        self.sock.send(Amplifier.eoi_1)

    def test(self):
        """
        Just as test, ask for instrument ID according to SCPI API.

        :return: amplifier type, band type and software release (e.g EDFA C Band, V2.1)
        :rtype: str
        """
        self.sock.send("*IDN?\n")
        self.sock.send(Amplifier.read_eoi)
        try:
            instrument_id = self.sock.recv(Amplifier.buffer_size)

        except socket.timeout:
            instrument_id = ""

        return instrument_id

    def enable(self, stat=False):
        """
        Enable or Disable the Amplifier.

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
        Define power or gain for mode AGC, APC in dBm or current for mode ACC in mA.
        The range of gain in mode AGC takes 20 to 35 dBm.
        The range of power in mode APC takes 0 to 23'5 dBm.
        The range of current in mode ACC takes 0 to 1210 mA.

        :param mod: mode type
        :type mod: string
        :param param: power or gain
        :type param: int
        """
        if mod == "AGC":
            self.sock.send("mode:AGC\n")  # set the mode to AGC
            cmd = "SEL:GM:%.2f\n" % param
            time.sleep(1)
            self.sock.send(cmd + "\n")  # set the gain

        elif mod == "APC":
            self.sock.send("mode:APC\n")  # set the mode to APC
            cmd = "SEL:PM:%.2f\n" % param
            time.sleep(1)
            self.sock.send(cmd + "\n")  # set the power

        elif mod == "ACC":
            self.sock.send("mode:ACC\n")  # set the mode to ACC
            cmd = "SEL:IL1:%.2f\n" % param
            time.sleep(1)
            self.sock.send(cmd + "\n")  # set the current

    def status(self):
        """
        Check and return the Amplifier configured parameters:

            - Check mode (power/gain) and put it into the variable 'param' as float.
            - Check status (enable/disable) and put it into the variable 'stat' (True/False).

        :return: status, mode, power
        :rtype list
        """
        # Check mode
        self.sock.send("mode\n")
        self.sock.send(Amplifier.read_eoi)
        try:
            s = self.sock.recv(Amplifier.buffer_size)
        except socket.timeout:
            s = ""

        # mod = string.split(s, " ")[1]  # store mode in variable 'mod' as string
        mod = s.split(" ")[1]  # store mode in variable 'mod' as string
        # param = float(string.split(s, " ")[2])  # store parameter (power/gain) in variable 'param' as float
        param = float(s.split(" ")[2])  # store parameter (power/gain) in variable 'param' as float

        # Check status
        self.sock.send("POW\n")
        self.sock.send(Amplifier.read_eoi)
        try:
            s = self.sock.recv(Amplifier.buffer_size)
        except socket.timeout:
            s = ""

        stat = False
        # if string.find(s, "OFF") == -1:
        if s.find("OFF") == -1:
            stat = True

        return [stat, mod, param]

    def close(self):
        """
        Close and delete the Amplifier connection.
        """
        self.sock.close()

    def checkerror(self):
        """
        Check system errors in the Amplifier.

        :return: s
        """
        self.sock.send("SYST:ERR?\n")
        self.sock.send("++read eoi\n")
        try:
            s = self.sock.recv(Amplifier.buffer_size)
        except socket.timeout:

            s = ""

        # TODO define s
        return s
