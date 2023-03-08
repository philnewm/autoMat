from maya import cmds
from maya import mel
import os
import logging
from autoMat.lib import utils


logging.basicConfig()
logger = logging.getLogger('nodes')
# TODO change log level to info before merging to test
logger.setLevel(logging.DEBUG)


class ShaderNode(object):
    """
    General shader node setup

    Args:
        object (_type_): _description_
    """

    def __init__(self, input_file_path: str, input_tex_file_list: list) -> None:
        self.socket_connect = '.'
        self.name = os.path.split(input_file_path)[1]
        self.shader_name = self.name + '_AutoMatShader'
        self.shader_type = None
        self.tex_file_list = []

        # shader channels
        self.diff = None
        self.metal = None
        self.roughness = None
        self.opacity = None
        self.normal = None
        self.output = None

        self.diff_tex = None
        self.metal_tex = None
        self.roughness_tex = None
        self.opacity_tex = None
        self.normal_tex = None
        self.displacement_tex = None

        self.shading_group = None

    def create_shader_node(self):
        cmds.shadingNode(self.shader_type,
                         name=self.shader_node_name, asShader=True)

        logger.info(f'shader node created {self.shader_node_name}')

    def setup_textures(self):
        for texture in self.file_list:
            self.texture_list.append(ImageNode(texture))

    def setup_diff_tex(self, file_path):
        self.diff_tex = ImageNode(file_path)
        utils.connect_color_channel(self.diff_tex.col_out, self.diff)

    def assign_to_geo(self):
        self.shading_group = ShadingGroup(self.shading_group_name)


class ShadingGroup(object):
    def __init__(self, input_name: str = 'prev_shader', channels: str = utils.shading_group_dict) -> None:
        self.socket_connect = '.'
        self.node_name = input_name + '_ShadGrp'

        self.surface_shader = self.node_name + \
            channels[utils.shading_group.vp_preview]
        self.ai_surface_shader = self.node_name + \
            channels[utils.shading_group.arnold]
        self.vr_material_shader = self.node_name + \
            channels[utils.shading_group.vray]
        self.rs_material_shader = self.node_name + \
            channels[utils.shading_group.redshift]
        self.displacement_shader = self.node_name + \
            channels[utils.shading_group.displacement]
        self.rs_displacement_shader = self.node_name + \
            channels[utils.shading_group.redshift_displacement]

        # execute default methods
        self.create_shading_grp_node()

    def create_shading_grp_node(self):
        cmds.sets(name=self.node_name,
                  renderable=True, noSurfaceShader=True, empty=True)

        logger.info(f"Created shading group {self.node_name}")

    def assignShader(self, shader: str):
        cmds.select(self.nodeName, replace=True)
        cmds.hyperShade(assign=shader)


class PrevSphere(object):
    def __init__(self, node_name, disp_channel_list) -> None:
        self.node_name = node_name + '_previewSphere_geo'
        self.shape_node = self.node_name + 'Shape'

    def create_prev_sphere_with_udims(self, smooth_steps):
        self.smooth_steps = smooth_steps
        cmds.polyCube(name=self.node_name)
        cmds.polyMapCut(self.node_name + '.e[:]', constructionHistory=True)
        mel.eval('u3dLayout -res 4096 -rot 1 -scl 1 -rmn 0 -rmx 360 -rst 90 -spc 0.0078125 -mar 0.0078125 -u 6 -box 0 1 0 1 ' +
                 self.node_name + '.f[0:6];')
        cmds.polySmooth(self.node_name, divisions=self.smooth_steps)
        # don't show while animation is palying
        cmds.setAttr(self.node_name + '.hideOnPlayback', 1)
        # enable drawing overrides otherwise next line is not goona do anything
        cmds.setAttr(self.node_name + '.overrideEnabled', 1)
        # set non selectable so user can't copy and delete by accident
        cmds.setAttr(self.node_name + '.overrideDisplayType', 2)

        logger.debug(f"Created {self.node_name} with UDIMs")

    def duplicate(self, prevName):
        counter = 1  # init counter
        # rename if exists
        # TODO handle with naming class instead
        while cmds.objExists(prevName + str(counter)):
            counter += 1
        cmds.duplicate(prevName, name=prevName + str(counter))

    def get_displacement_settings(self):
        # TODO check implementation for arnold
        cmds.setAttr(self.shape_node + '.aiSubdivType', 1)
        cmds.setAttr(self.shape_node +
                     '.aiSubdivIterations', self.dispSubdivs)
        cmds.setAttr(self.shape_node +
                     '.aiDispHeight', self.dispHeight)
        cmds.setAttr(self.shape_node +
                     '.aiDispPadding', self.dispPadding)


class ImageNode(object):
    def __init__(self, input_node_name: str, input_tex_type: str = 'file') -> None:
        self.node_name = input_node_name
        self.tex_type = input_tex_type
        self.socket_connect = '.'
        self.colorSpace = ''

        self.col_out = self.node_name + self.socket_connect + 'outColor'

    def create_image_node(self):
        cmds.shadingNode('file', name=self.node_name,
                         asTexture=True, isColorManaged=True)

    def create_aiImage_node(self):
        cmds.shadingNode('aiImage', name=self.node_name,
                         asTexture=True, isColorManaged=True)

    def load_texture(self, input_texture_attr, input_texture):
        self.texture_attr = input_texture_attr
        cmds.setAttr(self.node_name + self.socket_connect + input_texture_attr,
                     input_texture, type='string')

    def change_tiling_mode(self, input_tiling_attr, mode_id: int = 0):
        cmds.setAttr(self.node_name + self.socket_connect +
                     input_tiling_attr, mode_id)

    def set_color_space(self, color_space_attr, input_color_space):
        self.color_space = input_color_space

        cmds.setAttr(self.node_name + self.socket_connect +
                     color_space_attr, self.color_space, type='string')

        cmds.setAttr(self.node_name + '.ignoreColorSpaceFileRules', 1)

        logger.debug(f"Texture Color conversion: {self.colorSpace}")


if __name__ == '__main__':
    # add testing code for this script file here
    # newSphere = PrevSphere('prev_sphere')
    # newSphere.create_prev_sphere_with_udims(3)

    file_node_channel_list = {'outColor': 'outColor',
                              'outRed': 'outColorR',
                              'outGreen': 'outColorG',
                              'outBlue': 'outColorB',
                              'outAlpha': 'outAlpha'
                              }

    newImageNode = ImageNode(
        'TestImage', 'file', channel_list=file_node_channel_list)
    newImageNode.load_texture(
        'fileTextureName', 'sourceimages/textures/mud_with_large_stones_38_65_4K/mud_with_large_stones_38_65_diffuse.jpg')
    newImageNode.change_tiling_mode('uvTilingMode', mode_id=0)
    newImageNode.set_color_space(
        'colorSpace', 'Input - Generic - sRGB - Texture')
