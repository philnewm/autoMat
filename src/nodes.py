from maya import cmds
import os
import re


class FileNode(object):
    def __init__(self, nodeName: str, imagePath: str, texType: str, csDefaults: tuple = (
            "Input - Generic - sRGB - Texture", "Utility - Raw"), renderEngine: str = 'arnold', enableAutoTX: bool = True, debug: bool = False) -> None:
        self.nodeName = nodeName
        self.filePath = imagePath
        self.udim = re.search(r'\d\d\d\d', os.path.split(imagePath)[1])
        self.col_cs, self.util_cs = csDefaults
        self.colorSpace = None
        self.renderEngine = renderEngine
        self.texType = texType
        self.name = None
        self.enableAutoTX = enableAutoTX
        self.debug = debug

        self.colorOut = self.nodeName + '.outColor'
        self.redColorOut = self.nodeName + '.outColor.outColorR'

        if texType:
            self.createNode()
            self.loadImage()
            self.setColorSpace()

    def createNode(self):
        # check which file node to create
        print(self.renderEngine)
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

        return self.nodeName

    def loadImage(self):
        # import image
        if self.udim:
            udim_sequence = self.udim.group(0)
            udim_sequence = self.filePath.replace(udim_sequence, '<udim>')

            cmds.setAttr(self.nodeName + '.filename',
                         udim_sequence, type='string')
            if self.debug:
                print(
                    f"image imported: {udim_sequence}, auto tx: {self.enableAutoTX}")
            return

        cmds.setAttr(self.nodeName + '.filename',
                     self.filePath, type='string')
        cmds.setAttr(self.nodeName + '.autoTx', self.enableAutoTX)

        if self.debug:
            print(
                f"image imported: {self.filePath}, auto tx: {self.enableAutoTX}")
        # TODO option for udims

    def setColorSpace(self):
        if self.texType == 'color':
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


class TriPlanarNode(object):
    def __init__(self, nodeName: str = 'aiTriplanar', blend: float = 0.5, scale: float = 1.0, renderEngine: str = 'arnold', debug: bool = False) -> None:
        self.blendValue = blend
        self.renderEngine = renderEngine
        self.nodeName = nodeName + '_trip'
        self.triPlanar = None
        self.dataIn = self.nodeName + '.input'
        self.debug = debug
        self.outColor = self.nodeName + '.outColor'
        self.outColorRed = self.outColor + '.outColorR'
        self.blend = self.nodeName + '.blend'
        self.scale = scale

        self.createNode()
        self.setScale()

    def createNode(self):
        # create triplanar
        if self.renderEngine == 'arnold':
            self.triPlanar = cmds.shadingNode(
                'aiTriplanar', name=self.nodeName, asTexture=True)
            cmds.setAttr(self.blend, self.blendValue)
        if self.renderEngine == 'vray':
            # TODO  check vray triplanar
            pass

        if self.renderEngine == 'redshift':
            # TODO  check redshift triplanar
            pass

        if self.debug:
            print(f"Triplanar node: {self.triPlanar}")

        return self.nodeName

    def setBlend(self, blend: float):
        self.blendValue = blend
        cmds.setAttr(self.blend, self.blendValue)

        if self.debug:
            print(f"changed blend value to: {self.blendValue}")

    def setScale(self):
        cmds.setAttr(self.nodeName + '.scaleX', self.scale)
        cmds.setAttr(self.nodeName + '.scaleY', self.scale)
        cmds.setAttr(self.nodeName + '.scaleZ', self.scale)

    def connectColor(self, input, output):
        cmds.connectAttr(input,
                         self.dataIn, force=True)
        cmds.connectAttr(self.outColor, output, force=True)

        if self.debug:
            print(f"connected {input} as input and {output} as output")

    def connectData(self, input, output):  # very spaghetti
        cmds.connectAttr(input,
                         self.dataIn, force=True)
        cmds.connectAttr(self.outColorRed, output, force=True)

        if self.debug:
            print(f"connected {input} as input and {output} as output")

    def connectIn(self, input):
        cmds.connectAttr(input, self.dataIn, force=True)

        if self.debug:
            print(f"connected {input} as input to {self.dataIn}")

    def connectOut(self, output):
        cmds.connectAttr(self.outColor, output, force=True)

        if self.debug:
            print(f"connected {self.outColor} as input to {output}")


