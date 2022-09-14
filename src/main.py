from imp import reload
from maya import cmds
import maya.mel as mel
from math import sqrt
import nodes
import os
reload(nodes)


class autoMat(object):
    def __init__(self, dataPath: str = 'sourceimages/', renderEngine: str = 'arnold', triPlanar: bool = False) -> None:
        self.renderEngine = renderEngine
        self.projectDir = cmds.workspace(q=True, rootDirectory=True)
        self.dataPath = os.path.join(self.projectDir, dataPath)
        self.dataDict = {}
        self.triPlanar = triPlanar

        # remove from here
        # texNodeName = os.path.split(self.dataPath)[1].split('.')[0]

        self.texTypes = {'color': ('diff', 'albedo', 'color', 'rgb'),
                         'metalness': ('met', ),
                         'roughness': ('rough', ),
                         'glossiness': ('gloss', ),
                         'normal': ('nrm', 'nor'),
                         'displacement': ('height', 'disp'),
                         'emissive': ('emiss', 'illum', 'emit'),
                         'sss': ('sss', 'subsurf'),
                         'transmission': ('trans', ),
                         'opacity': ('op', 'alpha', 'transp'),
                         'coat': ('coat', ),
                         'sheen': ('sheen', )}
        # default execution
        self.findFiles()
        self.setupMaterialTrip()

    def setupMaterialTrip(self):
        moveStep = 0
        triScale = 0.35  # TODO remove hardcoded values
        triBlend = 1.0
        columns = round(sqrt(len(self.dataDict.keys())))

        for key, value in self.dataDict.items():
            # setup shader
            shaderNodeName = os.path.split(key)[1]
            newShader = nodes.arnoldPBRShader(shaderNodeName, debug=True)

            # assign to preview mesh
            newShader.assigntoSphere(-2 * (moveStep % columns), 0,
                                     (moveStep // columns) * 2, debug=True)
            moveStep += 1

            for v in value:
                texNodeName = v.split('.')[0]
                texFilePath = os.path.join(key, v)
                texType = self.getType(texNodeName)

                if texType == 'color':
                    newShader.setupTripColor(
                        texNodeName, texFilePath, texType, triBlend, triScale)

                if texType == 'metalness':
                    newShader.setupTripMetalness(
                        texNodeName, texFilePath, texType, triBlend, triScale)

                if texType == 'roughness':
                    newShader.setupTripRoughness(
                        texNodeName, texFilePath, texType, triBlend, triScale)

                if texType == 'normal':
                    newShader.setupTripNormal(
                        texNodeName, texFilePath, texType, triBlend, triScale)

                if texType == 'displacement':
                    newShader.setupTripDisplacement(
                        texNodeName, texFilePath, texType, triBlend, triScale)

    def getType(self, name: str):
        # TODO check image for color or grayscale
        # TODO ask user for recognized pattern
        for keys, values in self.texTypes.items():
            for val in values:
                if val in name.lower():
                    # returns texture types
                    return keys

    def findFiles(self):
        try:
            os.path.exists(self.dataPath)
        except:
            raise ("choosen path does not exist")

        for path, directories, files in os.walk(self.dataPath):
            if files:
                texList = []
                for file in files:
                    # exclude .tx files from reading
                    if file.endswith('.tx'):
                        continue
                    texList.append(file)

                self.dataDict[path] = texList


mel.eval('MLdeleteUnused;')
newAutoMat = autoMat(triPlanar=True)

# unknownNodes = cmds.ls(type="unknown")
# for item in unknownNodes:
#     if cmds.objExists(item):
#         print(item)
#         cmds.delete(item)
