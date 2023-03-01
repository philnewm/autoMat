from maya import cmds
from maya import mel
import os
import logging

logging.basicConfig()
logger = logging.getLogger('nodes')
# TODO change log level to info before merging to test
logger.setLevel(logging.DEBUG)


class ShaderNode(object):
    """
    _summary_

    Args:
        object (_type_): _description_
    """

    def __init__(self, input_name: str, input_shader_type: str, input_supported_channels: list, input_shader_channels: dict) -> None:
        self.socket_connect = '.'
        self.node_name = input_name
        self.shader_node_name = self.node_name + '_AutoMatShader'
        self.shader_type = input_shader_type

        self.supported_channels = input_supported_channels

        self._get_shader_channels(input_shader_channels)

    def _get_shader_channels(self, shader_channels: dict):
        for channel in self.supported_channels_list:
            self.supported_channels[channel] = self.shader_node_name + \
                self.socket_connect + shader_channels[channel][0]

        logger.debug(f'shader channels collected: {self.supported_channels}')

    def create_shader_node(self):
        cmds.shadingNode(self.shader_type,
                         name=self.shader_node_name, asShader=True)

        logger.info(f'shader node created {self.shader_node_name}')


class ShadingGroup(object):
    def __init__(self, input_name: str = 'prev_shader') -> None:
        self.socket_connect = '.'
        self.node_name = 'shading_grp_' + input_name
        # preview shader

        # TODO check if corrects
        self.supported_channels = {'vp_surface': 'surfaceShader',
                                   'ai_surface': 'aiSurfaceShader',
                                   'vr_surface': 'rsSurfaceShader',
                                   'rs_surface': 'rsSurfaceShader',
                                   'displacement': 'displacementShader',
                                   'rs_displacement': 'rsDisplacementShader'}

        for channel in self.supported_channels:
            self.supported_channels[channel] = self.node_name + \
                self.socket_connect + self.supported_channels[channel]

        # self.surface_shader = self.node_name + '.surfaceShader'
        # self.ai_surface_shader = self.node_name + '.aiSurfaceShader'
        # # TODO check if correct
        # self.rs_material_shader = self.node_name + '.rsmaterialShader'
        # # TODO check if correct
        # self.vr_material_shader = self.node_name + '.vrmaterialShader'

        # self.displacement_shader = self.node_name + '.displacementShader'
        # # TODO redshift displacement shader name
        # self.rs_displacement_shader = self.node_name + ''

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
    def __init__(self, input_node_name: str, input_image_node_type: str, channel_list: list) -> None:
        self.node_name = input_node_name
        self.socket_connect = '.'
        self.image_node_type = input_image_node_type
        self.texture_attr = ''

        self._create_image_node(self.image_node_type)

    def _create_image_node(self, image_node_type: str):
        cmds.shadingNode(image_node_type, name=self.node_name,
                         asTexture=True, isColorManaged=True)

    def load_texture(self, input_texture_attr, input_texture):
        self.texture_attr = input_texture_attr
        cmds.setAttr(self.node_name + self.socket_connect + input_texture_attr,
                     input_texture, type='string')

    def change_tiling_mode(self, input_tiling_attr, mode_id: int = 0):
        cmds.setAttr(self.node_name + self.socket_connect +
                     input_tiling_attr, mode_id)


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
    newImageNode.change_tiling_mode('uvTilingMode', mode_id=3)
