from maya import cmds
import os


class TextureImport(object):

    # TODO find more logical way for path paramter
    def __init__(self, path: str = None) -> None:

        if path:
            self.texDir = path
        else:
            self.projectDir = cmds.workspace(q=True, rootDirectory=True)
            self.texDir = self.projectDir + 'sourceimages/' + 'textures'

        self.filePaths = {}

    def find(self):  # TODO maybe better in __init__

        if not os.path.exists(self.texDir):
            raise ("choosen path does not exist")

        for path, directories, files in os.walk(self.texDir):
            if files:
                texList = []
                for file in files:
                    # exclude .tx files from reading
                    if file.endswith('.tx'):
                        continue
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
if __name__ == '__main__':
    someImport = TextureImport()
    for key, value in someImport.find().items():
        print(key)
        for v in value:
            print(v)
