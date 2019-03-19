import os
import signal
from subprocess import Popen, PIPE
from threading import Timer


def run(folder, filename, timeout_sec):
    program = 'C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe'
    options = '-nodisplay -nosplash -nodesktop -wait'
    cmd = """{} {} -r "cd(fullfile('{}')), {}" """.format(program, options, folder, filename)

    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    timer = Timer(timeout_sec, p.kill)
    try:
        timer.start()
        out, err = p.communicate()
        if p.returncode == 0:
            print("Command {} succeeded, exit-code = {} returned".format(cmd, p.returncode))
        else:
            print("Command {} failed, exit-code = {} returned, error = {}".format(cmd, p.returncode, str(err)))
    finally:
        timer.cancel()
        os.kill(p.pid, signal.SIGTERM)


if __name__ == '__main__':
    folder = 'C:/Users/cttc/Desktop/agent-bvt/config'
    filename = 'Leia_DAC_up.m'
    run(folder, filename, 50)