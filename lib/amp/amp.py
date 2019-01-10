import string
import time
import socket

BUFSIZE = 100

READ_EOI = "++read eoi\n"

CONNECTION_PORT = 1234

CONNECTION_TIMEOUT = 2

EOI_1 = "++eoi 1\n"

EOS_3 = "++eos 3\n"

TIMEOUT = "++read_tmo_ms 500\n"

READ_AFTER_WRITE = "++auto 0\n"

MODE = "++mode 1\n"

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>, Josep M.Fabrega <jmfabrega@cttc.cat> and Laia Nadal " \
             "<laia.nadal@cttc.cat> "
__copyright__ = "Copyright 2018, CTTC"


class Amplifier:
    """
    This is a class for Amplifier configuration.

    """

    def __init__(self, ip, addr):
        """
        The constructor for Amplifier class.

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
        Connect to Amplifier and initialize the Amplifier default parameters:

            - Set mode as CONTROLLER.
            - Set GPIB address.
            - Turn off READ_AFTER_WRITE to avoid "Query Unterminated" errors.
            - Read timeout is 500 ms.
            - Do not append CR or LF to GPIB data.
            - Assert EOI_1 with last byte to indicate end of data.

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
        self.sock.send(EOI_1)

    def test(self):
        """
        Just as test, ask for instrument ID according to SCPI API

        :return: amplifier type, band type and software release (e.g EDFA C Band,V2.1)
        :rtype: str
        """
        self.sock.send("*IDN?\n")
        self.sock.send(READ_EOI)
        try:
            instrument_id = self.sock.recv(BUFSIZE)

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

        elif mod == "ACC":
            self.sock.send("MODE:ACC\n")  # set the mode to ACC
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
        self.sock.send("MODE\n")
        self.sock.send(READ_EOI)
        try:
            s = self.sock.recv(BUFSIZE)
        except socket.timeout:
            s = ""

        mod = string.split(s, " ")[1]  # store mode in variable 'mod' as string
        param = float(string.split(s, " ")[2])  # store parameter (power/gain) in variable 'param' as float

        # Check status
        self.sock.send("POW\n")
        self.sock.send(READ_EOI)
        try:
            s = self.sock.recv(BUFSIZE)
        except socket.timeout:
            s = ""

        stat = False
        if string.find(s, "OFF") == -1:
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
            s = self.sock.recv(BUFSIZE)
        except socket.timeout:

            s = ""

        # TODO define s
        return s


# if __name__ == '__main__':
#     ip_eth_manlight_1 = '10.1.1.15'
#     ip_eth_manlight_2 = '10.1.1.16'
#     addr_gpib = '3'
#     manlight_1 = Amplifier(ip_eth_manlight_1, addr_gpib)
#     manlight_2 = Amplifier(ip_eth_manlight_2, addr_gpib)
#     manlight_1.mode("APC", 5)
#     manlight_2.mode("ACC", 3)
#     manlight_1.enable(True)
#     manlight_2.enable(True)
#     time.sleep(5)
#     print(manlight_1.status())
#     print(manlight_2.status())
#     print(manlight_1.test())
#     print(manlight_2.test())
#     manlight_1.close()
#     manlight_2.close()
