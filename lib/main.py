from importlib import reload

from autoMat.lib import nodes
from autoMat.lib import utils
reload(nodes)
reload(utils)

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
                  'output': ['outColor', 'multi'],
                  }

displacement_settings = {'subdivtype': 'aiSubdivType',
                         'subdiviterations': 'aiSubdivIterations',
                         'dispheight': 'aiDispHeight',
                         'padding': 'aiDispPadding',
                         }

supported_channels_list = [
            'baseCol', 'metal', 'rough', 'opacity', 'normal', 'output']

def vp_prev_setup():
    prev_shader = nodes.ShaderNode('PrevShader', 'standardSurface', supported_channels_list, preview_shader)
    prev_shader.create_shader_node()

    test_shad_grp = nodes.ShadingGroup()
    connect_surface_shader = utils.NodeConnector()
    connect_surface_shader.connect_nodes(
        prev_shader.supported_channels['output'], test_shad_grp.supported_channels['vp_surface'])
    
    diff_texture = nodes.ImageNode('diff_texture', 'file', )     


if __name__ == '__main__':
    # add testing code for this script file here
    vp_prev_setup()
