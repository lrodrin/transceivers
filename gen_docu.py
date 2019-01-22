import os

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def listdirs(folder):
    return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]


if __name__ == '__main__':
    basepath = os.getcwd()
    libpath = "/lib/"
    docpath = "/docs/"
    for d in listdirs(basepath + libpath):
        print("pydoc -w " + basepath + libpath + d + "/*.py")
        # TODO remove init files from the call
        try:
            os.system("pydoc -w " + basepath + libpath + d + "/*.py")
        except:
            pass

    print("mv *.html " + basepath + docpath)
    os.system("mv *.html " + basepath + docpath)
