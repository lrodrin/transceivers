from __future__ import print_function

import socket


class Laser:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.open()

    def open(self):

        # Set IP address of GPIB-ETHERNET
        ip = '10.1.1.7'

        # Set GPIB address
        addr = '11'

        # Open TCP connect to port 1234 of GPIB-ETHERNET
        self.sock.settimeout(0.5)
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
        self.sock.send("*IDN?\n")
        self.sock.send("++read eoi\n")
        try:
            s = self.sock.recv(100)

        except socket.timeout:
            s = ""

        print(s)

    def wavelength(self, ch, lambda0):
        cmd = "CH%d:NM" % ch
        self.sock.send(cmd + "\n")  # set units in nm
        cmd = "CH%d:L=%.3f" % (ch, lambda0)
        self.sock.send(cmd + "\n")  # set wavelength

    def power(self, ch, power):
        cmd = "CH%d:DBM" % ch
        self.sock.send(cmd + "\n")  # set units in dBm
        cmd = "CH%d:P=%.3f" % (ch, power)
        self.sock.send(cmd + "\n")  # set power

    def status(self, ch, stat=False):
        if stat:
            cmd = "CH%d:ENABLE" % ch
            self.sock.send(cmd + "\n")  # enable laser
        else:
            cmd = "CH%d:DISABLE" % ch
            self.sock.send(cmd + "\n")  # disable laser

    def close(self):
        self.sock.close()

    def checkerror(self):
        self.sock.send("SYST:ERR?\n")
        self.sock.send("++read eoi\n")
        try:
            s = self.sock.recv(100)

        except socket.timeout:

            s = ""

        print(s)


# if __name__ == '__main__':
#     yenista = Laser()
#     yenista.wavelength(3, 1550.12)
#     yenista.power(3, 14.5)
#     yenista.status(3, True)
#     print(yenista.test())
