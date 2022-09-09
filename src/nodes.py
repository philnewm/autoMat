from maya import cmds
import os


class FileNode(object):
    def __init__(self, imagePath: str, renderEngine: str = 'arnold', debug: bool = 0) -> None:
        self.nodeName = None
        self.filePath = imagePath
        # TODO change for maya default aces
        self.col_cs = "Input - Generic - sRGB - Texture"
        self.util_cs = "Utility - Raw"  # TODO change for maya default aces
        self.colorSpace = None
        self.renderEngine = renderEngine
        self.texType = None
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
        self.createNode()
        self.loadImage()
        self.getType()
        self.setColorSpace()

    def splitName(self):
        self.nodeName = os.path.split(self.filePath)[1].split('.')[0]

        if self.debug:
            print(f"node name: {self.nodeName}, path: {self.filePath}")

    def createNode(self):
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

        return self.imageNode

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
            self.colorSpace = self.util_cs

        cmds.setAttr(self.nodeName + '.ignoreColorSpaceFileRules', 1)
        if self.debug:
            print(f"Texture Color conversion: {self.colorSpace}")

    def colorOut(self):
        return self.nodeName + '.outColor'

    def redColorOut(self):
        return self.nodeName + '.outColor.outColorR'

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


class TriPlanarNode(object):
    def __init__(self, nodeName: str = 'aiTriplanar', blend: float = 0.5, renderEngine: str = 'arnold', debug: bool = 0) -> None:
        self.blendValue = blend
        self.renderEngine = renderEngine
        self.nodeName = nodeName
        self.triPlanar = None
        self.inputCon = None
        self.debug = debug
        self.inputCon = None

        self.createNode()

    def createNode(self):
        # create triplanar
        if self.renderEngine == 'arnold':
            self.triPlanar = cmds.shadingNode(
                'aiTriplanar', name=self.nodeName, asTexture=True)
            cmds.setAttr(self.triPlanar + '.blend', self.blendValue)
        if self.renderEngine == 'vray':
            # TODO  check vray triplanar
            pass

        if self.renderEngine == 'redshift':
            # TODO  check redshift triplanar
            pass

        if self.debug:
            print(f"Triplanar node: {self.triPlanar}")

        return self.triPlanar

    def connect(self, inputConnection):
        self.inputCon = inputConnection
        cmds.connectAttr(self.inputCon,
                         self.triPlanar + '.input', force=True)
        if self.debug:
            print(
                f"connected: {self.inputCon} and {self.triPlanar + '.input'}")


class NormalMapNode(object):
    def __init__(self, nodeName: str = 'aiNormalMap', normalStrength: float = 1.0, renderEngine: str = 'arnold') -> None:
        self.nodeName = nodeName
        self.strength = normalStrength
        self.normalNode = None
        self.renderEngine = renderEngine

        self.createNode()

    def createNode(self):
        if self.renderEngine == 'arnold':
            self.normalNode = cmds.shadingNode(
                'aiNormalMap', name=self.nodeName, asUtility=True)
        else:
            pass

        print(f"Node created: {self.normalNode}")

    def setStrength(self):
        pass

    def connect(self, inputConnection):
        self.inputCon = inputConnection
        cmds.connectAttr(self.inputCon,
                         self.normalNode + '.input', force=True)
        if self.debug:
            print(
                f"connected: {self.inputCon} and {self.normalNode + '.input'}")

    def normalOut(self):
        return self.nodeName + '.outValue'


class DisplacementNode(object):
    def __init__(self, nodeName: str = 'dispalacementShader', scale: int = 1) -> None:
        self.nodeName = nodeName
        self.scale = scale
        self.dispNode = None

        self.createNode()

    def createNode(self):
        # TODO check if different nodes for other engines
        self.dispNode = cmds.shadingNode(
            'displacementShader', name=self.nodeName, asShader=True)
        print(f"Node created: {self.dispNode}")

    def setStrength(self):
        cmds.setAttr(self.dispNode + '.scale', self.scale)

    def connect(self, inputConnection):
        self.inputCon = inputConnection
        cmds.connectAttr(self.inputCon,
                         self.dispNode + '.displacement', force=True)
        if self.debug:
            print(
                f"connected: {self.inputCon} and {self.dispNode + '.displacement'}")


class PBRShader(object):
    def __init__(self, nodeName: str = 'PBRShader', renderEngine: str = 'arnold') -> None:
        self.nodeName = nodeName
        self.renderEngine = renderEngine
        self.shader = None

    def createArnoldPBRShader(self):
        self.shader = cmds.shadingNode(
            'aiStandardSurface', name=self.nodeName, asShader=True)

    def createVrayPBRShader(self):
        pass
        # TODO name of vray pbr shader
        # self.shader =

    # smarter decision for engine specific types needed
    def createRedshiftPBRShader(self):
        self.shader = cmds.shadingNode(
            'RedshiftMaterial', name=self.nodeName, asShader=True)

    def connectDiff(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.shader + '.baseColor', force=True)

    def connectMetal(self, inputConnection):
        print(inputConnection)
        cmds.connectAttr(inputConnection,
                         self.shader + '.metalness', force=True)

    def connectRough(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.shader + '.specularRoughness', force=True)

    def connectNormal(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.shader + '.normalCamera', force=True)


# test code
if __name__ == '__main__':
    diffPath = "sourceimages/textures/medieval_windows_29_73/medieval_windows_29_73_diffuse.jpg"
    metalPath = "sourceimages/textures/medieval_windows_29_73/medieval_windows_29_73_metalness.jpg"
    roughPath = "sourceimages/textures/medieval_windows_29_73/medieval_windows_29_73_roughness.jpg"
    normalPath = "sourceimages/textures/medieval_windows_29_73/medieval_windows_29_73_normal.jpg"

    # this ones nice
    # dispFileNode = FileNode(path, debug=1)
    # dispMapNode = DisplacementNode()
    # dispMapNode.connect(dispFileNode.colorOut())
    #
    newShader = PBRShader(os.path.split(os.path.split(diffPath)[0])[1])
    newShader.createArnoldPBRShader()
    newDiffTex = FileNode(diffPath, debug=1)
    newMetalTex = FileNode(metalPath, debug=1)
    newRoughTex = FileNode(roughPath, debug=1)
    newNormalTex = FileNode(normalPath, debug=1)
    newNormaMap = NormalMapNode()
    newShader.connectDiff(newDiffTex.colorOut())
    newShader.connectMetal(newMetalTex.redColorOut())
    newShader.connectRough(newRoughTex.redColorOut())
    newShader.connectNormal(newNormaMap.normalOut())
    newNormaMap.connect(newNormalTex.colorOut())
