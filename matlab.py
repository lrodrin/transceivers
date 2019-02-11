from subprocess import Popen, PIPE
from threading import Timer


def run(timeout_sec):
    proc = Popen(['notepad.exe', r'C:\Users\cttc\Desktop\agent-bvt\server\Leia_DAC_up.m'], stdout=PIPE, stderr=PIPE)
    # proc = Popen(
    #     ['C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe', '-nodisplay', '-nosplash', '-nodesktop',
    #      r'C:\Users\cttc\Desktop\agent-bvt\server\Leia_DAC_up.m'], stdout=PIPE, stderr=PIPE)

    timer = Timer(timeout_sec, proc.kill)
    try:
        timer.start()
        stdout, stderr = proc.communicate()
        print("retcode = ", proc.returncode)
        print("res = ", stdout)
        print("stderr = ", stderr)  # TODO error control
    finally:
        timer.cancel()

    return proc.returncode


if __name__ == '__main__':
    rc = 0
    while rc != 1:
        rc = run(10)  # timeout happens at 10 second
        print(rc)

