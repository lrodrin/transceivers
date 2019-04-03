"""This is the Laser module.
"""
import logging
import socket
import time

logger = logging.getLogger("LASER")
logger.addHandler(logging.NullHandler())


class Laser:
    """
    This is a class for Laser module.

    :var int connection_port:
    :var int connection_timeout:
    :var str mode:
    :var str read_after_write:
    :var str read_timeout:
    :var str eoi_1:
    :var str eos_3:
    :var int buffer_size:
    :var str read_eoi:
    :var int time_sleep_enable: Time needed to enable/disable the Laser before check the status
    """
    connection_port = 1234
    connection_timeout = 1
    mode = "++mode 1\n"
    read_after_write = "++auto 0\n"
    read_timeout = "++read_tmo_ms 500\n"
    eoi_1 = "++eoi 1\n"
    eos_3 = "++eos 3\n"
    buffer_size = 100
    read_eoi = "++read eoi\n"
    time_sleep_enable = 5

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
        self.connection_and_initialization()

    def connection_and_initialization(self):
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
        self.sock.settimeout(self.connection_timeout)
        ip = self.ip
        port = self.connection_port
        try:
            self.sock.connect((ip, port))
            logger.debug("Connection to Laser {} on port {} opened".format(ip, port))

        except socket.error as error:
            logger.error("Connection to Laser refused, {}".format(error))

        # Initialization
        try:
            self.sock.send(bytes(self.mode, encoding='utf8'))
            addr_GPIB = "++addr " + self.addr + "\n"
            self.sock.send(bytes(addr_GPIB, encoding='utf8'))
            self.sock.send(bytes(self.read_after_write, encoding='utf8'))
            self.sock.send(bytes(self.read_timeout, encoding='utf8'))
            self.sock.send(bytes(self.eos_3, encoding='utf8'))
            self.sock.send(bytes(self.eoi_1, encoding='utf8'))

        except socket.error as error:
            logger.error("Default parameters of the Laser not initialized, {}".format(error))

    def test(self):
        """
        Just as test, ask for instrument ID according to SCPI API.

        :return: instrument ID (e.g NetTest, OSICS, 0, 3.01)
        :rtype: str
        """
        try:
            self.sock.send(bytes("*IDN?\n", encoding='utf8'))
            self.sock.send(bytes(self.read_eoi, encoding='utf8'))
            return self.sock.recv(self.buffer_size)

        except socket.error as error:
            logger.error("Laser test, {}".format(error))

    def wavelength(self, ch, lambda0):
        """
        Define the wavelength in nm.

            - The range of wavelength takes 1527'55899 to 1565'544 nm.

        :param ch: channel
        :type ch: int
        :param lambda0: wavelength
        :type lambda0: float
        """
        try:
            logger.debug("Set wavelength %s" % lambda0)
            self.sock.send(bytes("CH%d:NM\n" % ch, encoding='utf8'))  # set units in nm
            self.sock.send(bytes("CH%d:L=%.3f\n" % (ch, lambda0), encoding='utf8'))

        except socket.error as error:
            logger.error("Wavelength not configured, {}".format(error))

    def power(self, ch, power):
        """
        Define the power in dBm.

            - The range of power takes 6'03 to 14'50 dBm.

        :param ch: channel
        :type ch: int
        :param power: power
        :type power: float
        """
        try:
            logger.debug("Set power %s" % power)
            self.sock.send(bytes("CH%d:DBM\n" % ch, encoding='utf8'))  # set units in dBm
            self.sock.send(bytes("CH%d:P=%.3f\n" % (ch, power), encoding='utf8'))

        except socket.error as error:
            logger.error("Power not configured, {}".format(error))

    def enable(self, ch, stat=False):
        """
        Enable or Disable the Laser.

        :param ch: channel
        :type ch: int
        :param stat: if True is enable otherwise is disable
        :type stat: bool
        """
        logger.debug("Set status %s" % stat)
        if stat:
            try:
                self.sock.send(bytes("CH%d:ENABLE\n" % ch, encoding='utf8'))
                time.sleep(self.time_sleep_enable)

            except socket.error as error:
                logger.error("Can't enable, {}".format(error))
        else:
            try:
                self.sock.send(bytes("CH%d:DISABLE\n" % ch, encoding='utf8'))
                time.sleep(self.time_sleep_enable)

            except socket.error as error:
                logger.error("Can't disable, {}".format(error))

    def status(self, ch):
        """
        Check and return the Laser configured parameters:

            - Check status (enable/disable) and put it into the variable 'stat' (True/False).
            - Check wavelength and put it into the variable 'wavelength' in nm.
            - Check power and put it into the variable 'power' in dBm (-60 indicates DISABLED).

        :param ch: channel
        :type ch: int
        :return: status, wavelength, power
        :rtype: list
        """
        stat = False
        wavelength = float()
        power = float()

        # Check status
        try:
            self.sock.send(bytes("CH%d:ENABLE?\n" % ch, encoding='utf8'))
            self.sock.send(bytes(self.read_eoi, encoding='utf8'))
            s = self.sock.recv(self.buffer_size)
            if s.split(bytes(":", encoding='utf8'))[1] == "ENABLED\n":
                stat = True

        except socket.error as error:
            logger.error("Checking status, {}".format(error))

        # Check wavelength
        try:
            self.sock.send(bytes("CH%d:L?\n" % ch, encoding='utf8'))
            self.sock.send(bytes(self.read_eoi, encoding='utf8'))
            s = self.sock.recv(self.buffer_size)
            wavelength = float(s.split(bytes("=", encoding='utf8'))[1])

        except socket.error as error:
            logger.error("Checking wavelength, {}".format(error))

        # Check power
        try:
            self.sock.send(bytes("CH%d:P?\n" % ch, encoding='utf8'))
            self.sock.send(bytes(self.read_eoi, encoding='utf8'))
            s = self.sock.recv(self.buffer_size)
            if stat:
                power = float(s.split(bytes("=", encoding='utf8'))[1])
            else:
                power = -60

        except socket.error as error:
            logger.error("Checking wavelength, {}".format(error))

        return [stat, wavelength, power]

    def close(self):
        """
        Close and delete connection of the Laser.
        """
        try:
            logger.debug("Connection to Laser closed")
            self.sock.close()

        except socket.error as error:
            logger.error("Connection to Laser not closed, {}".format(error))

    def checkerror(self):
        """
        Check system errors in the Laser.

        :return: error message
        :rtype: str
        """
        try:
            self.sock.send(bytes("SYST:ERR?\n", encoding='utf8'))
            self.sock.send(bytes(self.read_eoi, encoding='utf8'))
            return self.sock.recv(self.buffer_size)

        except socket.error as error:
            logger.error("System error, {}".format(error))

    @staticmethod
    def configuration(ip, addr, channel, lambda0, power):
        """
        Laser configuration:

            - Set wavelength of the Laser.
            - Set the power of the Laser.
            - Check status, mode and power of the Laser and shows the values.

        :param ip: IP address of GPIB-ETHERNET
        :type ip: str
        :param addr: GPIB address
        :type addr: str
        :param channel: channel
        :type channel: int
        :param lambda0: wavelength
        :type lambda0: float
        :param power: power
        :type power: float
        """
        logger.debug("Laser on channel %s configuration started" % channel)
        try:
            yenista = Laser(ip, addr)
            yenista.enable(channel, False)  # Ensure Laser is off
            yenista.wavelength(channel, lambda0)
            yenista.power(channel, power)
            yenista.enable(channel, True)
            result = yenista.status(channel)
            logger.debug(
                "Laser parameters - status: {}, wavelength: {}, power: {}".format(result[0], result[1], result[2]))

            yenista.close()
            logger.debug("Laser on channel %s configuration finished" % channel)

        except Exception as error:
            logger.error("Laser configuration failed, {}".format(error))
            raise error