class NormalMapNode(object):
    def __init__(self, nodeName: str = 'aiNormalMap', normalStrength: float = 1.0, renderEngine: str = 'arnold', debug: bool = False) -> None:
        self.nodeName = nodeName + '_aiNormalMap'
        self.strength = normalStrength
        self.normalNode = None
        self.renderEngine = renderEngine
        self.normalOut = self.nodeName + '.outValue'
        self.dataIn = self.nodeName + '.input'
        self.debug = debug

        self.createNode()

    def createNode(self):
        if self.renderEngine == 'arnold':
            self.normalNode = cmds.shadingNode(
                'aiNormalMap', name=self.nodeName, asUtility=True)
        else:
            pass

        print(f"NormalMap Node created: {self.normalNode}")

    def setStrength(self):
        pass

    def connect(self, input, output):
        cmds.connectAttr(input, self.dataIn, force=True)
        cmds.connectAttr(self.normalOut, output, force=True)
        if self.debug:
            print(f"connected {input} as input and {output} as output")

    def connectIn(self, input):
        cmds.connectAttr(input, self.dataIn, force=True)

        if self.debug:
            print(f"connected {input} as input to {self.dataIn}")

    def connectOut(self, output):
        cmds.connectAttr(self.normalOut, output, force=True)

        if self.debug:
            print(f"connected {self.normalOut} as input to {output}")


class DisplacementNode(object):
    def __init__(self, nodeName: str = 'dispalacementShader', scale: int = 1, debug: bool = False) -> None:
        self.nodeName = nodeName + '_dispShader'
        self.scale = scale
        self.dispNode = None
        self.dispIn = self.nodeName + '.displacement'
        self.dispOut = self.nodeName + '.displacement'
        self.debug = debug

        # execute default methods
        self.createNode()

    def createNode(self):
        # TODO check if different nodes for other render engines
        self.dispNode = cmds.shadingNode(
            'displacementShader', name=self.nodeName, asShader=True)
        print(f"Node created: {self.dispNode}")

    def setScale(self):
        cmds.setAttr(self.dispNode + '.scale', self.scale)

    def connect(self, input: str, output: str):
        cmds.connectAttr(input,
                         self.dispIn, force=True)
        cmds.connectAttr(self.dispOut, output, force=True)
        if self.debug:
            print(
                f"connected: {input} as input and {output} as output")

    def connectIn(self, input: str):
        cmds.connectAttr(input,
                         self.dispIn, force=True)
        if self.debug:
            print(
                f"connected: {input} as input to {self.dispIn}")

    def connectOut(self, output: str):
        cmds.connectAttr(self.dispOut, output,
                         force=True)
        if self.debug:
            print(
                f"connected: {self.dispOut} as input to {output}")


