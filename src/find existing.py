import os
from maya import cmds

dataDict = {'/mnt/Projects/tmp/autoMat_rnd/sourceimages/julian_endterm300_textures/plants/basket_grass/Textures/Atlas': ['slfm2rp_2K_Albedo.exr', 'slfm2rp_2K_Opacity.exr', 'slfm2rp_2K_Normal.exr', 'slfm2rp_2K_Translucency.exr', 'slfm2rp_2K_Displacement.exr', 'slfm2rp_2K_AO.exr', 'slfm2rp_2K_Roughness.exr'], '/mnt/Projects/tmp/autoMat_rnd/sourceimages/julian_endterm300_textures/plants/basket_grass/Textures/Billboard': ['Billboard_2K_Displacement.exr', 'Billboard_2K_Opacity.exr', 'Billboard_2K_AO.exr', 'Billboard_2K_Roughness.exr', 'Billboard_2K_Normal.exr', 'Billboard_2K_Translucency.exr', 'Billboard_2K_Albedo.exr'], '/mnt/Projects/tmp/autoMat_rnd/sourceimages/julian_endterm300_textures/plants/sea_champion/Textures/Atlas': ['vkblbbpia_2K_Albedo.exr', 'vkblbbpia_2K_Normal.exr', 'vkblbbpia_2K_AO.exr', 'vkblbbpia_2K_Displacement.exr', 'vkblbbpia_2K_Roughness.exr', 'vkblbbpia_2K_Translucency.exr', 'vkblbbpia_2K_Opacity.exr'], '/mnt/Projects/tmp/autoMat_rnd/sourceimages/julian_endterm300_textures/plants/sea_champion/Textures/Billboard': ['Billboard_2K_Displacement.exr', 'Billboard_2K_Opacity.exr', 'Billboard_2K_AO.exr', 'Billboard_2K_Roughness.exr', 'Billboard_2K_Normal.exr', 'Billboard_2K_Translucency.exr', 'Billboard_2K_Albedo.exr'],
            '/mnt/Projects/tmp/autoMat_rnd/sourceimages/julian_endterm300_textures/plants/thatching_grass/Textures/Atlas': ['uc0oceo_2K_Roughness.tif', 'uc0oceo_2K_Opacity.tif', 'uc0oceo_2K_Normal.tif', 'uc0oceo_2K_Displacement.tif', 'uc0oceo_2K_Albedo.tif', 'uc0oceo_2K_AO.tif', 'uc0oceo_2K_Translucency.tif'], '/mnt/Projects/tmp/autoMat_rnd/sourceimages/julian_endterm300_textures/plants/thatching_grass/Textures/Billboard': ['Billboard_2K_Displacement.tif', 'Billboard_2K_Normal.tif', 'Billboard_2K_Opacity.tif', 'Billboard_2K_Translucency.tif', 'Billboard_2K_Roughness.tif', 'Billboard_2K_AO.tif', 'Billboard_2K_Albedo.tif'], '/mnt/Projects/tmp/autoMat_rnd/sourceimages/julian_endterm300_textures/plants/wild_grass_01/Textures/Atlas': ['vlkhcbxia_2K_Translucency.tif', 'vlkhcbxia_2K_Roughness.tif', 'vlkhcbxia_2K_AO.tif', 'vlkhcbxia_2K_Displacement.exr', 'vlkhcbxia_2K_Normal.tif', 'vlkhcbxia_2K_Albedo.tif', 'vlkhcbxia_2K_Opacity.tif'], '/mnt/Projects/tmp/autoMat_rnd/sourceimages/julian_endterm300_textures/plants/wild_grass_01/Textures/Billboard': ['Billboard_2K_AO.tif', 'Billboard_2K_Displacement.exr', 'Billboard_2K_Albedo.tif', 'Billboard_2K_Normal.tif', 'Billboard_2K_Opacity.tif', 'Billboard_2K_Translucency.tif', 'Billboard_2K_Roughness.tif']}

texture_list = ['Billboard_2K_Displacement.exr',
                'Billboard_2K_Displacement.exr', 'Billboard_2K_Displacement.exr', 'Billboard_2K_Displacement.exr', 'Billboard_2K_Displacement.exr']

image_node = 'aiImage'


def rename_if_exists(node_name):
    counter = 1  # init counter

    if cmds.objExists(node_name):
        while cmds.objExists(node_name + str(counter)):
            counter += 1

        return node_name + str(counter)
    else:

        return node_name


for item in texture_list:
    # INFO first check in top level structure neccessary
    node_name = os.path.splitext(item)[0]

    cmds.shadingNode(image_node, name=rename_if_exists(node_name),
                     asTexture=True, isColorManaged=True)
