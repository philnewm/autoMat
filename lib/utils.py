from maya import cmds
import logging
import os
import re
from enum import Enum

logging.basicConfig()
logger = logging.getLogger('utils')
# TODO change log level to info before merging to test
logger.setLevel(logging.DEBUG)

# ========== connect nodes ==========


def connect_color_channel(source_socket, destination_socket):
    cmds.connectAttr(source_socket, destination_socket, force=True)
    logging.debug(f"connected: {source_socket} to {destination_socket}")


def connect_single_color_channel(source_socket, destination_socket):
    cmds.connectAttr(source_socket + 'R', destination_socket)

# ========== clean-up ==========


def delete_history(selection=None):
    cmds.select(selection)
    cmds.delete(constructionHistory=True)


# ========== data ==========
class shader(Enum):
    color = 'diffuse'
    metal = 'metal'
    rough = 'rough'
    opacity = 'opacity'
    normal = 'normal'
    displacement = 'displacement'
    subsurf = 'sss'


class shading_group(Enum):
    vp_preview = 'vp_surface'
    arnold = 'ai_surface'
    vray = 'vr_surface'
    redshift = 'rs_surface'
    displacement = 'displacement'
    redshift_displacement = 'rs_displacement'


shading_group_dict = {shading_group.vp_preview: 'surfaceShader',
                      shading_group.arnold: 'aiSurfaceShader',
                      shading_group.vray: 'vraySpecificSurfaceShader',
                      shading_group.redshift: 'rsSurfaceShader',
                      shading_group.displacement: 'displacementShader',
                      shading_group.redshift_displacement: 'rsDisplacementShader'}


def find_files(dataPath):
    """
    Walks down the given directory path and searches for files within each directory while creating a dictionary of all found directories and files.

    Args:
        datapath (str): folder path to start recursive search
    """
    # BUG self.dataDict.clear() # doesn't work when recursion is used
    acceptedFilesList = ['exr', 'tga', 'tiff', 'tif', 'png', 'jpg', 'jpeg', 'bmp', 'ico', 'jng', 'pbm',
                         'pgm', 'ppm', 'wbmp', 'xpm', 'gif', 'hdr', 'j2k', 'jp2', 'pfm', 'webp', 'jpeg-xr', 'psd']

    if os.path.exists(dataPath):
        names = os.listdir(dataPath)
        logger.debug(f"Found directories: {names} in path: {dataPath}")
    else:
        logger.warning("Given Path does not exist!")
        return

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


def check_for_wrong_type(ignore_list: list, search_string: str):
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


if __name__ == '__main__':
    # add testing code for this script file here
    pass
