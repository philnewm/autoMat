import pprint
from importlib import reload

from autoMat_test.lib import nodes
from autoMat_test.lib import utils
reload(nodes)
reload(utils)


def vp_prev_setup():
    test_shader = nodes.VPPrevShaderNode()
    pprint.pprint(test_shader.supported_channels)
    test_shader.create_shader_node()

    test_shad_grp = nodes.ShadingGroup()
    pprint.pprint(test_shad_grp.supported_channels)
    connect_surface_shader = utils.NodeConnector()
    connect_surface_shader.connect_nodes(
        test_shader.supported_channels['output'], test_shad_grp.supported_channels['vp_surface'])


if __name__ == '__main__':
    # add testing code for this script file here
    vp_prev_setup()
