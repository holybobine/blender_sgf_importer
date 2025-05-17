import bpy
import os
import bmesh
import mathutils

from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import *
from . import funcs




class SGF_OT_import_sgf_file(bpy.types.Operator, ImportHelper):
    """Import .sgf file"""
    bl_idname = 'sgf.import_sgf_file'
    bl_label='Import .sgf file'
    bl_options = {'UNDO'}

    # ImportHelper mixin class uses this
    ext = '.sgf'

    filepath = ''

    filter_glob: StringProperty( # type: ignore
        default='*'+ext,
        options={'HIDDEN'},
        maxlen=255,
    )

    action: EnumProperty( # type: ignore
        items=(
                ('NEW', 'Import new .sgf file', ''),
                ('UPDATE', 'Change .sgf file for current board', ''),
            ),
        default='NEW',
    )

    def draw(self, context):
        if not os.path.exists(self.filepath):
            return
        
        if not os.path.splitext(self.filepath)[1] == '.sgf':
            return
        
        layout = self.layout
        scn = context.scene

        # retrieve game data
        player_black = funcs.get_metadata_from_sgf_file(self.filepath, 'PB')
        player_white = funcs.get_metadata_from_sgf_file(self.filepath, 'PW')
        player_black_rank = funcs.get_metadata_from_sgf_file(self.filepath, 'BR', fail_value='?')
        player_white_rank = funcs.get_metadata_from_sgf_file(self.filepath, 'WR', fail_value='?')

        board_size = funcs.get_board_size(self.filepath)

        game_result = funcs.get_metadata_from_sgf_file(self.filepath, 'RE')
        game_komi = funcs.get_metadata_from_sgf_file(self.filepath, 'KM')
        game_handicap = funcs.get_metadata_from_sgf_file(self.filepath, 'HA', fail_value='None')
        game_date = funcs.get_metadata_from_sgf_file(self.filepath, 'DT')

        # players
        box = layout.box()
        box.label(text='%s (%s)'%(player_black, player_black_rank), icon='NODE_MATERIAL')

        box = layout.box()
        box.label(text='%s (%s)'%(player_white, player_white_rank), icon='SHADING_SOLID')

        # game data
        box = layout.box()
        split = box.split(factor=0.5)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        split.enabled = False

        # col1.label(text='Date :')
        # col2.label(text=obj.sgf_settings.game_date)

        col1.label(text='Date :')
        col2.label(text=game_date)

        col1.label(text='Result :')
        col2.label(text=game_result)

        col1.label(text='Komi :')
        col2.label(text=game_komi)
        
        col1.label(text='Handicap :')
        col2.label(text=game_handicap)

        

        # ascii board
        funcs.display_ascii_board(layout, self.filepath, board_size)

    def execute(self, context):
        print('-INF- import new .sgf file')
        
        print(self.filepath)

        if self.action == 'NEW':
            obj = funcs.add_new_sgf_object(self, context)
        elif self.action == 'UPDATE':
            obj = bpy.context.active_object

        funcs.select_object_solo(obj)
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        funcs.del_all_vertices_in_obj(obj)
        funcs.load_board_from_sgf_file(obj, self.filepath)
        
            

        return {'FINISHED'}

class SGF_OT_increment_current_move(bpy.types.Operator):
    """"""
    bl_idname = "sgf.increment_current_move"
    bl_label = ""
    bl_options = {'UNDO'}

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
    bl_options = {'UNDO'}

    def execute(self, context):
        print('BOUTON')

        # obj = context.object
        # modifier = funcs.get_sgf_modifier(obj)

        # funcs.set_geonode_value(modifier, 'board_name', 'JOOOHN')

        print()

        return {'FINISHED'} 



class SGF_OT_export_board_to_svg(bpy.types.Operator, ExportHelper):
    """Export board to .svg"""
    bl_idname = 'sgf.export_board_to_svg'
    bl_label='Export SVG'
    bl_options = {'UNDO'}

    filepath = ''

    filename_ext = ".svg"

    filter_glob: StringProperty( # type: ignore
        default="*.svg",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        

        split = layout.split(factor=0.4)
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column()

        col1.label(text='Export Method')
        row = col2.row(align=True)
        row.prop(scn.sgf_settings, 'export_method', text='')

        col1.label(text='Board')
        col1.label(text='')
        col1.label(text='')
        col1.label(text='')
        col2.prop(scn.sgf_settings, 'export_edge')
        col2.prop(scn.sgf_settings, 'export_grid_x')
        col2.prop(scn.sgf_settings, 'export_grid_y')
        col2.prop(scn.sgf_settings, 'export_hoshis')

        col1.separator()
        col2.separator()

        col1.label(text='Stones')
        col2.prop(scn.sgf_settings, 'export_black_stones')
        col2.prop(scn.sgf_settings, 'export_white_stones')



    def execute(self, context):
        scn = context.scene
        obj = context.object
        modifier = funcs.get_sgf_modifier(obj)
       

        svg_filepath = funcs.get_svg_filepath_for_single_export_from_modifier(modifier, user_filepath=self.filepath)

        if scn.sgf_settings.export_method == 'single':
            funcs.export_to_svg(obj, svg_filepath)
        elif scn.sgf_settings.export_method == 'multiple':
            funcs.export_multiple_to_svg(obj, svg_filepath)

        context.scene.sgf_settings.last_used_filepath = os.path.dirname(self.filepath)


        return {'FINISHED'} 


classes = [    
    SGF_OT_import_sgf_file,
    SGF_OT_bouton,
    SGF_OT_increment_current_move,
    SGF_OT_export_board_to_svg,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)