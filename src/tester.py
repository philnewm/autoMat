import os
import re

dataPath = "/mnt/Projects/tmp/autoMat_rnd/sourceimages"

acceptedFilesList = ['bmp', 'ico', 'jpg',
                     'jpeg', 'jng', 'pbm', 'pgm', 'png', 'ppm', 'tga', 'tiff', 'wbmp', 'xpm', 'gif', 'hdr', 'exr', 'j2k', 'jp2', 'pfm', 'webp', 'jpeg-xr', 'psd']
ignoreList = ["^\.", "prev", "thumbs", "swatch"]

# ignorePattern = re.compile(r'(\.|prev|thumb|swatch)')

dataDict = {}


def check_for_wrong_type(ignore_list: list, search_string: str):
    pattern_list = ignore_list

    ignore_string = '('
    separator = '|'

    for item in pattern_list:
        ignore_string += item + separator

    pattern = re.compile(ignore_string[:-1] + ')', re.IGNORECASE)

    return pattern.search(search_string.lower())


def scan_dir(dataPath, acceptedFilesList, ignoreList):
    names = os.listdir(dataPath)
    texList = []
    dirList = []
    for name in names:
        # check if string is present in ignoreList
        if check_for_wrong_type(ignoreList, name):
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
        dataDict[dataPath] = texList

    # start recursive execusion
    for dir in dirList:
        scan_dir(os.path.join(dataPath, dir), acceptedFilesList, ignoreList)


scan_dir(dataPath, acceptedFilesList, ignoreList)

for key, value in dataDict.items():
    print(key, value, sep=' : ')
