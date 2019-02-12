import sys
import subprocess


def run(folder, filename):
    program = 'C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe'
    options = '-nodisplay -nosplash -nodesktop -wait'
    cmd = """{} {} -r "cd(fullfile('{}')), {}" """.format(program, options, folder, filename)
    try:
        p = subprocess.Popen(cmd)
        out, err = p.communicate()
        if p.returncode == 0:
            print("command '%s' succeeded, exit-code=%d" % (cmd, p.returncode))
        else:
            print("command '%s' failed, exit-code=%d error = %s" % (cmd, p.returncode, str(err)))

    except OSError as e:
        sys.exit("failed to execute program '%s': %s" % (cmd, str(e)))


if __name__ == '__main__':
    folder = 'C:/Users/cttc/Desktop/agent-bvt/server'
    filename = 'Leia_DAC_up.m'
    run(folder, filename)