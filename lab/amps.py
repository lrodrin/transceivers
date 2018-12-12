from __future__ import print_function

import socket
import time


class Amps:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)

    def open(self, ip):

        # Set GPIB address
        addr = '3'

        # Open TCP connect to port 1234 of GPIB-ETHERNET
        self.sock.settimeout(2)  # readjusted the timeout in order to allow a propper GPIB -> Eth conversion
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

    def status(self, stat=False):
        if stat:
            self.sock.send("POW:ON\n")  # enable EDFA
        else:
            self.sock.send("POW:OFF\n")  # disable EDFA

        time.sleep(1)

    def mode(self, mod, param=0):
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

    def close(self):
        self.sock.close()

    def checkerror(self):
        self.sock.send("SYST:ERR?\n")
        self.sock.send("++read eoi\n")

        try:
            s = self.sock.recv(100)

        except socket.timeout:

            s = ""

        print (s)


# if __name__ == '__main__':
#     manlight_1 = Amps()
#     manlight_2 = Amps()
#     manlight_1.open('10.1.1.15')
#     manlight_2.open('10.1.1.16')
#     print(manlight_1.test())
#     print(manlight_2.test())
#     manlight_1.mode("APC", 15)
#     manlight_2.mode("APC", 17)
#     manlight_1.close()
#     manlight_2.close()
