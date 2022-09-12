from maya import cmds
import importFiles
import nodes
import os

path = "/mnt/Projects/tmp/autoMat_rnd/sourceimages/textures/"


# for key, value in importFiles.find().items():
#     # TODO make less crappy calling
#     print(f"key: {key}")
#     for v in value:
#         newTex = nodes.FileNode(v.split('.')[0], os.path.join(key, v))
#         newTex.loadImage()


class autoMat(object):
    def __init__(self, shaderNodeName: str, texNodeName: str, renderEngine: str = 'arnold') -> None:
        self.shaderNodeName = os.path.split(shaderNodeName)[1]
        self.texNodeName = os.path.split(texNodeName)[0]
        self.renderEngine = renderEngine

    def extractFromPath(self):
        self.shaderNodeName = os.path.split(self.path)[0]
        print(self.shaderNodeName)


if __name__ == '__main__':
    importFiles = importFiles.TextureImport(path)
    for key, value in importFiles.find().items():
        nodes.PBRShader(os.path.split(
            key)[1]).createArnoldPBRShader()
        for v in value:
            # print(v.split('.')[0], os.path.join(key, v), sep='\t')
            nodes.FileNode(v.split('.')[0], os.path.join(key, v), debug=True)
