from __future__ import division
from maya import cmds


class matBuilder(object):

    def __init__(self, name: str = None) -> None:
        self.shader = None
        self.shaderName = name
        self.matSphere = None
        self.sphereShape = None
        self.shadingGroup = None
        self.shaderList = []
        self.diffTex = None
        self.metalTex = None
        self.roughTex = None
        self.normalTex = None
        self.heightTex = None
        self.textureName = None
        self.textureList = []
        self.matDict = {}  # Use dicitionary for material names based on folder names for keys and texture file paths as list for values

        # TODO get rid of hard coded paths
        self.pathDiff = "/mnt/Projects/tmp/autoMat_rnd/sourceimages/textures/medieval_windows_29_73/medieval_windows_29_73_diffuse.jpg"
        self.pathMetal = "/mnt/Projects/tmp/autoMat_rnd/sourceimages/textures/medieval_windows_29_73/medieval_windows_29_73_metalness.jpg"
        self.pathRough = "/mnt/Projects/tmp/autoMat_rnd/sourceimages/textures/medieval_windows_29_73/medieval_windows_29_73_roughness.jpg"
        self.pathNormal = "/mnt/Projects/tmp/autoMat_rnd/sourceimages/textures/medieval_windows_29_73/medieval_windows_29_73_normal.jpg"
        self.pathDisplace = "/mnt/Projects/tmp/autoMat_rnd/sourceimages/textures/medieval_windows_29_73/medieval_windows_29_73_height.jpg"
        # TODO add optional slots e.g. emissive, sss, opacity, transmission, coat, sheen

        self.files = [self.pathDiff, self.pathMetal,
                      self.pathRough, self.pathNormal, self.pathDisplace]

    def createSphere(self):
        self.matSphere, self.sphereShape = cmds.polyCube(name="PreviewSphere")
        cmds.polySmooth(self.matSphere, divisions=3)
        cmds.setAttr(self.sphereShape + '.aiSubdivType', 1)
        cmds.setAttr(self.sphereShape +
                     '.aiSubdivIterations', 3)  # TODO fix bug
        cmds.delete(self.matSphere, constructionHistory=True)

    def createShader(self):
        self.shader = cmds.shadingNode(
            'aiStandardSurface', name=self.shaderName, asShader=True)

        self.shaderList.append(self.shader)

    def assignShader(self):
        # TODO is dis clever
        self.shadingGroup = cmds.sets(name='PreviewSphereShadingGrp',
                                      renderable=True, noSurfaceShader=True, empty=True)
        cmds.connectAttr(self.shader + '.outColor',
                         self.shadingGroup + '.surfaceShader', force=True)

        cmds.select(self.matSphere, replace=True)
        cmds.hyperShade(assign=self.shader)

    def getFiles(self):  # non active snippet
        self.files = cmds.fileDialog2(
            cap='Choose Files to Create a Material from', fm=4)
        if self.files is None:
            self.destroy = 1

    def createFileNodes(self):
        self.diffName = "diffuse_tex"
        self.metalName = "metal_tex"
        self.roughName = "rough_tex"
        self.normalName = "normal_tex"
        self.dispName = "disp_tex"

        # create texture nodes
        self.diffTex = cmds.shadingNode(
            'aiImage', name=self.diffName, asTexture=True)  # aiImage Node only visible in lit vp
        self.metalTex = cmds.shadingNode(
            'aiImage', name=self.metalName, asTexture=True)  # aiImage Node only visible in lit vp
        self.roughTex = cmds.shadingNode(
            'aiImage', name=self.roughName, asTexture=True)  # aiImage Node only visible in lit vp
        self.normalTex = cmds.shadingNode(
            'aiImage', name=self.normalName, asTexture=True)  # aiImage Node only visible in lit vp0
        self.dispTex = cmds.shadingNode(
            'aiImage', name=self.dispName, asTexture=True)  # aiImage Node only visible in lit vp
        # TODO test aiImage with UDIM
        # TODO add option to use default file node

    def setupDiff(self):

        # connect image
        cmds.setAttr(self.diffTex + '.filename',
                     self.pathDiff, type='string')
        # set colrospace
        cmds.setAttr(self.diffTex + '.colorSpace',
                     'Input - Generic - sRGB - Texture', type='string')
        # connect nodes
        cmds.connectAttr(self.diffTex + '.outColor',
                         self.shader + '.baseColor', force=True)

    def setupMetal(self):
        # TODO setup switchable colorspace 'maya ACES', 'OCIO ACES', 'unmanaged'
        # connect image
        cmds.setAttr(self.metalTex + '.filename',
                     self.pathMetal, type='string')
        # set colorspace
        cmds.setAttr(self.metalTex + '.colorSpace',
                     'Utility - Raw', type='string')
        # connect to shader
        cmds.connectAttr(self.metalTex + '.outColorR',
                         self.shader + '.metalness', force=True)

    def setupRough(self):
        # connect image
        cmds.setAttr(self.roughTex + '.filename',
                     self.pathRough, type='string')
        # set colrospace
        cmds.setAttr(self.roughTex + '.colorSpace',
                     'Utility - Raw', type='string')

        cmds.connectAttr(self.roughTex + '.outColorR',
                         self.shader + '.specularRoughness', force=True)

    def setupNormal(self):
        self.aiNormal = cmds.shadingNode(
            'aiNormalMap', name='aiNormalMap', asUtility=True)

        cmds.setAttr(self.normalTex + '.filename',
                     self.pathNormal, type='string')

        cmds.setAttr(self.normalTex + '.colorSpace',
                     'Utility - Raw', type='string')

        cmds.connectAttr(self.normalTex + '.outColor',
                         self.aiNormal + '.input', force=True)

        cmds.connectAttr(self.aiNormal + '.outValue',
                         self.shader + '.normalCamera', force=True)

    def setupDisp(self):
        self.disp = cmds.shadingNode(
            'displacementShader', name='displacementShader', asShader=True)

        cmds.setAttr(self.dispTex + '.filename',
                     self.pathDisplace, type='string')

        cmds.setAttr(self.dispTex + '.colorSpace',
                     'Utility - Raw', type='string')
        cmds.connectAttr(self.dispTex + '.outColorR',
                         self.disp + '.displacement', force=True)

        cmds.connectAttr(self.disp + '.displacement',
                         self.shadingGroup + '.displacementShader', force=True)
        # TODO figure out how to connect displacement to shading group without object
        # TODO setup displacement without shading group


if __name__ == "__main__":
    newMat = matBuilder("ai_testMat")
    newMat.createShader()
    newMat.createSphere()
    newMat.assignShader()
    newMat.createFileNodes()
    newMat.setupDiff()
    newMat.setupMetal()
    newMat.setupRough()
    newMat.setupNormal()
    print(cmds.listAttr(newMat.sphereShape))
    newMat.setupDisp()
