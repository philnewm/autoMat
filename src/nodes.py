# This code contains a bunch of wrapper classes + Methods
# which can be used in a flexible way to automate more complex process
# regarding the loading fo texture files and settings them up for a
# PBR-workflow


from maya import cmds
from maya import mel
import os
import re
import logging

logging.basicConfig()
logger = logging.getLogger('AutoMat')
logger.setLevel(logging.INFO)


class FileNode(object):
    """
    Create a filenode to use for texture import.
    """

    def __init__(self, nodeName: str, imagePath: str, texType: str, csDefaults: tuple = (
            "Input - Generic - sRGB - Texture", "Utility - Raw"), renderEngine: str = 'arnold', enableAutoTX: bool = True) -> None:
        """
        All default variables for file node creation get assigned.

        Args:
            nodeName (str): Name for created file node 
            imagePath (str): Filepath for image to load into file node
            texType (str): Typ of texture (color, metal, roughness, ...)
            csDefaults (tuple, optional): Default colorspace names for color and data images. Defaults to ( "Input - Generic - sRGB - Texture", "Utility - Raw").
            renderEngine (str, optional): Render engine in use. Defaults to 'arnold'.
            enableAutoTX (bool, optional): Switch creation of tx files for arnold on/off. Defaults to True.
        """

        self.nodeName = nodeName
        self.filePath = imagePath
        self.col_cs, self.util_cs = csDefaults
        self.colorSpace = None
        self.renderEngine = renderEngine
        self.texType = texType
        self.name = None
        self.enableAutoTX = enableAutoTX
        self.ignoreMissingTex = True

        self.colorOut = self.nodeName + '.outColor'
        self.redColorOut = self.nodeName + '.outColor.outColorR'

        if texType:
            self.createNode()
            self.loadImage()
            self.setColorSpace()

    def createNode(self):
        """
        Create a filenode based on the selected renderengine.

        Returns:
            _type_: _description_
        """
        # check which file node to create
        if self.renderEngine == 'arnold':
            self.imageNode = 'aiImage'
            # create file node
            self.name = cmds.shadingNode(
                self.imageNode, name=self.nodeName, asTexture=True, isColorManaged=True)

        else:
            self.imageNode = 'file'  # TODO check for correct naming

        logger.debug(f"file node: {self.imageNode}")
        return self.nodeName

    def loadImage(self):
        # import image
        # if self.udim:
        #     # TODO check if only 1001 udim available (fake udim)
        #     udim_sequence = self.udim.group(0)
        #     udim_sequence = self.filePath.replace(udim_sequence, '<udim>')

        #     cmds.setAttr(self.nodeName + '.filename',
        #                  udim_sequence, type='string')
        #     logger.info(
        #         f"image imported: {udim_sequence}, auto tx: {self.enableAutoTX}")
        #     return

        cmds.setAttr(self.nodeName + '.filename',
                     self.filePath, type='string')
        cmds.setAttr(self.nodeName + '.autoTx', self.enableAutoTX)
        cmds.setAttr(self.nodeName + '.ignoreMissingTextures',
                     self.ignoreMissingTex)

        logger.info(
            f"image imported: {self.filePath}, auto tx: {self.enableAutoTX}")

    def setColorSpace(self):  # TODO add custom input method
        # check if .exr files or not and use all as utility raw or not
        if self.texType == 'color' and os.path.splitext(os.path.split(self.filePath)[1])[1][1:] != "exr":
            cmds.setAttr(self.nodeName + '.colorSpace',
                         self.col_cs, type='string')
            self.colorSpace = self.col_cs
        else:
            cmds.setAttr(self.nodeName + '.colorSpace',
                         self.util_cs, type='string')
            self.colorSpace = self.util_cs

        cmds.setAttr(self.nodeName + '.ignoreColorSpaceFileRules', 1)
        logger.debug(f"Texture Color conversion: {self.colorSpace}")


