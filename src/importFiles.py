from maya import cmds
import os


class Import(object):

    def __init__(self, path: str = None) -> None:

        if path:
            self.texDir = path
        else:
            self.projectDir = cmds.workspace(q=True, rootDirectory=True)
            self.texDir = self.projectDir + 'sourceimages/' + 'textures'

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

        self.filePaths = {}

    def find(self):  # TODO better in __init__

        if not os.path.exists(self.texDir):
            return

        for path, directories, files in os.walk(self.texDir):
            if files:
                texList = []
                for file in files:
                    # exclude .tx files from reading
                    if file.endswith('.tx'):
                        continue
                    # TODO check gets doubled in imageNode
                    texType = self.getType(file)
                    print()
                    if texType:
                        texList.append(file)

                self.filePaths[path] = texList

        # returns dictionary of filpaths and files
        return self.filePaths

    def getType(self, name: str):
        # TODO check image for color or grayscale
        # TODO ask user for recognized pattern
        for keys, values in self.texTypes.items():
            for val in values:
                if val in name.lower():

                    # returns texture types
                    return keys

# test code
# someImport = Import()
# for key, value in someImport.find().items():
#     print(key)
#     for v in value:
#         print(v)
