import glob
import os
import shutil

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def listdirs(folder):
   return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

if __name__ == '__main__':
    basepath = os.getcwd()
    libpath = "/lib"
    ld = listdirs(basepath + libpath)
    print(ld)
    for d in ld:
        os.system("pydoc -w " + d + "/*.py")
