import bpy
from bpy.props import *
from bpy.types import PropertyGroup

from . import funcs

class SGF_board_props(PropertyGroup):
    current_move : IntProperty( # type: ignore
        name='Target Move',
        default=0,
        soft_min=0,
        update=funcs.update_board_from_move, 
    )
    move_max : IntProperty() # type: ignore

    board_width : bpy.props.FloatProperty(default=39.78, update=funcs.update_board_size) # type: ignore
    board_height : bpy.props.FloatProperty(default=42.66, update=funcs.update_board_size) # type: ignore

    spacing_x : bpy.props.FloatProperty(default=0.0) # type: ignore
    spacing_y : bpy.props.FloatProperty(default=0.0) # type: ignore


classes = [
    SGF_board_props,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Object.sgf_settings = PointerProperty(type=SGF_board_props) # type: ignore


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)