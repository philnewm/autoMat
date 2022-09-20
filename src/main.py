from imp import reload
from maya import cmds
import maya.mel as mel
from math import sqrt
import os
import nodes
# from autoMat.src import nodes
import ui
# from autoMat.src import ui
reload(ui)  # TODO remove later only for WIP with maya
reload(nodes)   # TODO remove later only for WIP with maya


class autoMat(object):
    def __init__(self, dataPath: str = 'sourceimages/', renderEngine: str = 'arnold', triPlanar: bool = False) -> None:
        """
        This class holds all neccessary functions and values to setup complete PBR materials using classes from nodes.py library.

        Args:
            dataPath (str, optional): A directory to search for files. Defaults to 'sourceimages/'.
            renderEngine (str, optional): Render engine in use. Defaults to 'arnold'.
            triPlanar (bool, optional): wether to use triplanar mapping or not. Defaults to False.
        """

        self.renderEngine = renderEngine
        self.projectDir = cmds.workspace(q=True, rootDirectory=True)
        self.dataPath = os.path.join(self.projectDir, dataPath)
        self.dataDict = {}
        self.triPlanar = triPlanar
        self.csDefaults = ("sRGB", "Raw")
        self.grpName = "Preview_Spheres_grp"

        self.removeEmptyGroups()

        if not cmds.objExists(self.grpName):
            cmds.group(empty=True, name=self.grpName)

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

    # TODO find cleaner way to implement multiple materials setups
    def setupMaterialTrip(self, showInVP=True):
        """
        This Sets up a complete PBR material based on available textures using triplanar mapping.

        Args:
            showInVP (bool, optional): Set if materials should be visible in maya viewport or not. Defaults to True.
        """
        self.cleanUp()

        # TODO move values to UI
        moveStep = 0
        # TODO Scalar Zero Value for displacements with gray value 0.5 everything except .exr
        triScale = 0.65
        triBlend = 1.0
        columns = round(sqrt(len(self.dataDict.keys())))

        for key, value in self.dataDict.items():
            # setup shader
            shaderNodeName = os.path.split(key)[1]

            newShader = nodes.arnoldPBRShader(shaderNodeName, debug=True)

            # displacementFileType

            # assign to preview mesh
            newShader.assigntoSphere(-2 * (moveStep % columns), 0,
                                     (moveStep // columns) * 2, showInVP, self.grpName,  debug=True)
            moveStep += 1

            # TODO add try except clauses if something fails

            for v in value:
                texNodeName, texFilePath, texType, texFileType = self.extractData(
                    key, v)

                if texType == 'color':
                    newShader.setupTripColor(
                        texNodeName, texFilePath, texType, self.csDefaults, triBlend, triScale)

                if texType == 'metalness':
                    newShader.setupTripMetalness(
                        texNodeName, texFilePath, texType, self.csDefaults, triBlend, triScale)

                if texType == 'roughness':
                    newShader.setupTripRoughness(
                        texNodeName, texFilePath, texType, self.csDefaults, triBlend, triScale)

                if texType == 'normal':
                    newShader.setupTripNormal(
                        texNodeName, texFilePath, texType, self.csDefaults, triBlend, triScale)

                if texType == 'displacement':
                    # adjust zero scale if neccessary
                    if texFileType == 'exr':
                        zeroScaleValue = 0.0
                    else:
                        zeroScaleValue = 0.5

                    newShader.setupTripDisplacement(
                        texNodeName, texFilePath, texType, self.csDefaults, triBlend, triScale, zeroScaleValue)

        # cmds.hyperShade(clearWorkArea=True)

    def removeEmptyGroups(self):
        # delete empty groups
        transforms = cmds.ls(type='transform')
        deleteList = []
        for tran in transforms:
            if cmds.nodeType(tran) == 'transform':
                children = cmds.listRelatives(tran, c=True)
            if children == None:
                deleteList.append(tran)

        cmds.delete(deleteList)

    # TODO clean hypershade after creation

    # TODO find cleaner way to implement multiple materials setups
    def setupMaterial(self, showInVP=True):
        """
        This Sets up a complete PBR material based on available textures.

        Args:
            showInVP (bool, optional): Set if materials should be visible in maya viewport or not. Defaults to True.
        """
        self.cleanUp()

        moveStep = 0
        columns = round(sqrt(len(self.dataDict.keys())))

        for key, value in self.dataDict.items():
            # setup shader
            shaderNodeName = os.path.split(key)[1]
            # TODO check if objects with name already and exist and add number
            newShader = nodes.arnoldPBRShader(shaderNodeName, debug=True)

            # assign to preview mesh
            newShader.assigntoSphere(-2 * (moveStep % columns), 0,
                                     (moveStep // columns) * 2, showInVP, debug=True)
            moveStep += 1

            for v in value:
                texNodeName, texFilePath, texType, texFileType = self.extractData(
                    key, v)

                if texType == 'color':
                    newShader.setupColor(
                        texNodeName, texFilePath, texType, self.csDefaults)

                elif texType == 'metalness':
                    newShader.setupMetalness(
                        texNodeName, texFilePath, texType, self.csDefaults)

                elif texType == 'roughness':
                    newShader.setupRoughness(
                        texNodeName, texFilePath, texType, self.csDefaults)

                elif texType == 'normal':
                    newShader.setupNormal(
                        texNodeName, texFilePath, texType, self.csDefaults)

                elif texType == 'displacement':
                    # adjust zero scale if neccessary
                    print(texFileType)
                    if texFileType == 'exr':
                        zeroScaleValue = 0.0
                    else:
                        zeroScaleValue = 0.5

                    newShader.setupDisplacement(
                        texNodeName, texFilePath, texType, self.csDefaults, zeroScaleValue)

        # cmds.hyperShade(clearWorkArea=True)

    def extractData(self, key, v):
        """
        This function extracts the texture node name, filepath and texture type from a dictionary.
        Args:
            key (_type_): directory path where texture where found
            v (_type_): texture file

        Returns:
            _type_: _description_
        """
        texNodeName = v.split('.')[0]
        texFileType = v.split('.')[1]
        texFilePath = os.path.join(key, v)
        texType = self.getType(texNodeName)
        return texNodeName, texFilePath, texType, texFileType

    def cleanUp(self):
        """
        Cleans all existing materials and preview spheres from the maya scene.
        """
        try:
            # TODO setup list of created spheres for more effective delete
            cmds.delete('*_previewSphere_geo')
            mel.eval('MLdeleteUnused;')
        except ValueError:
            print("No Objects to delete")

    def getType(self, name: str):
        """
        Return somewhat "clever" guess of the texture type based on the texture files name.

        Args:
            name (str): Texture file name

        Returns:
            _type_: Texture type
        """
        # TODO check image for color or grayscale
        # TODO ask user for recognized pattern
        for keys, values in self.texTypes.items():
            for val in values:
                if val in name.lower():
                    # returns texture types
                    return keys

    def findFiles(self):
        """
        Walks down the given directory path and searches for files within each directory while creating a dictionary of all found directories and files.
        """
        self.dataDict.clear()

        try:
            os.path.exists(self.dataPath)
        except:
            raise ("choosen path does not exist")

        for path, directories, files in os.walk(self.dataPath):

            # ignore directories starting with '.' (.mayaSwatches, .vrayThumbs)
            if files and not os.path.split(path)[1].startswith('.'):

                texList = []
                for file in files:

                    # exclude .tx files from beeign read
                    if file.endswith('.tx'):
                        continue
                    # exclude hidden files from beeing read
                    elif file.startswith('.'):
                        continue
                    else:
                        texList.append(file)

                self.dataDict[path] = texList
