import bpy
import os
import bmesh

from bpy_extras.io_utils import ImportHelper
from bpy.props import *
from . import funcs




class SGF_OT_import(bpy.types.Operator, ImportHelper):
    """"""
    bl_idname = 'sgf.import'
    bl_label='Import .sgf'

    # ImportHelper mixin class uses this
    ext = ".sgf"

    action: bpy.props.EnumProperty( # type: ignore
        items= (
                    ("NEW", "New", ""),
                    ("UPDATE", "Update", "")
                ),
    )

    filter_glob: StringProperty( # type: ignore
        default='*'+ext,
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        print('-INF- import new .sgf file')

        file_extension = os.path.splitext(self.filepath)[1]

        if file_extension != '.sgf':
            funcs.alert(
                    text='No .sgf file detected',
                    title='ERROR',
                    icon='ERROR'
                )
        else:

            if self.action == 'NEW':
                obj = funcs.add_new_sgf_object(self, context)
                funcs.select_object_solo(context, obj)
            else:
                obj = bpy.context.active_object

            
            funcs.del_all_vertices_in_obj(obj)
            funcs.load_board_from_sgf_file(obj, self.filepath)
            obj.sgf_settings.is_sgf_object = True
            

        return {'FINISHED'}


class SGF_OT_increment_current_move(bpy.types.Operator):
    """"""
    bl_idname = "sgf.increment_current_move"
    bl_label = ""

    value: bpy.props.IntProperty()  # type: ignore

    def execute(self, context):

        obj = context.object

        current_move = obj.sgf_settings.current_move
        move_max = obj.sgf_settings.move_max
        new_move = current_move + self.value

        if new_move < 0:
            new_move = 0

        if new_move > move_max:
            new_move = move_max

        obj.sgf_settings.current_move = new_move

        return {'FINISHED'}


class SGF_OT_bouton(bpy.types.Operator):
    """"""
    bl_idname = 'sgf.bouton'
    bl_label='BOUTON'

    def execute(self, context):
        print('BOUTON')

        sgf_path = context.object.sgf_settings.sgf_filepath
        ascii_board = funcs.get_ascii_board_from_sgf_file(sgf_path, 10)

        print(ascii_board)

        return {'FINISHED'}



classes = [    
    SGF_OT_import,
    SGF_OT_bouton,
    SGF_OT_increment_current_move,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)