from maya import cmds
import importFiles
import nodes
import os

path = "/mnt/Projects/tmp/autoMat_rnd/sourceimages/textures/"

newImport = importFiles.TextureImport(path)

for key, value in newImport.find().items():
    # TODO make less crappy calling
    print(f"key: {key}")
    for v in value:
        newTex = nodes.FileNode(v.split('.')[0], os.path.join(key, v))
        newTex.loadImage()
