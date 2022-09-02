from maya import cmds
import pprint
from PySide2 import QtWidgets, QtCore, QtGui
import os

PROJECTDIR = cmds.workspace(q=True, rootDirectory=True)
texDir = PROJECTDIR + 'sourceimages/' + 'textures'
arnoldPBRShader = 'aiStandardSurface'


def find(directory: str = texDir):

    if not os.path.exists(directory):
        return

    matname = []

    for path, directories, files in os.walk(texDir):
        for mats in directories:
            matname.append(cmds.shadingNode(
                arnoldPBRShader, name=mats, asShader=True))
        for f in files:
            print(f)
    return matname


print(find())
