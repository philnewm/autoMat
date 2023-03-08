from importlib import reload

from autoMat.lib import nodes
# from autoMat.lib import utils
reload(nodes)
# reload(utils)

file_node_channel_list = {'outColor': 'outColor',
                            'outRed': 'outColorR',
                            'outGreen': 'outColorG',
                            'outBlue': 'outColorB',
                            'outAlpha': 'outAlpha'
                            }

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
    
    # ========== setup mock-up ==========
    # prev_shader = nodes.PreviewShader(filepath, texture_list)
    # prev_shader.setup_pbr_nodes()
    # prev_shader.assign_shader()

if __name__ == '__main__':
    # add testing code for this script file here
    vp_prev_setup()
