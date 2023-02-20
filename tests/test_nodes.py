from lib.nodes import vp_prev_shader_node


def test_shader_node_default() -> None:

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
                      'normCam': ['normalCamera', 'multi']}

    name = 'prev_shader'
    test_shader = vp_prev_shader_node(name, shader_channels=preview_shader)
    assert test_shader.node_name == 'prev_shader_AutoMatShader'
