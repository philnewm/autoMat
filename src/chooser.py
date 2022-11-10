import os

dataPath = "/mnt/Projects/tmp/autoMat_rnd/sourceimages/textures/wood_veneer_vdcjfiw"

acceptedFilesList = ['exr', 'tga', 'tiff', 'png', 'jpg', 'jpeg', 'bmp', 'ico', 'jng', 'pbm',
                     'pgm', 'ppm', 'wbmp', 'xpm', 'gif', 'hdr', 'j2k', 'jp2', 'pfm', 'webp', 'jpeg-xr', 'psd']

texList = []
nexList = ['hello', 'what up']

names = os.listdir(dataPath)

for name in names:
    if os.path.isfile(os.path.join(dataPath, name)) and any(os.path.splitext(name)[1][1:] == fileType for fileType in acceptedFilesList):

        if not any(os.path.splitext(name)[0] in os.path.splitext(texture)[0] for texture in texList):
            texList.append(name)

            print(texList)

        else:
            newType_index = acceptedFilesList.index(
                os.path.splitext(name)[1][1:])

            for texture in texList:
                if os.path.splitext(texture)[0] == os.path.splitext(name)[0]:
                    oldType_index = acceptedFilesList.index(
                        os.path.splitext(texture)[1][1:])

                    if newType_index < oldType_index:
                        print(
                            f"replacing: {texture} of index: {oldType_index} with {name}")
                        texList[texList.index(texture)] = name
print(texList)
