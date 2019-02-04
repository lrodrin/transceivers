"""This is the Amplifier module.

This module does stuff.
"""
import socket
import time
# TODO import logging


class Amplifier:
    """
    This is a class for Amplifier module.
    """
    # TODO Laia's review
    # TODO documentar variables de la classe
    # TODO es podria fer un constants.py
    connection_port = 1234
    connection_timeout = 2
    controller_mode = "++mode 1\n"
    read_after_write = "++auto 0\n"
    read_timeout = "++read_tmo_ms 500\n"
    eoi_1 = "++eoi 1\n"
    eos_3 = "++eos 3\n"

    buffer_size = 100
    read_eoi = "++read eoi\n"
    time_sleep = 10

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
        Open TCP connection to connection port of Amplifier IP address of GPIB-ETHERNET and initialize the Amplifier
        default parameters:

            - mode (str): Set mode as CONTROLLER.
            - addr_GPIB (str): Set GPIB address.
            - read_after_write (str): Turn off read-after-write to avoid "Query Unterminated" errors.
            - read_timeout (str): Read timeout is 500 ms.
            - eos_3 (str): Do not append CR or LF to GPIB data.
            - eoi_1 (str): Assert EOI with last byte to indicate end of data.
        """
        # Connection
        self.sock.settimeout(Amplifier.connection_timeout)
        ip = self.ip
        port = Amplifier.connection_port
        try:
            self.sock.connect((ip, port))
            print("Connection to amplifier {} on port {} opened".format(ip, port))
        except socket.error as e:
            print("ERROR: connection to amplifier refused, {}".format(e))

        # Initialization
        try:
            print("Init default parameters")
            self.sock.send(Amplifier.controller_mode)
            addr_GPIB = "++addr " + self.addr + "\n"
            self.sock.send(addr_GPIB)
            self.sock.send(Amplifier.read_after_write)
            self.sock.send(Amplifier.read_timeout)
            self.sock.send(Amplifier.eos_3)
            self.sock.send(Amplifier.eoi_1)
        except socket.error as e:
            print("ERROR: in initialization default parameters, {}".format(e))

    def test(self):
        """
        Just as test, ask for instrument ID according to SCPI API.

        :return: instrument ID (e.g EDFA C Band, V2.1)
        :rtype: str
        """
        try:
            self.sock.send("*IDN?\n")
            self.sock.send(Amplifier.read_eoi)
            return self.sock.recv(Amplifier.buffer_size)
        except socket.error as e:
            print("ERROR: testing, {}".format(e))

    def enable(self, stat=False):
        """
        Enable or Disable the Amplifier.

        :param stat: status
        :type stat: bool
        """
        msg = "Set status %s"
        if stat:
            print(msg % stat)
            try:
                self.sock.send("POW:ON\n")
            except socket.error as e:
                print("ERROR: can't enable, {}".format(e))
        else:
            print(msg % stat)
            try:
                self.sock.send("POW:OFF\n")
            except socket.error as e:
                print("ERROR: can't disable, {}".format(e))

        time.sleep(Amplifier.time_sleep)

    def mode(self, mod, param=0):
        """
        Define power or gain for mode AGC, APC in dBm or current for mode ACC in mA.
        The range of gain in mode AGC takes 20 to 35 dBm.
        The range of power in mode APC takes 0 to 23'5 dBm.
        The range of current in mode ACC takes 0 to 1210 mA.

        :param mod: mode
        :type mod: str
        :param param: power, gain or current
        :type param: float
        """
        try:
            print("Set mode %s" % mod)
            if mod == "AGC":
                self.sock.send("mode:AGC\n")
                cmd = "SEL:GM:%.2f\n" % param
                time.sleep(Amplifier.time_sleep)
                self.sock.send(cmd + "\n")
                print("Set gain %s" % param)

            elif mod == "APC":
                self.sock.send("mode:APC\n")
                cmd = "SEL:PM:%.2f\n" % param
                time.sleep(Amplifier.time_sleep)
                self.sock.send(cmd + "\n")
                print("Set power %s" % param)

            elif mod == "ACC":
                self.sock.send("mode:ACC\n")
                cmd = "SEL:IL1:%.2f\n" % param
                time.sleep(Amplifier.time_sleep)
                self.sock.send(cmd + "\n")
                print("Set current %s" % param)
        except socket.error as e:
            print("ERROR: mode not configured, {}".format(e))

    def status(self):
        """
        Check and return the Amplifier configured parameters:

            - Check mode and put it into the variable 'mod' as string.
                - Check (power/gain/current) mode and put it into the variable 'power' as float.
            - Check status (enable/disable) and put it into the variable 'stat' (True/False).

        :return: status, mode, power
        :rtype list
        """
        mod = ""
        power = 0.00
        stat = False

        # Check mode
        try:
            self.sock.send("MODE\n")
            self.sock.send(Amplifier.read_eoi)
            s = self.sock.recv(Amplifier.buffer_size)
            mod = s.split(" ")[1]
            power = float(s.split(" ")[2])
        except socket.error as e:
            print("ERROR: checking mode, {}".format(e))

        # Check status
        try:
            self.sock.send("POW?\n")
            self.sock.send(Amplifier.read_eoi)
            s = self.sock.recv(Amplifier.buffer_size)
            if s.find("OFF") == -1:
                stat = True
        except socket.error as e:
            print("ERROR: checking mode, {}".format(e))

        return [stat, mod, power]

    def close(self):
        """
        Close and delete connection of the Amplifier.
        """
        try:
            print("Connection to amplifier closed")
            self.sock.close()
        except socket.error as e:
            print("ERROR: connection not closed, {}".format(e))

    def checkerror(self):
        """
        Check system errors in the Amplifier.

        # TODO define return
        :return: ?
        :rtype: str
        """
        try:
            self.sock.send("SYST:ERR?\n")
            self.sock.send(Amplifier.read_eoi)
            return self.sock.recv(Amplifier.buffer_size)
        except socket.error as e:
            print("ERROR: system error, {}".format(e))
