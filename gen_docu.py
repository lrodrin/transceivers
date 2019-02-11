import os

BASEPATH = os.getcwd()
LIBPATH = BASEPATH + "/lib/"
DOCPATH = BASEPATH + "/docs/"


def listdirs(folder):
    """
    List directories inside a folder specified by folder

    :param folder: path folder
    :type folder: str
    :return: list of directories from folder
    :rtype: list
    """
    return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]


if __name__ == '__main__':
    for dir in listdirs(LIBPATH):
        if not dir.startswith("_"):  # ignore __pycache__ directory
            for root, dirs, files in os.walk(LIBPATH + dir + "/"):
                for filename in files:
                    if filename.endswith(".py") and not filename.startswith("_"):
                        print("pydoc3 -w " + LIBPATH + dir + "/" + filename)
                        try:
                            os.system("pydoc3 -w " + LIBPATH + dir + "/" + filename)
                        except:
                            pass
                            # TODO

    print("mv *.html " + DOCPATH)
    os.system("mv *.html " + DOCPATH)
