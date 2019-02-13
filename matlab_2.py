from subprocess import Popen, PIPE
from threading import Timer


def run(timeout_sec):
    proc = Popen(['notepad.exe', r'C:\Users\Laura\Desktop\tp_configuration_files\Leia_DAC_up.m'], stdout=PIPE, stderr=PIPE)

    timer = Timer(timeout_sec, proc.kill)
    try:
        timer.start()
        stdout, stderr = proc.communicate()
        print("retcode = ", proc.returncode)
        print("res = ", stdout)
        print("stderr = ", stderr)  # TODO error control
    finally:
        timer.cancel()


if __name__ == '__main__':
    run(10)  # timeout happens at 5 second
