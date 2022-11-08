# This code uses mainly the nodes.py content to setup mroe complex processes
# The loading loading  and sorting functions got a custome implementation

from maya import cmds
import maya.mel as mel
from math import sqrt
import os
import re
# Only use when script gets executed from Maya script editor
from autoMat.src import nodes
# Only use when script gets executed from IDE
# import nodes


class autoMat(object):
    def __init__(self, dataPath: str = 'sourceimages/') -> None:
        """
        This class holds all neccessary functions and values to setup complete PBR materials using classes from nodes.py library.

        Args:
            dataPath (str, optional): A directory to search for files. Defaults to 'sourceimages/'.
            renderEngine (str, optional): Render engine in use. Defaults to 'arnold'.
            triPlanar (bool, optional): wether to use triplanar mapping or not. Defaults to False.
        """

        self.projectDir = cmds.workspace(q=True, rootDirectory=True)
        self.dataPath = os.path.join(self.projectDir, dataPath)
        self.dataDict = {}
        self.csDefaults = ("sRGB", "Raw")
        self.grpName = "Preview_Spheres_grp"
        self.prevTexType = None
        self.curTexType = 'default'
        self.texTypeList = []
        self.orgSphere = None

        # displacement values
        self.dispSubdivs = 3
        self.dispHeight = 1.0

        # triplanar values
        self.triScale = 0.65
        self.triBlend = 1

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

        self.ignoreList = ["^\.", "prev", "thumbs", "swatch"]

    # TODO find cleaner way to implement multiple materials setups
    def setupMaterialTrip(self, showInVP=True):
        """
        This Sets up a complete PBR material based on available textures using triplanar mapping.

        Args:
            showInVP (bool, optional): Set if materials should be visible in maya viewport or not. Defaults to True.
        """
        self.cleanUp()
        moveStep = 0
        columns = round(sqrt(len(self.dataDict.keys())))

        if not cmds.objExists(self.grpName):
            cmds.group(empty=True, name=self.grpName)

        self.orgSphere = None

        for key, value in self.dataDict.items():
            self.texTypeList.clear()

            # setup shader
            shaderNodeName = os.path.split(key)[1]
            newShader = nodes.arnoldPBRShader(shaderNodeName)

            # assign to preview mesh
            try:
                newShader.assigntoSphere(-2 * (moveStep % columns), 0,
                                         (moveStep // columns) * 2, showInVP, self.orgSphere, dispSubdivs=self.dispSubdivs, dispHeight=self.dispHeight)
            except:
                print(
                    f"ERROR: failed to assign shader {shaderNodeName} to preview sphere {newShader.geoName}")
            moveStep += 1
            self.orgSphere = newShader.geoName

            for v in value:
                texNodeName, texFilePath, texType, texFileType = self.extractData(
                    key, v)

                self.prevTexType = self.curTexType
                self.curTexType = texType

                if texType == 'color':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupTripColor(
                                texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create basecolor nodes for {newShader.shadNodeName}")

                elif texType == 'metalness':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupTripMetalness(
                                texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create metalness nodes for {newShader.shadNodeName}")

                elif texType == 'roughness':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupTripRoughness(
                                texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create roughness nodes for {newShader.shadNodeName}")

                elif texType == 'transmission':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupTripTransmiss(
                                texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create transmission nodes for {newShader.shadNodeName}")

                elif texType == 'sss':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupTripSSS(
                                texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create sss nodes for {newShader.shadNodeName}")

                elif texType == 'emissive':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupTripTransmission(
                                texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create emission nodes for {newShader.shadNodeName}")

                elif texType == 'opacity':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupTripOpacity(
                                texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create opacity nodes for {newShader.shadNodeName}")

                elif texType == 'normal':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupTripNormal(
                                texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create NormalMap nodes for {newShader.shadNodeName}")

                elif texType == 'displacement':
                    # adjust zero scale if neccessary
                    if texFileType == 'exr':
                        zeroScaleValue = 0.0
                    else:
                        zeroScaleValue = 0.5

                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupTripDisplacement(
                                texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale, zeroScaleValue, self.dispHeight)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create Displacement nodes for {newShader.shadNodeName}")

            # renable when all working
            try:
                mel.eval(
                    'hyperShadePanelGraphCommand("hyperShadePanel1", "clearGraph");')
            except (RuntimeError):
                print("hypershade panel not yet created")

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

        if not cmds.objExists(self.grpName):
            cmds.group(empty=True, name=self.grpName)

        self.orgSphere = None

        for key, value in self.dataDict.items():
            self.texTypeList.clear()

            shaderNodeName = os.path.split(key)[1]
            # setup shader
            try:
                newShader = nodes.arnoldPBRShader(shaderNodeName)
            except:
                print(f"ERROR: failed to create shader {shaderNodeName}")
            # assign to preview mesh
            try:
                newShader.assigntoSphere(-2 * (moveStep % columns), 0,
                                         (moveStep // columns) * 2, showInVP, self.orgSphere, dispSubdivs=self.dispSubdivs, dispHeight=self.dispHeight)
            except:
                print(
                    f"ERROR: failed to assign shader {shaderNodeName} to preview sphere {newShader.geoName}")
            moveStep += 1
            self.orgSphere = newShader.geoName

            for v in value:
                texNodeName, texFilePath, texType, texFileType = self.extractData(
                    key, v)

                self.prevTexType = self.curTexType
                self.curTexType = texType

                if texType == 'color':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupColor(
                                texNodeName, texFilePath, texType, self.csDefaults)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create basecolor nodes for {newShader.shadNodeName}")

                elif texType == 'metalness':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupMetalness(
                                texNodeName, texFilePath, texType, self.csDefaults)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create metalness nodes for {newShader.shadNodeName}")

                elif texType == 'roughness':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupRoughness(
                                texNodeName, texFilePath, texType, self.csDefaults)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create roughness nodes for {newShader.shadNodeName}")

                elif texType == 'transmission':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupTransmiss(
                                texNodeName, texFilePath, texType, self.csDefaults)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create transmission nodes for {newShader.shadNodeName}")

                elif texType == 'sss':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupSSS(
                                texNodeName, texFilePath, texType, self.csDefaults)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create sss nodes for {newShader.shadNodeName}")

                elif texType == 'emissive':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupEmission(

                                texNodeName, texFilePath, texType, self.csDefaults)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create emission nodes for {newShader.shadNodeName}")

                elif texType == 'opacity':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupOpacity(
                                texNodeName, texFilePath, texType, self.csDefaults)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create opacity nodes for {newShader.shadNodeName}")

                elif texType == 'normal':
                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupNormal(
                                texNodeName, texFilePath, texType, self.csDefaults)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create normal-map nodes for {newShader.shadNodeName}")

                elif texType == 'displacement':
                    # adjust zero scale if neccessary
                    if texFileType == 'exr':
                        zeroScaleValue = 0.0
                    else:
                        zeroScaleValue = 0.5

                    if texType in self.texTypeList:
                        continue
                    else:
                        try:
                            newShader.setupDisplacement(
                                texNodeName, texFilePath, texType, self.csDefaults, zeroScaleValue, self.dispHeight)
                            self.texTypeList.append(texType)
                        except:
                            print(
                                f"ERROR: failed to create Displacement nodes for {newShader.shadNodeName}")

        # renable when all working
        try:
            mel.eval(
                'hyperShadePanelGraphCommand("hyperShadePanel1", "clearGraph");')
        except (RuntimeError):
            print("hypershade panel not yet created")

    def removeEmptyGroups(self):
        """
        searches all empty groups within the scene and removes them
        """

        # delete empty groups
        transforms = cmds.ls(type='transform')
        if transforms:
            deleteList = []
            for tran in transforms:
                if cmds.nodeType(tran) == 'transform':
                    children = cmds.listRelatives(tran, c=True)
                    if children == None:
                        deleteList.append(tran)

            if deleteList:
                cmds.delete(deleteList)

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
            self.texTypeList.clear()
            cmds.delete('*_previewSphere_geo')
            if cmds.objExists(self.grpName):
                cmds.delete(self.grpName)
            # TODO move to own method
            # mel.eval('MLdeleteUnused;')  # TODO disable for first release
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
        # TODO ask user for recognized naming pattern
        for keys, values in self.texTypes.items():
            for val in values:
                if val in name.lower():
                    # returns texture types
                    return keys

    # def findFiles(self):
    #     """
    #     Walks down the given directory path and searches for files within each directory while creating a dictionary of all found directories and files.
    #     """
    #     self.dataDict.clear()
    #     acceptedFilesList = ['bmp', 'ico', 'jpg',
    #                          'jpeg', 'jng', 'pbm', 'pgm', 'png', 'ppm', 'tga', 'tiff', 'wbmp', 'xpm', 'gif', 'hdr', 'exr', 'j2k', 'jp2', 'pfm', 'webp', 'jpeg-xr', 'psd']

    #     try:
    #         os.path.exists(self.dataPath)
    #     except:
    #         raise ("choosen path does not exist")

    #     for path, directories, files in os.walk(self.dataPath):

    #         # ignore directories starting with '.' (.mayaSwatches, .vrayThumbs)
    #         if files and not any(part in os.path.split(path)[1].lower() for part in self.ignoreList):

    #             print(
    #                 f"file: {os.path.split(path)[1]}, value: {os.path.split(path)[1] not in self.ignoreList}")

    #             texList = []
    #             for file in files:
    #                 # check name for predefined list of file types
    #                 fileSplitList = file.split('.')
    #                 if fileSplitList[len(fileSplitList) - 1] in acceptedFilesList and not any(part in file for part in self.ignoreList):
    #                     texList.append(file)

    #             self.dataDict[path] = texList

    def check_for_wrong_type(self, ignore_list: list, search_string: str):
        pattern_list = ignore_list

        ignore_string = '('
        separator = '|'

        for item in pattern_list:
            ignore_string += item + separator

        pattern = re.compile(ignore_string[:-1] + ')', re.IGNORECASE)

        return pattern.search(search_string.lower())

    def findFiles(self, dataPath):
        """
        Walks down the given directory path and searches for files within each directory while creating a dictionary of all found directories and files.
        """
        # self.dataDict.clear() # doesn't work when recursion is used
        acceptedFilesList = ['bmp', 'ico', 'jpg',
                             'jpeg', 'jng', 'pbm', 'pgm', 'png', 'ppm', 'tga', 'tiff', 'wbmp', 'xpm', 'gif', 'hdr', 'exr', 'j2k', 'jp2', 'pfm', 'webp', 'jpeg-xr', 'psd']

        try:
            os.path.exists(dataPath)
        except:
            raise ("choosen path does not exist")

        names = os.listdir(dataPath)
        # print(names)
        texList = []
        dirList = []
        for name in names:
            # check if string is present in ignoreList
            if self.check_for_wrong_type(self.ignoreList, name):
                # print(f'{name} is present in the list')
                continue
            else:
                if os.path.isdir(os.path.join(dataPath, name)):
                    dirList.append(name)
                else:
                    # split filename and type, cut of '.' from filetype and compare with each filetype from acceptedFilesList and add to new list if True
                    if any(os.path.splitext(name)[1][1:] in acceptedType for acceptedType in acceptedFilesList):
                        texList.append(name)

        if len(texList) != 0:
            self.dataDict[dataPath] = texList

        # start recursive execusion
        for dir in dirList:
            self.findFiles(os.path.join(dataPath, dir))
