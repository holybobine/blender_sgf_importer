import bpy
import os
from bpy.props import *
from bpy.types import PropertyGroup

from . import funcs


def get_limited_value(self):
    return self.get('current_move', 0)

def set_limited_value(self, new_value):

    if new_value > bpy.context.object.sgf_settings.move_max:
        new_value = bpy.context.object.sgf_settings.move_max

    self['current_move'] = new_value
 
    

class SGF_board_props(PropertyGroup):

    sgf_filepath : StringProperty() # type: ignore

    is_valid_sgf_file : BoolProperty(default=False) # type: ignore
    is_sgf_object : BoolProperty(default=False) # type: ignore

    current_move : IntProperty( # type: ignore
        name='Target Move',
        default=0,
        soft_min=0,
        get=lambda self: get_limited_value(self),
        set=lambda self, value: set_limited_value(self, value),
        update=funcs.update_board_from_move, 
    )

    move_max : IntProperty() # type: ignore

    board_size : IntProperty( # type: ignore
        name='Board Size',
        default=19,
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'board_size')
    )

    board_width : FloatProperty( # type: ignore
        name='Width',
        default=397.8,
        precision=4,
        subtype='DISTANCE_CAMERA',
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'board_width')
    )
    
    board_height : FloatProperty( # type: ignore
        name='Height',
        default=426.6,
        precision=4,
        subtype='DISTANCE_CAMERA',
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'board_height')
    )
    
    hoshi_radius : FloatProperty( # type: ignore
        name='Hoshis',
        default=5.0,
        precision=4,
        subtype='DISTANCE_CAMERA',
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'hoshi_radius')
    )
    
    stone_radius : FloatProperty( # type: ignore
        name='Stones',
        default=22.0,
        precision=4,
        subtype='DISTANCE_CAMERA',
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'stone_radius')
    )

    outer_edge_ratio : FloatProperty( # type: ignore
        name='Edge Margin',
        default=10,
        soft_min=0,
        soft_max=100,
        subtype='PERCENTAGE',
        precision=0,
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'outer_edge_ratio')
    )

    stone_display : BoolProperty( # type: ignore
        name='stone_display',
        default=True, 
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'stone_display')
    )

    show_edge : BoolProperty( # type: ignore
        name='Edge',
        default=True,
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'show_edge')
    )
    show_grid_x : BoolProperty( # type: ignore
        name='Grid X',
        default=True,
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'show_grid_x')
    )
    show_grid_y : BoolProperty( # type: ignore
        name='Grid Y',
        default=True,
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'show_grid_y')
    )
    show_hoshis : BoolProperty( # type: ignore
        name='Hoshis',
        default=True,
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'show_hoshis')
    )
    show_black_stones : BoolProperty( # type: ignore
        name='Black',
        default=True,
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'show_black_stones')
    )
    show_white_stones : BoolProperty( # type: ignore
        name='White',
        default=True,
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'show_white_stones')
    )

    export_method : EnumProperty( # type: ignore
        items=(
                ('single', 'Single file', '', 'FILE', 0),
                ('multiple', 'Multiple files', '', 'DOCUMENTS', 1),
            ),
        name='Export Method',
        default='single',
        )
    


    PB : StringProperty() # type: ignore
    PW : StringProperty() # type: ignore
    PB_rank : StringProperty() # type: ignore
    PW_rank : StringProperty() # type: ignore
    
    game_name : StringProperty() # type: ignore
    game_event : StringProperty() # type: ignore
    game_app : StringProperty() # type: ignore
    game_rules : StringProperty() # type: ignore
    game_date : StringProperty() # type: ignore
    game_komi : StringProperty() # type: ignore
    game_handicap : StringProperty() # type: ignore
    game_result : StringProperty() # type: ignore




class SGF_scene_settings(PropertyGroup):

    addon_path = os.path.dirname(__file__)

    assetFilePath : StringProperty(default=os.path.join(addon_path, 'blend_assets', 'blender_sgf_importer_assets_v02.blend')) # type: ignore

    last_used_filepath : StringProperty() # type: ignore


classes = [
    SGF_scene_settings,
    SGF_board_props,
    
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.sgf_settings = PointerProperty(type=SGF_scene_settings) # type: ignore
    bpy.types.Object.sgf_settings = PointerProperty(type=SGF_board_props) # type: ignore


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)