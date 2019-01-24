import time

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.amp.amp import Amplifier

AMPLIFIER_ADDR = '3'
SECS = 5
IP_AMPLIFIER_2 = '10.1.1.16'
IP_AMPLIFIER_1 = '10.1.1.15'


def amplifier_startup(modeA, powA, modeB, powB, statA, statB):
    manlight_1 = Amplifier(IP_AMPLIFIER_1, AMPLIFIER_ADDR)
    manlight_2 = Amplifier(IP_AMPLIFIER_2, AMPLIFIER_ADDR)
    manlight_1.mode(modeA, powA)
    manlight_2.mode(modeB, powB)
    manlight_1.enable(statA)
    manlight_2.enable(statB)
    time.sleep(SECS)
    print(manlight_1.status())
    print(manlight_2.status())
    print(manlight_1.test())
    print(manlight_2.test())
    manlight_1.close()
    manlight_2.close()


if __name__ == '__main__':
    amplifier_startup("APC", 5, "APC", 3, True, True)
