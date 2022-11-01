import os


dataPath = "/mnt/Projects/tmp/autoMat_rnd/sourceimages"
acceptedFilesList = ['bmp', 'ico', 'jpg',
                     'jpeg', 'jng', 'pbm', 'pgm', 'png', 'ppm', 'tga', 'tiff', 'wbmp', 'xpm', 'gif', 'hdr', 'exr', 'j2k', 'jp2', 'pfm', 'webp', 'jpeg-xr', 'psd']
ignoreList = [".", "previews", "Thumbs",
              "vdcjfiw_Preview.png", ".vrayThumbs", ".mayaSwatches"]

dataDict = {}


def scan_dir(dataPath, acceptedFilesList, ignoreList):
    names = os.listdir(dataPath)
    # check if string is present in list
    texList = []
    dirList = []
    for name in names:
        if any(name in ignoreItem for ignoreItem in ignoreList):
            continue
        # print(f'{name} is present in the list')
        else:
            if os.path.isdir(os.path.join(dataPath, name)):
                dirList.append(name)
            else:
                # split filename and type, cut of '.' from filetype and compare with each filetype from acceptedFilesList and add to new list if True
                if any(os.path.splitext(name)[1][1:] in acceptedType for acceptedType in acceptedFilesList):
                    texList.append(name)
    if len(texList) != 0:
        dataDict[dataPath] = texList

    for dir in dirList:
        scan_dir(os.path.join(dataPath, dir), acceptedFilesList, ignoreList)


scan_dir(dataPath, acceptedFilesList, ignoreList)

for key, value in dataDict.items():
    print(key, value, sep=' : ')
