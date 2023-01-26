# This code uses mainly the nodes.py content to setup mroe complex processes
# The loading loading  and sorting functions got a custome implementation

# only for WIP with maya to make sure all changes get reloaded
import logging
from importlib import reload

from maya import cmds
import maya.mel as mel
from math import sqrt
import os
import re
# Only use when script gets executed from Maya script editor
from autoMat.src import nodes
# Only use when script gets executed from IDE
# import nodes
reload(nodes)  # TODO only for WIP with maya to make sure all changes get reloaded


logging.basicConfig()
logger = logging.getLogger('AutoMat')
logger.setLevel(logging.INFO)


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

        self.prevColor = None
        self.prevMetal = None
        self.prevRough = None
        self.prevGloss = None
        self.prevNormal = None
        self.prevDisp = None
        self.prevEmissive = None
        self.prevSSS = None
        self.prevTransmission = None
        self.prevOpacity = None
        self.prevCoat = None
        self.prevSheen = None

        # TODO try ro remove cause default values should be definied through UI
        # displacement values
        self.dispSubdivs = 3
        self.dispHeight = 1.0

        # triplanar values
        self.triScale = 0.65
        self.triBlend = 1

        # TODO implement button forthis one
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

        # NEWFEATURE implement clean LOD handling
        # README no LOD handling yet
        self.ignoreList = ["^\.", "prev",
                           "thumbs", "swatch", "lod[1-9]", "hdr"]

        self.specialCharsList = [" ", "-", ".", ",", ";", "#",
                                 "'", "´", "`", "!", "?", "%", "&", "~", "*"]

    # NEWFEATURE find cleaner way to implement multiple materials setups
    # NEWFEATURE rewrite implementation for switching to triplanar setup
    def setupMaterialTrip(self, showInVP=True):
        """
        This Sets up a complete PBR material based on available textures using triplanar mapping.

        Args:
            showInVP (bool, optional): Set if materials should be visible in maya viewport or not. Defaults to True.
        """
        self.delPrevSpheres()
        moveStep = 0
        columns = round(sqrt(len(self.dataDict.keys())))
        shaderNameOffset = 1

        if not cmds.objExists(self.grpName):
            cmds.group(empty=True, name=self.grpName)

        self.orgSphere = None

        for key, value in self.dataDict.items():
            self.texTypeList.clear()

            # remove spaces , dots and "-" from node name
            shaderNodeName = self.replaceSpecialChars(
                os.path.split(key)[1], self.specialCharsList, "_")

            # add number to name and increment if node exists
            shaderNodeName = self.rename_shader_if_exists(
                shaderNodeName, '_AutoMatShader')

            # setup shader
            newShader = nodes.arnoldPBRShader(shaderNodeName)

            # assign to preview mesh
            newShader.assigntoSphere(-2 * (moveStep % columns), 0,
                                     (moveStep // columns) * 2, showInVP, self.orgSphere, dispSubdivs=self.dispSubdivs, dispHeight=self.dispHeight)
            moveStep += 1
            self.orgSphere = newShader.geoName

            for v in value:
                texNodeName, texFilePath, texType, texFileType = self.extractData(
                    key, v)

                # remove spaces , dots and "-" from node name
                texNodeName = self.replaceSpecialChars(
                    texNodeName, self.specialCharsList, "_")

                # add number to name and increment if node exists
                texNodeName = self.rename_if_exists(texNodeName)

                self.prevTexType = self.curTexType
                self.curTexType = texType

                # NEWFEATURE use loop for each shader channel
                if texType == 'color':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevColor)
                        continue
                    else:
                        self.prevColor = texNodeName
                        newShader.setupTripColor(
                            texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                        self.texTypeList.append(texType)

                elif texType == 'metalness':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevMetal)
                        continue
                    else:
                        self.prevMetal = texNodeName
                        newShader.setupTripMetalness(
                            texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                        self.texTypeList.append(texType)

                elif texType == 'roughness':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevRough)
                        continue
                    else:
                        self.prevRough = texNodeName
                        newShader.setupTripRoughness(
                            texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                        self.texTypeList.append(texType)

                elif texType == 'transmission':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevTransmission)
                        continue
                    else:
                        self.prevTransmission = texNodeName
                        newShader.setupTripTransmiss(
                            texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                        self.texTypeList.append(texType)

                elif texType == 'sss':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevSSS)
                        continue
                    else:
                        self.prevSSS = texNodeName
                        newShader.setupTripSSS(
                            texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                        self.texTypeList.append(texType)

                elif texType == 'emissive':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevEmissive)
                        continue
                    else:
                        self.prevEmissive = texNodeName
                        newShader.setupTripTransmiss(
                            texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                        self.texTypeList.append(texType)

                elif texType == 'opacity':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevOpacity)
                        continue
                    else:
                        self.prevOpacity = texNodeName
                        newShader.setupTripOpacity(
                            texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                        self.texTypeList.append(texType)

                elif texType == 'normal':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevNormal)
                        continue
                    else:
                        self.prevNormal = texNodeName
                        newShader.setupTripNormal(
                            texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale)
                        self.texTypeList.append(texType)

                elif texType == 'displacement':
                    # adjust zero scale if neccessary
                    if texFileType == 'exr':
                        zeroScaleValue = 0.0
                    else:
                        zeroScaleValue = 0.5

                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevDisp)
                        continue
                    else:
                        self.prevDisp = texNodeName
                        newShader.setupTripDisplacement(
                            texNodeName, texFilePath, texType, self.csDefaults, self.triBlend, self.triScale, zeroScaleValue, self.dispHeight)
                        self.texTypeList.append(texType)

            # TODO renable when all working
            try:
                mel.eval(
                    'hyperShadePanelGraphCommand("hyperShadePanel1", "clearGraph");')
            except (RuntimeError):
                print("hypershade panel not yet created")

    # TODO find cleaner way to implement multiple materials setups
    # TODO use render engine spcific naming in shader
    def setupMaterial(self, showInVP=True):
        """
        This Sets up a complete PBR material based on available textures.

        Args:
            showInVP (bool, optional): Set if materials should be visible in maya viewport or not. Defaults to True.
        """
        self.delPrevSpheres()
        moveStep = 0
        columns = round(sqrt(len(self.dataDict.keys())))

        if not cmds.objExists(self.grpName):
            cmds.group(empty=True, name=self.grpName)

        self.orgSphere = None

        for key, value in self.dataDict.items():
            self.texTypeList.clear()

            # remove spaces , dots and "-" from node name
            shaderNodeName = self.replaceSpecialChars(
                os.path.split(key)[1], self.specialCharsList, "_")

            # add number to name and increment if node exists
            shaderNodeName = self.rename_shader_if_exists(
                shaderNodeName, '_AutoMatShader')

            # setup shader
            newShader = nodes.arnoldPBRShader(shaderNodeName)

            # assign to preview mesh
            newShader.assigntoSphere(-2 * (moveStep % columns), 0,
                                     (moveStep // columns) * 2, showInVP, self.orgSphere, dispSubdivs=self.dispSubdivs, dispHeight=self.dispHeight)
            moveStep += 1
            self.orgSphere = newShader.geoName

            for v in value:
                texNodeName, texFilePath, texType, texFileType = self.extractData(
                    key, v)

                # remove spaces , dots and "-" from node name
                texNodeName = self.replaceSpecialChars(
                    texNodeName, self.specialCharsList, "_")

                # add number to name and increment if node exists
                texNodeName = self.rename_if_exists(texNodeName)

                self.prevTexType = self.curTexType
                self.curTexType = texType

                # NEWFEATURE loop through shader channels
                if texType == 'color':
                    if texType in self.texTypeList:
                        # TODO implement cleaner way of changing file nodes path
                        self.change_to_UDIM(self.prevColor)
                        continue
                    else:
                        self.prevColor = texNodeName
                        newShader.setupColor(
                            texNodeName, texFilePath, texType, self.csDefaults)
                        self.texTypeList.append(texType)

                elif texType == 'metalness':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevMetal)
                        continue
                    else:
                        self.prevMetal = texNodeName
                        newShader.setupMetalness(
                            texNodeName, texFilePath, texType, self.csDefaults)
                        self.texTypeList.append(texType)

                elif texType == 'roughness':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevRough)
                        continue
                    else:
                        self.prevRough = texNodeName
                        newShader.setupRoughness(
                            texNodeName, texFilePath, texType, self.csDefaults)
                        self.texTypeList.append(texType)

                elif texType == 'transmission':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevTransmission)
                        continue
                    else:
                        self.prevTransmission = texNodeName
                        newShader.setupTransmiss(
                            texNodeName, texFilePath, texType, self.csDefaults)
                        self.texTypeList.append(texType)

                elif texType == 'sss':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevSSS)
                        continue
                    else:
                        self.prevSSS = texNodeName
                        newShader.setupSSS(
                            texNodeName, texFilePath, texType, self.csDefaults)
                        self.texTypeList.append(texType)

                elif texType == 'emissive':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevEmissive)
                        continue
                    else:
                        self.prevEmissive = texNodeName
                        newShader.setupEmission(
                            texNodeName, texFilePath, texType, self.csDefaults)
                        self.texTypeList.append(texType)

                elif texType == 'opacity':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevOpacity)
                        continue
                    else:
                        self.prevOpacity = texNodeName
                        newShader.setupOpacity(
                            texNodeName, texFilePath, texType, self.csDefaults)
                        self.texTypeList.append(texType)

                elif texType == 'normal':
                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevNormal)
                        continue
                    else:
                        self.prevNormal = texNodeName
                        newShader.setupNormal(
                            texNodeName, texFilePath, texType, self.csDefaults)
                        self.texTypeList.append(texType)

                elif texType == 'displacement':
                    # adjust zero scale if neccessary
                    if texFileType == 'exr':
                        zeroScaleValue = 0.0
                    else:
                        zeroScaleValue = 0.5

                    if texType in self.texTypeList:
                        self.change_to_UDIM(self.prevDisp)
                        continue
                    else:
                        self.prevDisp = texNodeName
                        newShader.setupDisplacement(
                            texNodeName, texFilePath, texType, self.csDefaults, zeroScaleValue, self.dispHeight)
                        self.texTypeList.append(texType)

        # TODO create checkbox for this one
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

    def delPrevSpheres(self):
        """
        Cleans all existing materials and preview spheres from the maya scene.
        """
        try:
            # TODO setup list of created spheres for more effective delete
            self.texTypeList.clear()
            cmds.delete('*_previewSphere_geo')
            if cmds.objExists(self.grpName):
                cmds.delete(self.grpName)
        except ValueError:
            print("No Objects to delete")

    def delUnusedNodes(self):
        """
        delete all unused nodes using UI fucntion from hypershade
        """
        mel.eval('MLdeleteUnused;')
        mel.eval('scriptEditorInfo -clearHistory;')

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

    # use the ignore list
    def check_for_wrong_type(self, ignore_list: list, search_string: str):
        """
        Search for string patterns to ignore

        Args:
            ignore_list (list): list containing strings to ignore
            search_string (str): current string to evaluate

        Returns:
            _type_: True if any character combination mathcing the ignore list was found, False if not
        """

        ignore_string = '('
        separator = '|'

        for item in ignore_list:
            ignore_string += item + separator

        pattern = re.compile(ignore_string[:-1] + ')', re.IGNORECASE)

        return pattern.search(search_string.lower())

    def findFiles(self, dataPath):
        """
        Walks down the given directory path and searches for files within each directory while creating a dictionary of all found directories and files.

        Args:
            datapath (str): folder path to start recursive search
        """
        # BUG self.dataDict.clear() # doesn't work when recursion is used
        acceptedFilesList = ['exr', 'tga', 'tiff', 'tif', 'png', 'jpg', 'jpeg', 'bmp', 'ico', 'jng', 'pbm',
                             'pgm', 'ppm', 'wbmp', 'xpm', 'gif', 'hdr', 'j2k', 'jp2', 'pfm', 'webp', 'jpeg-xr', 'psd']

        try:
            os.path.exists(dataPath)
        except:
            raise ("choosen path does not exist")
        try:
            names = os.listdir(dataPath)
        except:
            print(
                f"ERROR: path does not exist {dataPath}")

        texList = []
        dirList = []
        for name in names:
            # check if string is present in ignoreList
            if self.check_for_wrong_type(self.ignoreList, name):
                continue
            else:
                if os.path.isdir(os.path.join(dataPath, name)):
                    dirList.append(name)
                else:
                    # split filename and type, cut of '.' from filetype and compare with each filetype from acceptedFilesList and add to new list if True
                    if any(os.path.splitext(name)[1][1:] in acceptedType for acceptedType in acceptedFilesList):
                        # Check if filename already exists in texture list in case of multiple files with different filetypes
                        if not any(os.path.splitext(name)[0] in os.path.splitext(texture)[0] for texture in texList):
                            texList.append(name)
                        else:
                            # get filetype index from acceptedFilesList and use for comparison
                            newType_index = acceptedFilesList.index(
                                os.path.splitext(name)[1][1:])

                            for texture in texList:
                                # find matching texture in texList and its file type, get its index from acceptedFilesList
                                if os.path.splitext(texture)[0] == os.path.splitext(name)[0]:
                                    oldType_index = acceptedFilesList.index(
                                        os.path.splitext(texture)[1][1:])

                                    # switch to higher priority filetype if neccessary
                                    if newType_index < oldType_index:
                                        logger.debug(
                                            f"replacing: {texture} of index: {oldType_index} with {name}")
                                        texList[texList.index(texture)] = name

        if len(texList) != 0:
            self.dataDict[dataPath] = texList

        # start recursive execusion of dir searching
        for dir in dirList:
            self.findFiles(os.path.join(dataPath, dir))

    def change_to_UDIM(self, nodeName: str):
        """
        Replace 4 combined digits with <udim> tag if multiple texture files per channel are found

        Args:
            nodeName (str): file node name
        """

        # import images as UDIMs
        imagePath = cmds.getAttr(nodeName + '.filename')
        udim = re.search(r'\d{4}', os.path.split(imagePath)[1])

        if udim:
            try:
                udim_sequence = udim.group(0)
                udim_sequence = imagePath.replace(udim_sequence, '<udim>')

                cmds.setAttr(nodeName + '.filename',
                             udim_sequence, type='string')
                logger.info(
                    f"image changed to udims: {udim_sequence}")
            except:
                print(
                    f"ERROR: Unable to setup up UDIMs for {imagePath}")
            return

        logger.info(
            f"image not changed to udims")

