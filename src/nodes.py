from maya import cmds


class FileNode(object):
    def __init__(self, name: str, path: str, renderEngine: str = 'arnold') -> None:
        self.name = name
        self.filePath = path
        self.col_cs = "Input - Generic - sRGB - Texture"
        self.util_cs = "Utility - Raw"
        self.renderEngine = renderEngine
        self.texType = 'diffuse'
        self.nodeName = None

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

        if renderEngine == 'arnold':
            self.imageNode = 'aiImage'
        else:
            self.imageNode = 'file'  # TODO check for correct naming

        self.nodeName = cmds.shadingNode(
            self.imageNode, name=name, asTexture=True, isColorManaged=True)

    def loadImage(self):
        # import image
        # TODO create seperat assignment for non arnold file node
        cmds.setAttr(self.nodeName + '.filename',
                     self.filePath, type='string')

    def setColorSpace(self):
        if self.texType == 'diffuse':  # TODO remove double if
            cmds.setAttr(self.nodeName + '.colorSpace',
                         self.col_cs, type='string')
        else:
            cmds.setAttr(self.nodeName + '.colorSpace',
                         self.util_cs, type='string')

    def getType(self, name: str):
        # TODO check image for color or grayscale
        # TODO ask user for recognized pattern
        for keys, values in self.texTypes.items():
            for val in values:
                if val in name.lower():

                    # returns texture types
                    return keys


# test code
path = "/mnt/Projects/tmp/autoMat_rnd/sourceimages/textures/medieval_windows_29_73/medieval_windows_29_73_diffuse.jpg"
newFileNode = FileNode('SampleTexture', path, 'maya')
newFileNode.loadImage()
newFileNode.setColorSpace()
