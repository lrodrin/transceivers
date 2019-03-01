"""
This module generate the library documentation.
"""
import os
import subprocess

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
    for d in listdirs(LIBPATH):
        if not d.startswith("_"):  # ignore __pycache__ directory
            for root, dirs, files in os.walk(LIBPATH + d + "/"):
                for filename in files:
                    if filename.endswith(".py") and (not filename.startswith("_") and not filename.startswith(
                            "wsa")):  # ignore .pyc, __init__.py and wsapi.py
                        print('pydoc3 -w {}{}/{}'.format(LIBPATH, d, filename))
                        try:
                            subprocess.run('pydoc3 -w {}{}/{}'.format(LIBPATH, d, filename), shell=True)
                        except Exception as e:
                            print("The subprocess call failed")

    print("mv *.txt %s" % DOCPATH)
    subprocess.run('mv *.html %s' % DOCPATH, shell=True)
