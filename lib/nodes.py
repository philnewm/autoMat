from maya import cmds
from maya import mel
import os
import logging

logging.basicConfig()
logger = logging.getLogger('nodes')
# TODO change log level to info before merging to test
logger.setLevel(logging.DEBUG)

preview_shader = {'baseCol': ['baseColor', 'multi'],
                  'metal': ['metalness', 'single'],
                  'spec': ['specular', 'single'],
                  'specCol': ['specularColor', 'multi'],
                  'rough': ['specularRoughness', 'single'],
                  'transmis': ['transmission', 'single'],
                  'transmisCol': ['transmissionColor', 'multi'],
                  'transmisDepth': ['transmissionDepth', 'single'],
                  'transmisScat': ['transmissionScatter', 'multi'],
                  'sss': ['subsurface', 'single'],
                  'sssCol': ['subsurfaceColor', 'multi'],
                  'sssRad': ['subsurfaceRadius', 'multi'],
                  'coat': ['coat', 'single'],
                  'coatCol': ['coatColor', 'multi'],
                  'coatRough': ['coatRoughness', 'single'],
                  'sheen': ['sheen', 'single'],
                  'sheenCol': ['SheenColor', 'multi'],
                  'sheenRough': ['sheenRoughness', 'single'],
                  'emis': ['emission', 'single'],
                  'emisCol': ['emissionColor', 'multi'],
                  'opacity': ['opacity', 'multi'],
                  'normal': ['normalCamera', 'multi'],
                  'output': ['outColor', 'multi']}


class VPPrevShaderNode(object):
    """
    _summary_

    Args:
        object (_type_): _description_
    """

    def __init__(self, input_name: str = 'prev_shader', input_shader_type: str = 'standardSurface', shader_channels: dict = preview_shader) -> None:
        self.socket_connect = '.'

        self.node_name = input_name
        # TODO create new class for geo creation
        self.geo_name = self.node_name + '_previewSphere_geo'

        self.shader_node_name = self.node_name + '_AutoMatShader'
        self.shader_type = input_shader_type

        self.supported_channels = {'baseCol': '',
                                   'metal': '',
                                   'rough': '',
                                   'opacity': '',
                                   'normal': '',
                                   'output': ''}

        self.get_shader_channels(shader_channels)

    def get_shader_channels(self, shader_channels: dict):
        # for each supported shader channel
        for channel in self.supported_channels:
            # loop through all available shader channels
            for shader_channel in shader_channels.keys():
                # when matching pair is found add name as value
                if channel == shader_channel:
                    self.supported_channels[channel] = self.shader_node_name + \
                        self.socket_connect + \
                        shader_channels[shader_channel][0]

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
    def __init__(self, node_name) -> None:
        self.node_name = node_name

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


if __name__ == '__main__':
    # add testing code for this script file here
    newSphere = PrevSphere('prev_sphere')
    newSphere.create_prev_sphere_with_udims(3)
