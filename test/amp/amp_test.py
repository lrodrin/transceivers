#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.amp.amp import Amplifier

AMPLIFIER_ADDR = '3'

IP_AMPLIFIER_2 = '10.1.1.16'

IP_AMPLIFIER_1 = '10.1.1.15'

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

if __name__ == '__main__':
    manlight_1 = Amplifier(IP_AMPLIFIER_1, AMPLIFIER_ADDR)
    manlight_2 = Amplifier(IP_AMPLIFIER_2, AMPLIFIER_ADDR)
    manlight_1.mode("APC", 5)
    manlight_2.mode("APC", 3)
    manlight_1.enable(True)
    manlight_2.enable(True)
    time.sleep(5)
    print(manlight_1.status())
    print(manlight_2.status())
    print(manlight_1.test())
    print(manlight_2.test())
    manlight_1.close()
    manlight_2.close()
