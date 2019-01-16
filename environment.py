import os
import sys

from lib.laser.laser import Laser

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

print(sys.executable)
print(os.getcwd())
print(sys.path)

ip_laser = '10.1.1.7'
laser_addr = '11'
yenista = Laser(ip_laser, laser_addr)