class TriPlanarNode(object):
    def __init__(self, nodeName: str = 'aiTriplanar', blend: float = 0.5, scale: float = 1.0, renderEngine: str = 'arnold') -> None:
        self.blendValue = blend
        self.renderEngine = renderEngine
        self.nodeName = nodeName + '_trip'
        self.triPlanar = None
        self.dataIn = self.nodeName + '.input'
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

        logger.debug(f"Triplanar node: {self.triPlanar}")

        return self.nodeName

    def setBlend(self, blend: float):
        self.blendValue = blend
        cmds.setAttr(self.blend, self.blendValue)

        logger.debug(f"changed blend value to: {self.blendValue}")

    def setScale(self):
        cmds.setAttr(self.nodeName + '.scaleX', self.scale)
        cmds.setAttr(self.nodeName + '.scaleY', self.scale)
        cmds.setAttr(self.nodeName + '.scaleZ', self.scale)

    def connectColor(self, input, output):
        cmds.connectAttr(input,
                         self.dataIn, force=True)
        cmds.connectAttr(self.outColor, output, force=True)

        logger.info(f"connected {input} as input and {output} as output")

    def connectData(self, input, output):  # very spaghetti
        cmds.connectAttr(input,
                         self.dataIn, force=True)
        cmds.connectAttr(self.outColorRed, output, force=True)

        logger.info(f"connected {input} as input and {output} as output")

    def connectIn(self, input):
        cmds.connectAttr(input, self.dataIn, force=True)

        logger.info(f"connected {input} as input to {self.dataIn}")

    def connectOut(self, output):
        cmds.connectAttr(self.outColor, output, force=True)

        logger.info(f"connected {self.outColor} as input to {output}")


class NormalMapNode(object):
    def __init__(self, nodeName: str = 'aiNormalMap', normalStrength: float = 1.0, renderEngine: str = 'arnold') -> None:
        self.nodeName = nodeName + '_aiNormalMap'
        self.strength = normalStrength
        self.normalNode = None
        self.renderEngine = renderEngine
        self.normalOut = self.nodeName + '.outValue'
        self.dataIn = self.nodeName + '.input'

        self.createNode()

    def createNode(self):
        if self.renderEngine == 'arnold':
            self.normalNode = cmds.shadingNode(
                'aiNormalMap', name=self.nodeName, asUtility=True)
        else:
            pass

        logger.debug(f"NormalMap Node created: {self.normalNode}")

    def setStrength(self):
        cmds.setAttr(self.nodeName + '.strength', self.strength)
        logger.debug(f"set {input} strength to {self.strength}")

    def connect(self, input, output):
        cmds.connectAttr(input, self.dataIn, force=True)
        cmds.connectAttr(self.normalOut, output, force=True)
        logger.info(f"connected {input} as input and {output} as output")

    def connectIn(self, input):
        cmds.connectAttr(input, self.dataIn, force=True)

        logger.info(f"connected {input} as input to {self.dataIn}")

    def connectOut(self, output):
        cmds.connectAttr(self.normalOut, output, force=True)

        logger.info(f"connected {self.normalOut} as input to {output}")


class DisplacementNode(object):
    def __init__(self, nodeName: str = 'dispalacementShader', scale: int = 1) -> None:
        self.nodeName = nodeName + '_dispShader'
        self.scale = scale
        self.dispNode = None
        self.dispIn = self.nodeName + '.displacement'
        self.dispOut = self.nodeName + '.displacement'

        # execute default methods
        self.createNode()

    def createNode(self):
        # TODO check if different nodes for other render engines
        self.dispNode = cmds.shadingNode(
            'displacementShader', name=self.nodeName, asShader=True)
        logger.debug(f"Node created: {self.dispNode}")

    def setScale(self):
        cmds.setAttr(self.dispNode + '.scale', self.scale)
        logger.debug(f"Set {self.nodeName} scale to {self.scale}")

    def connect(self, input: str, output: str):
        cmds.connectAttr(input,
                         self.dispIn, force=True)
        cmds.connectAttr(self.dispOut, output, force=True)
        logger.info(f"connected: {input} as input and {output} as output")

    def connectIn(self, input: str):
        cmds.connectAttr(input,
                         self.dispIn, force=True)
        logger.info(f"connected: {input} as input to {self.dispIn}")

    def connectOut(self, output: str):
        cmds.connectAttr(self.dispOut, output,
                         force=True)
        logger.info(f"connected: {self.dispOut} as input to {output}")


