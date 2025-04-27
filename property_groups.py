import bpy
import os
from bpy.props import *
from bpy.types import PropertyGroup

from . import funcs

class SGF_board_props(PropertyGroup):

    is_sgf_object : BoolProperty(default=False) # type: ignore
    
    sgf_filepath : StringProperty() # type: ignore

    current_move : IntProperty( # type: ignore
        name='Target Move',
        default=0,
        soft_min=0,
        get=lambda self: funcs.get_limited_value(self),
        set=lambda self, value: funcs.set_limited_value(self, value),
        update=funcs.update_board_from_move, 
    )

    move_max : IntProperty() # type: ignore

    board_width : bpy.props.FloatProperty( # type: ignore
        name='board_width',
        default=39.78, 
        precision=2,
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'board_width')
    )
    
    board_height : bpy.props.FloatProperty( # type: ignore
        name='board_height',
        default=42.66, 
        precision=2,
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'board_height')
    )
    
    hoshi_radius : bpy.props.FloatProperty( # type: ignore
        name='hoshi_radius',
        default=5.0, 
        precision=2,
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'hoshi_radius')
    )
    
    stone_radius : bpy.props.FloatProperty( # type: ignore
        name='stone_radius',
        default=22.0, 
        precision=2,
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'stone_radius')
    )

    stone_display : bpy.props.BoolProperty( # type: ignore
        name='stone_display',
        default=True, 
        update=lambda self, prop_name: funcs.update_geonode_value_from_property(self, 'stone_display')
    )
    

    spacing_x : bpy.props.FloatProperty(default=0.0) # type: ignore
    spacing_y : bpy.props.FloatProperty(default=0.0) # type: ignore


    PB : StringProperty() # type: ignore
    PW : StringProperty() # type: ignore
    PB_rank : StringProperty() # type: ignore
    PW_rank : StringProperty() # type: ignore
    
    game_name : StringProperty() # type: ignore
    game_event : StringProperty() # type: ignore
    game_app : StringProperty() # type: ignore
    game_size : StringProperty() # type: ignore
    game_rules : StringProperty() # type: ignore
    game_date : StringProperty() # type: ignore
    game_komi : StringProperty() # type: ignore
    game_handicap : StringProperty() # type: ignore
    game_result : StringProperty() # type: ignore




class SGF_scene_settings(PropertyGroup):

    addon_path = os.path.dirname(__file__)

    assetFilePath : StringProperty(default=os.path.join(addon_path, 'blend_assets', 'blender_sgf_importer_assets_v00.blend')) # type: ignore


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