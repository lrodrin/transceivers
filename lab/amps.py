from __future__ import print_function

import socket
import time
import string

class Amps:

    def __init__(self, ip):
        self.ip = ip
        self.open()

    def open(self):

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
        self.sock.send("*IDN?\n")
        self.sock.send("++read eoi\n")
        s = None
        try:
            s = self.sock.recv(100)

        except socket.timeout:
            s = ""

        return s

    def enable(self, stat=False):
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

    def status(self):
        # First ask for the mode
        self.sock.send("MODE\n")
        self.sock.send("++read eoi\n")
        s = None
        try:
            s = self.sock.recv(100)

        except socket.timeout:
            s = ""

        mod=string.split(s," ")[1] # Store mode in variable 'mod' as string
        param=float(string.split(s," ")[2]) # Store parameter (power/gain) in variable 'param' as float

        # Then ask for the status (enabled/disabled) and store it into 'stat' (True/False)
        self.sock.send("POW\n")
        self.sock.send("++read eoi\n")
        s = None
        try:
            s = self.sock.recv(100)

        except socket.timeout:
            s = ""

        stat=False
        if string.find(s,"OFF")==-1:
            stat=True

        return [stat, mod, param]


    def close(self):
        self.sock.close()

    def checkerror(self):
        self.sock.send("SYST:ERR?\n")
        self.sock.send("++read eoi\n")
        s = None
        try:
            s = self.sock.recv(100)

        except socket.timeout:

            s = ""

        print(s)


if __name__ == '__main__':
    manlight_1 = Amps('10.1.1.15')
    manlight_2 = Amps('10.1.1.16')
    print(manlight_1.test())
    print(manlight_2.test())
    manlight_1.mode("APC", 5)
    manlight_2.mode("APC", 3)
    manlight_1.enable(True)
    print(manlight_1.status())
    print(manlight_2.status())
    manlight_1.close()
    manlight_2.close()