class arnoldPBRShader(object):
    def __init__(self, nodeName: str = 'PBRShader') -> None:
        self.nodeName = nodeName
        self.geoName = nodeName + '_previewSphere_geo'
        self.shadNodeName = nodeName + '_AutoMatShader'
        self.shadingGrpName = nodeName + '_shaGrp'
        self.shadGrp = None
        self.colorOut = self.shadNodeName + '.outColor'
        self.baseCol = self.shadNodeName + '.baseColor'
        self.metal = self.shadNodeName + '.metalness'
        self.rough = self.shadNodeName + '.specularRoughness'
        self.transmiss = self.shadNodeName + '.transmission'
        self.sss = self.shadNodeName + '.subsurface'
        self.emission = self.shadNodeName + '.emissionColor'
        self.opacity = self.shadNodeName + '.opacity'
        self.normal = self.shadNodeName + '.normalCamera'
        self.udimFlag = False

        cmds.shadingNode('aiStandardSurface',
                         name=self.shadNodeName, asShader=True)

    # Methods to connect textures to shader channels
    def connColor(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.baseCol, force=True)

        logger.info(
            f"connected: {inputConnection} as input to {self.baseCol}")

    def connMetal(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.metal, force=True)

        logger.info(f"connected: {inputConnection} as input to {self.metal}")

    def connRough(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.rough, force=True)

    def connTransmiss(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.transmiss, force=True)

        logger.info(
            f"connected: {inputConnection} as input to {self.transmiss}")

    def connSSS(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.sss, force=True)

        logger.info(
            f"connected: {inputConnection} as input to {self.sss}")

    def connEmission(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.emission, force=True)

        logger.info(
            f"connected: {inputConnection} as input to {self.emission}")

    def connOpacity(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.opacity, force=True)

        logger.info(
            f"connected: {inputConnection} as input to {self.opacity}")

    def connNormal(self, inputConnection):
        cmds.connectAttr(inputConnection,
                         self.normal, force=True)

        logger.info(f"connected: {inputConnection} as input to {self.baseCol}")

    def connColOut(self, output):
        cmds.connectAttr(self.colorOut, output, force=True)

        logger.info(f"connected: {self.colorOut} as input to {output}")

    def assigntoSphere(self, translateX: float = 0.0, translateY: float = 0.0, translateZ: float = 0.0, dispInVP=True, orgSphere: list = [], grpName: str = 'Preview_Spheres_grp', dispSubdivs: int = 3, dispHeight: float = 0.05):

        # create shading group
        self.shadGrp = ShadingGroup(
            self.shadingGrpName)
        self.shadingGrpName = self.shadGrp.nodeName
        self.grpName = grpName

        # connect shading group
        self.connColOut(self.shadGrp.aiSurfaceShaderInput)
        if dispInVP:
            self.connColOut(self.shadGrp.surfaceShaderInput)
        # create preview sphere
        self.prevSphere = PrevSphere(
            self.geoName, dispSubdivs, dispHeight=dispHeight)

        # check if already one created
        if orgSphere:
            logger.debug(f"OBJECT TO DUPLICATE: {orgSphere}")
            self.prevSphere.duplicate(orgSphere)
        else:
            self.prevSphere.createNodeWithUdims()
            self.prevSphere.setupDisplacement()
            # group all preview spheres together
            cmds.parent(self.geoName, self.grpName)

        self.prevSphere.moveOver(translateX, translateY, translateZ)

        # assign Shader
        self.prevSphere.assignShader(self.shadNodeName)

    def setupTripColor(self, texNodeName: str, texFilePath: str, texType: str, csDefaults, triBlend: float = 0.5, triScale: float = 1.0):
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
                       texType, csDefaults)
        triplanar = TriPlanarNode(
            texNodeName, triBlend, triScale)
        triplanar.connectColor(tex.colorOut, self.baseCol)

        logger.info(f"connected: {tex.colorOut} as input to {self.baseCol}")

    def setupColor(self, texNodeName: str, texFilePath: str, texType: str, csDefaults):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults)
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
                       texType, csDefaults)
        triplanar = TriPlanarNode(
            texNodeName, triBlend, triScale)
        triplanar.connectData(tex.colorOut, self.metal)

    def setupMetalness(self, texNodeName: str, texFilePath: str, texType: str, csDefaults):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, )
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
                       texType, csDefaults, )
        triplanar = TriPlanarNode(
            texNodeName, triBlend, triScale)
        triplanar.connectData(tex.colorOut, self.rough)

    def setupRoughness(self, texNodeName: str, texFilePath: str, texType: str, csDefaults):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, )
        self.connRough(tex.redColorOut)

    def setupTripTransmiss(self, texNodeName: str, texFilePath: str, texType: str, csDefaults, triBlend: float = 0.5, triScale: float = 1.0):
        """
        Sets up nodes to triplanar project the transmission texture

        Args:
            texNodeName (str): Texture nodes name
            texFilePath (str): Texture nodes file path
            texType (str): Texture nodes type
            csDefaults (_type_): Colorspace default value
            triBlend (float, optional): Triplanar blending value. Defaults to 0.5.
            triScale (float, optional): Triplanar scaling value. Defaults to 1.
        """
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, )
        triplanar = TriPlanarNode(
            texNodeName, triBlend, triScale)
        triplanar.connectData(tex.colorOut, self.transmiss)

    def setupTransmiss(self, texNodeName: str, texFilePath: str, texType: str, csDefaults):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, )
        self.connTransmiss(tex.redColorOut)

    def setupTripSSS(self, texNodeName: str, texFilePath: str, texType: str, csDefaults, triBlend: float = 0.5, triScale: float = 1.0):
        """
        Sets up nodes to triplanar project the sss texture

        Args:
            texNodeName (str): Texture nodes name
            texFilePath (str): Texture nodes file path
            texType (str): Texture nodes type
            csDefaults (_type_): Colorspace default value
            triBlend (float, optional): Triplanar blending value. Defaults to 0.5.
            triScale (float, optional): Triplanar scaling value. Defaults to 1.
        """
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, )
        triplanar = TriPlanarNode(
            texNodeName, triBlend, triScale)
        triplanar.connectData(tex.colorOut, self.sss)

    def setupSSS(self, texNodeName: str, texFilePath: str, texType: str, csDefaults):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, )
        self.connSSS(tex.redColorOut)

    def setupTripEmission(self, texNodeName: str, texFilePath: str, texType: str, csDefaults, triBlend: float = 0.5, triScale: float = 1.0):
        """
        Sets up nodes to triplanar project the emission texture

        Args:
            texNodeName (str): Texture nodes name
            texFilePath (str): Texture nodes file path
            texType (str): Texture nodes type
            csDefaults (_type_): Colorspace default value
            triBlend (float, optional): Triplanar blending value. Defaults to 0.5
            triScale (float, optional): Triplanar scaling value. Defaults to 1.
        """
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, )
        triplanar = TriPlanarNode(
            texNodeName, triBlend, triScale)
        triplanar.connectColor(tex.colorOut, self.emission)

    # TODO needs separation between emission and emission color

    def setupEmission(self, texNodeName: str, texFilePath: str, texType: str, csDefaults):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, )
        self.connEmission(tex.colorOut)

    def setupTripOpacity(self, texNodeName: str, texFilePath: str, texType: str, csDefaults, triBlend: float = 0.5, triScale: float = 1.0):
        """
        Sets up nodes to triplanar project the emission texture

        Args:
            texNodeName (str): Texture nodes name
            texFilePath (str): Texture nodes file path
            texType (str): Texture nodes type
            csDefaults (_type_): Colorspace default value
            triBlend (float, optional): Triplanar blending value. Defaults to 0.5.
            triScale (float, optional): Triplanar scaling value. Defaults to 1.
        """
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, )
        triplanar = TriPlanarNode(
            texNodeName, triBlend, triScale)
        triplanar.connectColor(tex.ColorOut, self.opacity)

    # TODO needs separation between emission and emission color

    def setupOpacity(self, texNodeName: str, texFilePath: str, texType: str, csDefaults):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, )
        self.connOpacity(tex.colorOut)

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
                       texType, csDefaults, )
        triplanar = TriPlanarNode(
            texNodeName, triBlend, triScale)
        normalMap = NormalMapNode(texNodeName)
        triplanar.connectColor(tex.colorOut, normalMap.dataIn)
        self.connNormal(normalMap.normalOut)

    def setupNormal(self, texNodeName: str, texFilePath: str, texType: str, csDefaults):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, )
        normalMap = NormalMapNode(texNodeName)
        normalMap.connect(tex.colorOut, self.normal)

    def setupTripDisplacement(self, texNodeName: str, texFilePath: str, texType: str, csDefaults, triBlend: float = 0.5, triScale: float = 1.0, zeroScaleValue: float = 0.0, dispScale: float = 1.0):
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
                       texType, csDefaults, )
        dispNode = DisplacementNode(texNodeName, scale=dispScale)
        triplanar = TriPlanarNode(texNodeName, triBlend, triScale)
        triplanar.connectData(tex.colorOut, dispNode.dispIn)
        cmds.connectAttr(dispNode.dispOut, self.shadGrp.displacementShaderIn)
        cmds.setAttr(dispNode.nodeName +
                     '.aiDisplacementZeroValue', zeroScaleValue)

    def setupDisplacement(self, texNodeName: str, texFilePath: str, texType: str, csDefaults, zeroScaleValue: float = 0.0, dispScale: float = 1.0):
        tex = FileNode(texNodeName, texFilePath,
                       texType, csDefaults, )

        dispNode = DisplacementNode(texNodeName, scale=dispScale)
        dispNode.connect(tex.redColorOut, self.shadGrp.displacementShaderIn)
        cmds.setAttr(dispNode.nodeName +
                     '.aiDisplacementZeroValue', zeroScaleValue)