class arnoldPBRShader(object):
    def __init__(self, nodeName: str = 'PBRShader', debug: bool = False) -> None:
        self.nodeName = nodeName
        self.geoName = nodeName + '_previewSphere_geo'
        self.shadNodeName = nodeName + '_AutoMatShader'
        self.shadingGrpName = nodeName + '_shaGrp'
        self.shadGrp = None
        self.colorOut = self.shadNodeName + '.outColor'
        self.baseCol = self.shadNodeName + '.baseColor'
        self.metal = self.shadNodeName + '.metalness'
        self.rough = self.shadNodeName + '.specularRoughness'
        self.normal = self.shadNodeName + '.normalCamera'
        self.udimFlag = False

        cmds.shadingNode('aiStandardSurface',
                         name=self.shadNodeName, asShader=True)

    # Methods to connect textures to shader channels
    def connColor(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.baseCol, force=True)

    def connMetal(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.metal, force=True)

    def connRough(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.rough, force=True)

    def connNormal(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.normal, force=True)

    def connColOut(self, output):
        cmds.connectAttr(self.colorOut, output, force=True)

    def assigntoSphere(self, translateX: float = 0.0, translateY: float = 0.0, translateZ: float = 0.0, scaleZeroValue: float = 0.0, dispInVP=True, grpName: str = 'Preview_Spheres_grp', debug: bool = False):

        # create shading group
        self.shadGrp = ShadingGroup(
            self.shadingGrpName, debug=debug)
        self.shadingGrpName = self.shadGrp.nodeName
        self.grpName = grpName

        # connect shading group
        self.connColOut(self.shadGrp.aiSurfaceShaderInput)
        if dispInVP:
            self.connColOut(self.shadGrp.surfaceShaderInput)

        # create preview sphere
        self.prevSphere = PrevSphere(
            self.geoName, 3, dispHeight=0.1)

        # group all preview spheres together
        cmds.parent(self.prevSphere.nodeName, self.grpName)

        # assign Shader
        self.prevSphere.assignShader(self.shadNodeName)
        self.prevSphere.moveOver(translateX, translateY, translateZ)

    def setupTripColor(self, texNodeName: str, texFilePath: str, texType: str, udim, csDefaults, triBlend: float = 0.5, triScale: float = 1.0):
        """
        Sets up nodes to triplanar project the diffuse texture

        Args:
            texNodeName (str): Texture nodes name
            texFilePath (str): Texture nodes file path
            texType (str): Texture nodes type
            csDefaults (_type_): Colorspace default value
            triBlend (float, optional): Triplanar blending value. Defaults to 0.5.
            triScale (float, optional): Triplanar scaling value. Defaults to 1.
        """

        tex = FileNode(texNodeName, texFilePath,
                       texType, udim, csDefaults, debug=True)
        triplanar = TriPlanarNode(
            texNodeName, triBlend, triScale)
        triplanar.connectColor(tex.colorOut, self.baseCol)

    def setupColor(self, texNodeName: str, texFilePath: str, texType: str, csDefaults):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, debug=True)
        self.connColor(tex.colorOut)

    def setupTripMetalness(self, texNodeName: str, texFilePath: str, texType: str, csDefaults, triBlend: float = 0.5, triScale: float = 1.0):
        """
        Sets up nodes to triplanar project the metal texture

        Args:
            texNodeName (str): Texture nodes name
            texFilePath (str): Texture nodes file path
            texType (str): Texture nodes type
            csDefaults (_type_): Colorspace default value
            triBlend (float, optional): Triplanar blending value. Defaults to 0.5.
            triScale (float, optional): Triplanar scaling value. Defaults to 1.
        """
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, debug=True)
        triplanar = TriPlanarNode(
            texNodeName, triBlend, triScale)
        triplanar.connectData(tex.colorOut, self.metal)

    def setupMetalness(self, texNodeName: str, texFilePath: str, texType: str, csDefaults):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, debug=True)
        self.connMetal(tex.redColorOut)

    def setupTripRoughness(self, texNodeName: str, texFilePath: str, texType: str, csDefaults, triBlend: float = 0.5, triScale: float = 1.0):
        """
        Sets up nodes to triplanar project the roughness texture

        Args:
            texNodeName (str): Texture nodes name
            texFilePath (str): Texture nodes file path
            texType (str): Texture nodes type
            csDefaults (_type_): Colorspace default value
            triBlend (float, optional): Triplanar blending value. Defaults to 0.5.
            triScale (float, optional): Triplanar scaling value. Defaults to 1.
        """
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, debug=True)
        triplanar = TriPlanarNode(
            texNodeName, triBlend, triScale)
        triplanar.connectData(tex.colorOut, self.rough)

    def setupRoughness(self, texNodeName: str, texFilePath: str, texType: str, csDefaults):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, debug=True)
        self.connRough(tex.redColorOut)

    def setupTripNormal(self, texNodeName: str, texFilePath: str, texType: str, csDefaults, triBlend: float = 0.5, triScale: float = 1.0):
        """
        Sets up nodes to triplanar project the normal texture

        Args:
            texNodeName (str): Texture nodes name
            texFilePath (str): Texture nodes file path
            texType (str): Texture nodes type
            csDefaults (_type_): Colorspace default value
            triBlend (float, optional): Triplanar blending value. Defaults to 0.5.
            triScale (float, optional): Triplanar scaling value. Defaults to 1.
        """
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, debug=True)
        triplanar = TriPlanarNode(
            texNodeName, triBlend, triScale)
        normalMap = NormalMapNode(texNodeName)
        triplanar.connectColor(tex.colorOut, normalMap.dataIn)
        self.connNormal(normalMap.normalOut)

    def setupNormal(self, texNodeName: str, texFilePath: str, texType: str, csDefaults):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, debug=True)
        normalMap = NormalMapNode(texNodeName)
        normalMap.connect(tex.colorOut, self.normal)

    def setupTripDisplacement(self, texNodeName: str, texFilePath: str, texType: str, csDefaults, triBlend: float = 0.5, triScale: float = 1.0, zeroScaleValue: float = 0.0):
        """
        Sets up nodes to triplanar project the displacement texture

        Args:
            texNodeName (str): Texture nodes name
            texFilePath (str): Texture nodes file path
            texType (str): Texture nodes type
            csDefaults (_type_): Colorspace default value
            triBlend (float, optional): Triplanar blending value. Defaults to 0.5.
            triScale (float, optional): Triplanar scaling value. Defaults to 1.
        """
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, debug=True)
        dispNode = DisplacementNode(texNodeName, scale=1.0)
        triplanar = TriPlanarNode(texNodeName, triBlend, triScale)
        triplanar.connectData(tex.colorOut, dispNode.dispIn)
        cmds.connectAttr(dispNode.dispOut, self.shadGrp.displacementShaderIn)
        cmds.setAttr(dispNode + '.aiDisplacementZeroValue', zeroScaleValue)

    def setupDisplacement(self, texNodeName: str, texFilePath: str, texType: str, csDefaults, zeroScaleValue: float = 0.0):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, debug=True)

        dispNode = DisplacementNode(texNodeName, scale=1.0)
        dispNode.connect(tex.redColorOut, self.shadGrp.displacementShaderIn)
        cmds.setAttr(dispNode.nodeName +
                     '.aiDisplacementZeroValue', zeroScaleValue)


