from imp import reload
from maya import cmds
import maya.mel as mel
import nodes
import os
reload(nodes)


class autoMat(object):
    def __init__(self, dataPath: str = 'sourceimages/', renderEngine: str = 'arnold', triPlanar: bool = False) -> None:
        self.renderEngine = renderEngine
        self.projectDir = cmds.workspace(q=True, rootDirectory=True)
        self.dataPath = os.path.join(self.projectDir, dataPath)
        self.dataDict = {}
        self.triPlanar = triPlanar

        # remove from here
        # texNodeName = os.path.split(self.dataPath)[1].split('.')[0]

        self.texTypes = {'color': ('diff', 'albedo', 'color', 'rgb'),
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
        # default execution
        self.findFiles()
        self.setupMaterial()

    def setupMaterial(self):
        moveStep = 0
        triScale = 0.35
        triBlend = 1.0
        for key, value in self.dataDict.items():
            # setup shader
            shaderNodeName = os.path.split(key)[1]
            newShader = nodes.PBRShader(shaderNodeName, debug=True)
            newShader.createArnoldPBRShader()

            # shading group
            shadingGrp = nodes.ShadingGroup(
                shaderNodeName + '_ShaGrp', debug=True)
            newShader.connColOut(shadingGrp.aiSurfaceShaderInput)

            # preview mesh
            prevSphere = nodes.PrevSphere(
                newShader.nodeName + '_PreviewSphere_geo', 3, dispHeight=0.1)
            prevSphere.assignShader(newShader.nodeName)
            prevSphere.moveOver(-2 * moveStep, 0, 0)
            moveStep += 1

            for v in value:
                texNodeName = v.split('.')[0]
                texFilePath = os.path.join(key, v)
                texType = self.getType(texNodeName)
                if texType == 'color':
                    tex = nodes.FileNode(texNodeName, texFilePath,
                                         texType, debug=True)
                    if self.triPlanar:
                        triplanar = nodes.TriPlanarNode(
                            'tri_' + texNodeName, triBlend, triScale)
                        triplanar.connectColor(tex.colorOut, newShader.baseCol)
                    else:
                        # bamybe rename to color
                        newShader.connDiff(tex.colorOut)

                if texType == 'metalness':
                    tex = nodes.FileNode(texNodeName, texFilePath,
                                         texType, debug=True)
                    if self.triPlanar:
                        triplanar = nodes.TriPlanarNode(
                            'tri_' + texNodeName, triBlend, triScale)
                        triplanar.connectData(tex.colorOut, newShader.metal)
                    else:
                        newShader.connMetal(tex.redColorOut)

                if texType == 'roughness':
                    tex = nodes.FileNode(texNodeName, texFilePath,
                                         texType, debug=True)
                    if self.triPlanar:
                        triplanar = nodes.TriPlanarNode(
                            'tri_' + texNodeName, triBlend, triScale)
                        triplanar.connectData(tex.colorOut, newShader.rough)
                    else:
                        newShader.connRough(tex.redColorOut)

                if texType == 'normal':
                    tex = nodes.FileNode(texNodeName, texFilePath,
                                         texType, debug=True)
                    normalMap = nodes.NormalMapNode(
                        texNodeName + '_ainormalMap')
                    if self.triPlanar:
                        triplanar = nodes.TriPlanarNode(
                            'tri_' + texNodeName, triBlend, triScale)
                        triplanar.connectColor(tex.colorOut, normalMap.dataIn)
                        newShader.connNormal(normalMap.normalOut)
                    else:
                        normalMap.connect(tex.colorOut, newShader.normal)

                if texType == 'displacement':
                    tex = nodes.FileNode(
                        texNodeName, texFilePath, texType, debug=True)
                    dispShader = nodes.DisplacementNode(
                        texNodeName + '_dispShader', debug=True)
                    if self.triPlanar:
                        triplanar = nodes.TriPlanarNode(
                            'tri_' + texNodeName, triBlend, triScale)
                        triplanar.connectData(tex.colorOut, dispShader.dispIn)
                        dispShader.connectOut(shadingGrp.displacementShaderIn)
                    else:
                        dispShader.connect(
                            tex.redColorOut, shadingGrp.displacementShaderIn)

    def getType(self, name: str):
        # TODO check image for color or grayscale
        # TODO ask user for recognized pattern
        for keys, values in self.texTypes.items():
            for val in values:
                if val in name.lower():
                    # returns texture types
                    return keys

    def findFiles(self):
        try:
            os.path.exists(self.dataPath)
        except:
            raise ("choosen path does not exist")

        for path, directories, files in os.walk(self.dataPath):
            if files:
                texList = []
                for file in files:
                    # exclude .tx files from reading
                    if file.endswith('.tx'):
                        continue
                    texList.append(file)

                self.dataDict[path] = texList


mel.eval('MLdeleteUnused;')
newAutoMat = autoMat(triPlanar=True)

# unknownNodes = cmds.ls(type="unknown")
# for item in unknownNodes:
#     if cmds.objExists(item):
#         print(item)
#         cmds.delete(item)
