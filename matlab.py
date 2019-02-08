import subprocess

p = subprocess.Popen(
    ['C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe', '-nodisplay', '-nosplash', '-nodesktop', '-wait', '-r',
     'Leia_DAC_up;'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

try:
    out, err = p.communicate()
    print(out, err)

except:
    pass

# error que es quedi amb wait.
try:
    p.wait(timeout=0.1)
except subprocess.TimeoutExpired:
    p.kill()
# try:
#     out, err = p.communicate()
#     if err:
#         print("err", err)
#     else:
#         print("out", out)
# except TimeoutError:
#     p.kill()
#     out, err = p.communicate()
#
# if p.returncode != 0:
#     print("fail")