class ShadingGroup(object):
    def __init__(self, nodeName) -> None:
        self.nodeName = nodeName
        self.aiSurfaceShaderInput = self.nodeName + '.aiSurfaceShader'
        self.surfaceShaderInput = self.nodeName + '.surfaceShader'
        self.displacementShaderIn = self.nodeName + '.displacementShader'

        # execute default methods
        self.createNode()

    def createNode(self):
        self.nodeName = cmds.sets(name=self.nodeName,
                                  renderable=True, noSurfaceShader=True, empty=True)

        logger.debug(f"Created {self.nodeName}")


class PrevSphere(object):
    """
    This class handles creating the preview sphere geometry and setting it all up for displacement
    """

    def __init__(self, nodeName: str = 'Preview_Sphere_geo', smoothSteps: int = 2, dispSubdivs: int = 3, tesselation: bool = True, dispHeight: float = 1.0) -> None:
        self.nodeName = nodeName
        self.sphere = 'preview_geo'
        self.shapeNodeName = self.nodeName + 'Shape'
        self.smoothSteps = smoothSteps
        self.dispSubdivs = dispSubdivs
        self.tess = tesselation
        self.dispHeight = dispHeight
        self.dispPadding = 0.8 * dispHeight  # TODO get rid of hardcoded multiplier

    def createNodeWithUdims(self):
        cmds.polyCube(name=self.nodeName)
        cmds.polyMapCut(self.nodeName + '.e[:]', constructionHistory=True)
        mel.eval('u3dLayout -res 4096 -rot 1 -scl 1 -rmn 0 -rmx 360 -rst 90 -spc 0.0078125 -mar 0.0078125 -u 6 -box 0 1 0 1 ' +
                 self.nodeName + '.f[0:6];')
        cmds.polySmooth(self.nodeName, divisions=self.smoothSteps)
        # don't show while animation is palying
        cmds.setAttr(self.nodeName + '.hideOnPlayback', 1)
        # enable drawing overrides otherwise next line is not goona do anything
        cmds.setAttr(self.nodeName + '.overrideEnabled', 1)
        # set non selectable so user can't copy and delete by accident
        cmds.setAttr(self.nodeName + '.overrideDisplayType', 2)

        logger.debug(f"Created {self.nodeName} with UDIMs")

    def duplicate(self, prevName):
        cmds.duplicate(prevName)
        cmds.rename(prevName + '1', self.nodeName)

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