class ShadingGroup(object):
    def __init__(self, nodeName, debug: bool = False) -> None:
        self.nodeName = nodeName
        self.aiSurfaceShaderInput = self.nodeName + '.aiSurfaceShader'
        self.surfaceShaderInput = self.nodeName + '.surfaceShader'
        self.displacementShaderIn = self.nodeName + '.displacementShader'

        # execute default methods
        self.createNode()

    def createNode(self):
        self.nodeName = cmds.sets(name=self.nodeName,
                                  renderable=True, noSurfaceShader=True, empty=True)


class PrevSphere(object):
    """
    This class handles creating the preview sphere geometry and setting it all up for displacement
    """

    def __init__(self, nodeName: str = 'Preview_Sphere_geo', smoothSteps: int = 2, dispSubdivs: int = 3, tesselation: bool = True, dispHeight: float = 1.0) -> None:
        self.nodeName = nodeName
        self.shapeNodeName = self.nodeName + 'Shape'
        self.smoothSteps = smoothSteps
        self.dispSubdivs = dispSubdivs
        self.tess = tesselation
        self.dispHeight = dispHeight
        self.dispPadding = 0.8 * dispHeight  # TODO get rid of hardcoded multiplier

        # defaults
        self.createNode()
        self.setupDisplacement()

    def createNode(self):
        cmds.polyCube(name=self.nodeName)
        cmds.polySmooth(self.nodeName, divisions=self.smoothSteps)

    def setupDisplacement(self):
        cmds.setAttr(self.shapeNodeName + '.aiSubdivType', 1)
        cmds.setAttr(self.shapeNodeName +
                     '.aiSubdivIterations', self.dispSubdivs)
        cmds.setAttr(self.shapeNodeName +
                     '.aiDispHeight', self.dispHeight)
        cmds.setAttr(self.shapeNodeName +
                     '.aiDispPadding', self.dispPadding)

        cmds.select(self.nodeName)
        cmds.delete(constructionHistory=True)

    def assignShader(self, shader: str):
        cmds.select(self.nodeName, replace=True)
        cmds.hyperShade(assign=shader)

    def moveOver(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        cmds.move(x, y, z, self.nodeName)
