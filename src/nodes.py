from maya import cmds
import os


class FileNode(object):
    def __init__(self, imagePath: str, renderEngine: str = 'arnold', debug: bool = 0) -> None:
        self.nodeName = None
        self.filePath = path
        self.col_cs = "Input - Generic - sRGB - Texture"
        self.util_cs = "Utility - Raw"
        self.colorSpace = None
        self.renderEngine = renderEngine
        self.texType = 'diffuse'
        self.name = None
        self.enableAutoTX = 1
        self.debug = debug

        # TODO check if really neccessary here
        self.texTypes = {'diffuse': ('diff', 'albedo', 'color', 'rgb'),
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

        # setup parameter
        self.splitName()
        self.createImageNode()
        self.loadImage()
        self.getType()
        self.setColorSpace()

    def splitName(self):
        self.nodeName = os.path.split(self.filePath)[1].split('.')[0]

        if self.debug:
            print(f"node name: {self.nodeName}, path: {self.filePath}")

    def createImageNode(self):
        # check which file node to create
        if self.renderEngine == 'arnold':
            self.imageNode = 'aiImage'
            # create file node
            self.name = cmds.shadingNode(
                self.imageNode, name=self.nodeName, asTexture=True, isColorManaged=True)

        else:
            self.imageNode = 'file'  # TODO check for correct naming

        # maybe remove
        if self.debug:
            print(f"file node: {self.imageNode}")

    def loadImage(self):
        # import image
        cmds.setAttr(self.nodeName + '.filename',
                     self.filePath, type='string')
        cmds.setAttr(self.nodeName + '.autoTx', self.enableAutoTX)

        if self.debug:
            print(
                f"image imported: {self.filePath}, auto tx: {self.enableAutoTX}")

    def setColorSpace(self):
        if self.texType == 'diffuse':  # TODO remove double if
            cmds.setAttr(self.nodeName + '.colorSpace',
                         self.col_cs, type='string')
            self.colorSpace = self.col_cs
        else:
            cmds.setAttr(self.nodeName + '.colorSpace',
                         self.util_cs, type='string')
            self.colorSpace = self.col_cs

        cmds.setAttr(self.nodeName + '.ignoreColorSpaceFileRules', 1)
        if self.debug:
            print(f"Texture Color conversion: {self.colorSpace}")

    def getType(self):
        # TODO check image for color or grayscale
        # TODO ask user for recognized pattern
        texName = os.path.split(self.filePath)[1]
        texName = texName.split('.')[0]
        for keys, values in self.texTypes.items():
            for val in values:
                if val in texName.lower():
                    self.texType = keys
                    if self.debug:
                        print(f"texture type: {self.texType}")
                    # returns texture types
                    return keys


# test code
if __name__ == '__main__':
    path = "/sourceimages/textures/medieval_windows_29_73/medieval_windows_29_73_diffuse.jpg"
    newFileNode = FileNode(path, debug=1)