# TODO !!!CREATE NEW NODE CLASS TO HANDLE ALL SPECIAL EXCEPTIONS!!!

    def replaceSpecialChars(self, input_string: str, replaceCharList: list, replaceChar):
        """
        Replace all scpecial characters from replaceCharList found in inoput_string.

        Args:
            input_string (str): String to check for special characters
            replaceCharList (list): list of characters to replace
            replaceChar (_type_): new character to replace it with

        Returns:
            _type_: string without special characters
        """
        for item in replaceCharList:
            input_string = input_string.replace(item, replaceChar)

        logger.debug(f"Converted string: {input_string}")
        return input_string

    def rename_if_exists(self, node_name: str):
        """
        Check if node_name already exists in the running maya instance
        Add counter to name in case node_name already exists

        Args:
            node_name (str): string to check against current maya instance

        Returns:
            str: input string as is or string with added counter
        """
        counter = 1  # init counter

        if cmds.objExists(node_name):

            while cmds.objExists(node_name + str(counter)):
                counter += 1

            return node_name + str(counter)
        else:

            return node_name

    def rename_shader_if_exists(self, node_name: str, suffix: str = '_AutoMatShader'):
        """
        Check if node_name already exists as shader node name in the running maya instance
        Add counter to name in case node_name already exists
        Is also able to use a suffix for shader node name identification

        Args:
            node_name (str): string to check against current maya instance
            suffix (str): string to add to shader node name

        Returns:
            str: input string as is or string with added counter
        """
        counter = 1  # init counter

        if cmds.objExists(node_name + suffix):

            while cmds.objExists(node_name + str(counter) + suffix):
                counter += 1

            return node_name + str(counter)
        else:

            return node_name
