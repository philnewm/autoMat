from maya import cmds
import os
from maya import mel

PROJECTDIR = cmds.workspace(q=True, rootDirectory=True)
texDir = PROJECTDIR + 'sourceimages/' + 'textures'

texTypes = {'diffuse': ('diff', 'albedo', 'color', 'rgb'),
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

diff_cs = "Input - Generic - sRGB - Texture"
util_cs = "Utility - Raw"
arnold_re = 'ai'


def find(directory: str = texDir):

    if not os.path.exists(directory):
        return

    matname = []

    for path, directories, files in os.walk(texDir):
        if files:
            # TODO engine change to dynamic
            createShaderNode(path, renderEngine=arnold_re)
            for file in files:
                if file.endswith('.tx'):
                    continue
                if checkname(file):
                    filePath = os.path.join(path, file)
                    createImageNode(file, filePath, checkname(
                        file), renderEngine='ai')


def createImageNode(file: str, path: str, type: str, renderEngine: str = 'ai'):
    if renderEngine == arnold_re:
        imageNode = 'aiImage'

    if renderEngine == 'vr':
        pass
    if renderEngine == 'rs':
        pass
    filename, _ = os.path.splitext(file)

    texNode = cmds.shadingNode(imageNode, name=filename, asTexture=True)

    if type == 'diffuse':
        # import image
        cmds.setAttr(texNode + '.filename', path, type='string')
        # set colorspace for ACES
        if type == 'diffuse':  # TODO double if
            cmds.setAttr(texNode + '.colorSpace', diff_cs, type='string')
        else:
            cmds.setAttr(texNode + '.colorSpace', util_cs, type='string')

    if type == 'metalness':
        cmds.shadingNode(imageNode, name=filename, asTexture=True)

    if type == 'roughness':
        cmds.shadingNode(imageNode, name=filename, asTexture=True)

    if type == 'normal':
        cmds.shadingNode(imageNode, name=filename, asTexture=True)

    if type == 'displacement':
        cmds.shadingNode(imageNode, name=filename, asTexture=True)

    return filename


def createShaderNode(path: str, renderEngine: str = 'ai'):
    if renderEngine == 'ai':
        pbrshader = 'aiStandardSurface'
    cmds.shadingNode(pbrshader, name=os.path.split(path)
                     [1], asShader=True)


def checkname(name: str):
    # TODO check image for color or grayscale
    # TODO ask user for recognized pattern
    for keys, values in texTypes.items():
        for val in values:
            if val in name.lower():
                return keys


mel.eval('MLdeleteUnused')

find()
