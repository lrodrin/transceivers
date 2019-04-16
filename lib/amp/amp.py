"""This is the Amplifier module.
"""
import logging
import socket
import time

logger = logging.getLogger("AMPLIFIER")
logger.addHandler(logging.NullHandler())


class Amplifier:
    """
    This is a class for Amplifier module.

    :var int connection_port:
    :var int connection_timeout:
    :var str controller_mode:
    :var str read_after_write:
    :var str read_timeout:
    :var str eoi_1:
    :var str eos_3:
    :var int buffer_size:
    :var str read_eoi:
    :var int time_sleep_enable: Time needed to enable/disable the Amplifier before set the mode
    :var int time_sleep_mode: Time needed to set mode of the Amplifier before changing the power
    :var int time_sleep_mode_power: Time needed to change mode and power of the Amplifier
    :var int time_sleep_status: Time needed to check mode, power ans status of the Amplifier
    """
    connection_port = 1234
    connection_timeout = 2
    controller_mode = "++mode 1\n"
    read_after_write = "++auto 0\n"
    read_timeout = "++read_tmo_ms 500\n"
    eoi_1 = "++eoi 1\n"
    eos_3 = "++eos 3\n"
    buffer_size = 100
    read_eoi = "++read eoi\n"
    time_sleep_enable = 1
    time_sleep_mode = 1
    time_sleep_mode_power = 2
    time_sleep_status = 5

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
        self.connection_and_initialization()

    def connection_and_initialization(self):
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
        self.sock.settimeout(self.connection_timeout)
        ip = self.ip
        port = self.connection_port
        try:
            self.sock.connect((ip, port))
            logger.debug("Connection to Amplifier {} on port {} opened".format(ip, port))

        except socket.error as error:
            logger.error("Connection to Amplifier refused, {}".format(error))

        # Initialization
        try:
            self.sock.send(bytes(self.controller_mode, encoding='utf-8'))
            addr_GPIB = "++addr " + self.addr + "\n"
            self.sock.send(bytes(addr_GPIB, encoding='utf-8'))
            self.sock.send(bytes(self.read_after_write, encoding='utf-8'))
            self.sock.send(bytes(self.read_timeout, encoding='utf-8'))
            self.sock.send(bytes(self.eos_3, encoding='utf-8'))
            self.sock.send(bytes(self.eoi_1, encoding='utf-8'))

        except socket.error as error:
            logger.error("Default parameters of the Amplifier not initialized, {}".format(error))

    def test(self):
        """
        Just as tests, ask for instrument ID according to SCPI API.

        :return: instrument ID (e.g EDFA C Band, V2.1)
        :rtype: str
        """
        try:
            self.sock.send(bytes("*IDN?\n", encoding='utf-8'))
            self.sock.send(bytes(self.read_eoi, encoding='utf-8'))
            return self.sock.recv(self.buffer_size).decode('utf-8')

        except socket.error as error:
            logger.error("Amplifier tests, {}".format(error))

    def enable(self, stat=False):
        """
        Enable or Disable the Amplifier.

        :param stat: if True is enable otherwise is disable
        :type stat: bool
        """
        logger.debug("Set status %s" % stat)
        if stat:
            try:
                self.sock.send(bytes("POW:ON\n", encoding='utf-8'))
            except socket.error as error:
                logger.error("Can't enable the Amplifier, {}".format(error))
        else:
            try:
                self.sock.send(bytes("POW:OFF\n", encoding='utf-8'))
            except socket.error as error:
                logger.error("Can't disable the Amplifier, {}".format(error))

        time.sleep(self.time_sleep_enable)

    def mode(self, mod, param=0):
        """
        Define mode and power.
        Define power or gain for mode AGC and APC in dBm, or current for mode ACC in mA.

            - The range of gain in mode AGC takes 20 to 35 dBm.
            - The range of power in mode APC takes 0 to 23'5 dBm.
            - The range of current in mode ACC takes 0 to 1210 mA.

        :param mod: mode
        :type mod: str
        :param param: power, gain or current
        :type param: float
        """
        try:
            logger.debug("Set mode %s" % mod)
            if mod == "AGC":
                self.sock.send(bytes("MODE:AGC\n", encoding='utf-8'))
                cmd = "SEL:GM:%.2f\n" % param
                time.sleep(self.time_sleep_mode)
                self.sock.send(bytes(cmd + "\n", encoding='utf-8'))
                logger.debug("Set gain %s" % param)

            elif mod == "APC":
                self.sock.send(bytes("MODE:APC\n", encoding='utf-8'))
                cmd = "SEL:PM:%.2f\n" % param
                time.sleep(self.time_sleep_mode)
                self.sock.send(bytes(cmd + "\n", encoding='utf-8'))
                logger.debug("Set power %s" % param)

            elif mod == "ACC":
                self.sock.send(bytes("MODE:ACC\n", encoding='utf-8'))
                cmd = "SEL:IL1:%.2f\n" % param
                time.sleep(self.time_sleep_mode)
                self.sock.send(bytes(cmd + "\n", encoding='utf-8'))
                logger.debug("Set current %s" % param)

        except socket.error as error:
            logger.error("Mode and power not configured, {}".format(error))

    def status(self):
        """
        Check and return the Amplifier configured parameters:
            - Check mode and put it into the variable 'mod' as string.
            - Check (power/gain/current) of the mode and put it into the variable 'power' as float.
            - Check status (enable/disable) and put it into the variable 'stat' (True/False).

        :return: status, mode, power
        :rtype list
        """
        mod = str()
        power = float()
        stat = False

        # Check mode
        try:
            self.sock.send(bytes("MODE\n", encoding='utf-8'))
            self.sock.send(bytes(self.read_eoi, encoding='utf-8'))
            s = self.sock.recv(self.buffer_size).decode('utf-8')
            mod = str.split(s, " ")[1]  # mode
            power = float(str.split(s, " ")[2])  # power

        except socket.error as error:
            logger.error("Checking mode and power, {}".format(error))

        # Check status
        try:
            self.sock.send(bytes("POW\n", encoding='utf-8'))
            self.sock.send(bytes(self.read_eoi, encoding='utf-8'))
            s = self.sock.recv(self.buffer_size).decode('utf-8')
            if str.find(s, "OFF") == -1:
                stat = True

        except socket.error as error:
            logger.error("Checking status, {}".format(error))

        return [stat, mod, power]

    def close(self):
        """
        Close and delete connection of the Amplifier.
        """
        try:
            logger.debug("Connection to Amplifier closed")
            self.sock.close()

        except socket.error as error:
            logger.error("Connection to Amplifier not closed, {}".format(error))

    def checkerror(self):
        """
        Check system errors in the Amplifier.

        :return: error message
        :rtype: str
        """
        try:
            self.sock.send(bytes("SYST:ERR?\n", encoding='utf-8'))
            self.sock.send(bytes(self.read_eoi, encoding='utf-8'))
            return self.sock.recv(self.buffer_size).decode('utf-8')

        except socket.error as error:
            logger.error("System error, {}".format(error))

    @staticmethod
    def configuration(ip, addr, mode, power):
        """
        Amplifier configuration:

            - Set mode of the Amplifier
            - Enable or disable the Amplifier.
            - Check status, mode and power of the Amplifier and shows the values.

        :param ip: IP address of GPIB-ETHERNET
        :type ip: str
        :param addr: GPIB address
        :type addr: str
        :param mode: mode
        :type mode: str
        :param power: power
        :type power: float
        """
        logger.debug("Amplifier configuration started")
        try:
            manlight = Amplifier(ip, addr)
            manlight.enable(False)  # Ensure Amplifier is off
            manlight.mode(mode, power)
            time.sleep(Amplifier.time_sleep_mode_power)
            manlight.enable(True)
            time.sleep(Amplifier.time_sleep_status)
            result = manlight.status()
            logger.debug(
                "Amplifier parameters - status: {}, mode: {}, power: {}".format(result[0], result[1], result[2]))

            manlight.close()
            logger.debug("Amplifier configuration finished")

        except Exception as error:
            logger.error("Amplifier configuration failed, {}".format(error))
            raise error
