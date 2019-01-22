import os
from os import walk

def listdirs(folder):
    return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]


if __name__ == '__main__':
    basepath = os.getcwd()
    libpath = "/lib/"
    docpath = "/docs/"
    match = "*.py"
    for dir in listdirs(basepath + libpath):
        if not dir.startswith("_"):   # ignore __pycache__ directory
            print("pydoc -w " + basepath + libpath + dir + "/" + match)
        # try:
        #     os.system("pydoc -w " + basepath + libpath + dir + "/*.py")
        # except:
        #     pass

    print("mv *.html " + basepath + docpath)
    # os.system("mv *.html " + basepath + docpath)
