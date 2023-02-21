import pprint
from importlib import reload

from autoMat.lib import nodes
from autoMat.lib import utils
reload(nodes)
reload(utils)


def vp_prev_setup():
    test_shader = nodes.VPPrevShaderNode()
    test_shader.create_shader_node()

    test_shad_grp = nodes.ShadingGroup()
    connect_surface_shader = utils.NodeConnector()
    connect_surface_shader.connect_nodes(
        test_shader.supported_channels['output'], test_shad_grp.supported_channels['vp_surface'])


if __name__ == '__main__':
    # add testing code for this script file here
    vp_prev_setup()
