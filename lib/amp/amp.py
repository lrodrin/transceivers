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
    """
    # TODO documentar variables constants de la classe
    connection_port = 1234
    connection_timeout = 2
    controller_mode = "++mode 1\n"
    read_after_write = "++auto 0\n"
    read_timeout = "++read_tmo_ms 500\n"
    eoi_1 = "++eoi 1\n"
    eos_3 = "++eos 3\n"

    buffer_size = 100
    read_eoi = "++read eoi\n"
    time_sleep_mode = 1  # Time needed to enable/disable the Amplifier after changing the mode
    time_sleep_enable = 7  # Time needed to enable/disable the Laser before check the status

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
        self.sock.settimeout(Amplifier.connection_timeout)
        ip = self.ip
        port = Amplifier.connection_port
        try:
            self.sock.connect((ip, port))
            logger.debug("Connection to Amplifier {} on port {} opened".format(ip, port))

        except socket.error as error:
            logger.error("Connection to Amplifier refused, {}".format(error))
            raise error

        # Initialization
        try:
            self.sock.send(Amplifier.controller_mode)
            addr_GPIB = "++addr " + self.addr + "\n"
            self.sock.send(addr_GPIB)
            self.sock.send(Amplifier.read_after_write)
            self.sock.send(Amplifier.read_timeout)
            self.sock.send(Amplifier.eos_3)
            self.sock.send(Amplifier.eoi_1)
            logger.debug("Default parameters of the Amplifier initialized")

        except socket.error as error:
            logger.error("Default parameters of the Amplifier not initialized, {}".format(error))
            raise error

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

        except socket.error as error:
            logger.error("Amplifier test, {}".format(error))
            raise error

    def enable(self, stat=False):
        """
        Enable or Disable the Amplifier.

        :param stat: if True is enable otherwise is disable
        :type stat: bool
        """
        logger.debug("Set status %s" % stat)
        if stat:
            try:
                self.sock.send("POW:ON\n")
                time.sleep(Amplifier.time_sleep_enable)

            except socket.error as error:
                logger.error("Can't enable the Amplifier, {}".format(error))
                raise error
        else:
            try:
                self.sock.send("POW:OFF\n")
                time.sleep(Amplifier.time_sleep_enable)

            except socket.error as error:
                logger.error("Can't disable the Amplifier, {}".format(error))
                raise error

    def mode(self, mod, param=0):
        """
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
                self.sock.send("mode:AGC\n")
                cmd = "SEL:GM:%.2f\n" % param
                self.sock.send(cmd + "\n")
                logger.debug("Set gain %s" % param)

            elif mod == "APC":
                self.sock.send("mode:APC\n")
                cmd = "SEL:PM:%.2f\n" % param
                self.sock.send(cmd + "\n")
                logger.debug("Set power %s" % param)

            elif mod == "ACC":
                self.sock.send("mode:ACC\n")
                cmd = "SEL:IL1:%.2f\n" % param
                self.sock.send(cmd + "\n")
                logger.debug("Set current %s" % param)

            time.sleep(Amplifier.time_sleep_mode)

        except socket.error as error:
            logger.error("Mode not configured, {}".format(error))
            raise error

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
            self.sock.send("MODE\n")
            self.sock.send(Amplifier.read_eoi)
            s = self.sock.recv(Amplifier.buffer_size)
            mod = s.split(" ")[1]  # mode
            power = float(s.split(" ")[2])  # power

        except socket.error as error:
            logger.error("Checking mode, {}".format(error))
            raise error

        # Check status
        try:
            self.sock.send("POW?\n")
            self.sock.send(Amplifier.read_eoi)
            s = self.sock.recv(Amplifier.buffer_size)
            if s.find("OFF") == -1:
                stat = True

        except socket.error as error:
            logger.error("Checking status, {}".format(error))
            raise error

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
            raise error

    def checkerror(self):
        """
        Check system errors in the Amplifier.

        :return: error message
        :rtype: str
        """
        try:
            self.sock.send("SYST:ERR?\n")
            self.sock.send(Amplifier.read_eoi)
            return self.sock.recv(Amplifier.buffer_size)

        except socket.error as error:
            logger.error("System error, {}".format(error))
            raise error

    @staticmethod
    def startup(ip, addr, mode, power, status):
        """
        Amplifier startup:

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
        :param status: if True is enable otherwise is disable
        :type status: bool
        """
        logger.debug("Amplifier startup")
        try:
            manlight = Amplifier(ip, addr)
            manlight.mode(mode, power)
            manlight.enable(status)
            params = manlight.status()
            logger.debug(
                "Amplifier parameters - status: {}, mode: {}, power: {}".format(params[0], params[1], params[2]))

            manlight.close()

        except Exception as error:
            logger.error("Amplifier startup, {}".format(error))
            raise error
