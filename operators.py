import bpy
import os
import bmesh
import mathutils

from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import *
from . import funcs





class SGF_OT_add_new(bpy.types.Operator, ImportHelper):
    """Create new board from .sgf file"""
    bl_idname = 'sgf.add_new'
    bl_label='Import .sgf'
    bl_options = {'UNDO'}

    # ImportHelper mixin class uses this
    ext = ".sgf"

    filepath = ''

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

            obj = funcs.add_new_sgf_object(self, context)
            funcs.select_object_solo(obj)

            
            funcs.del_all_vertices_in_obj(obj)
            funcs.load_board_from_sgf_file(obj, self.filepath)
            obj.sgf_settings.is_sgf_object = True
            

        return {'FINISHED'}

class SGF_OT_change_sgf_file(bpy.types.Operator, ImportHelper):
    """Choose another .sgf file for selected board"""
    bl_idname = 'sgf.change_sgf_file'
    bl_label='Choose another .sgf file'
    bl_options = {'UNDO'}

    # ImportHelper mixin class uses this
    ext = ".sgf"

    filter_glob: StringProperty( # type: ignore
        default='*'+ext,
        options={'HIDDEN'},
        maxlen=255,
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

        board_size = int(funcs.get_metadata_from_sgf_file(self.filepath, 'SZ'))

        game_result = funcs.get_metadata_from_sgf_file(self.filepath, 'RE')
        game_komi = funcs.get_metadata_from_sgf_file(self.filepath, 'KM')
        game_handicap = funcs.get_metadata_from_sgf_file(self.filepath, 'HA', fail_value='None')


        # display ascii board
        ascii_board = funcs.get_ascii_board_from_sgf_file(self.filepath)
        funcs.display_ascii_board(layout, ascii_board, board_size)


        # display game data
        box = layout.box()
        box.label(text='%s (%s)'%(player_black, player_black_rank), icon='NODE_MATERIAL')

        box = layout.box()
        box.label(text='%s (%s)'%(player_white, player_white_rank), icon='SHADING_SOLID')

        box = layout.box()
        split = box.split(factor=0.5)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        split.enabled = False

        # col1.label(text='Date :')
        # col2.label(text=obj.sgf_settings.game_date)

        col1.label(text='Board Size :')
        col2.label(text=f'{board_size}x{board_size}')

        box = layout.box()
        split = box.split(factor=0.5)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        split.enabled = False

        # col1.label(text='Date :')
        # col2.label(text=obj.sgf_settings.game_date)

        col1.label(text='Result :')
        col2.label(text=game_result)

        col1.label(text='Komi :')
        col2.label(text=game_komi)
        
        col1.label(text='Handicap :')
        col2.label(text=game_handicap)

        
        

        





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

            obj = bpy.context.active_object

            
            funcs.del_all_vertices_in_obj(obj)
            funcs.load_board_from_sgf_file(obj, self.filepath)
            obj.sgf_settings.is_sgf_object = True
            

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

        # funcs.set_view_top()

        sgf_path = context.object.sgf_settings.sgf_filepath
        board_size = 19

        ascii_board = funcs.get_ascii_board_from_sgf_file(sgf_path)
        funcs.display_ascii_board(ascii_board, board_size)

        return {'FINISHED'} 

class SGF_OT_export_to_svg(bpy.types.Operator, ExportHelper):
    """Export board to .svg"""
    bl_idname = 'sgf.export_to_svg'
    bl_label='Export SVG'
    bl_options = {'UNDO'}

    filepath = ''

    filename_ext = ".svg"

    filter_glob: StringProperty( # type: ignore
        default="*.svg",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # def draw(self, context):
    #     layout = self.layout
    #     scn = context.scene

    #     obj = context.object
    #     modifier = funcs.get_sgf_modifier(context.object)

    #     split = layout.split(factor=0.4)
    #     col1 = split.column()
    #     col1.alignment = 'RIGHT'
    #     col2 = split.column()

    #     col1.label(text='Board')
    #     col1.label(text='')
    #     col1.label(text='')
    #     col1.label(text='')
    #     col2.prop(scn.sgf_settings, 'export_edge')
    #     col2.prop(scn.sgf_settings, 'export_grid_x')
    #     col2.prop(scn.sgf_settings, 'export_grid_y')
    #     col2.prop(scn.sgf_settings, 'export_hoshis')

    #     col1.separator()
    #     col2.separator()

    #     col1.label(text='Stones')
    #     col2.prop(scn.sgf_settings, 'export_black_stones')
    #     col2.prop(scn.sgf_settings, 'export_white_stones')
    
    def execute(self, context):

        obj = context.object

        # store values to be restored

        resolution_x = bpy.data.scenes["Scene"].render.resolution_x
        resolution_y = bpy.data.scenes["Scene"].render.resolution_y

        areas_view_modes = []
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                areas_view_modes.append([
                    area,
                    area.spaces[0].region_3d.view_perspective,
                    area.spaces[0].use_local_camera,
                    area.spaces[0].camera,
                ])


        # setup camera view

        export_cam = funcs.create_export_cam_above_object(obj)

        bpy.data.scenes["Scene"].render.resolution_x = 1080
        bpy.data.scenes["Scene"].render.resolution_y = 1080

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].region_3d.view_perspective = 'CAMERA'
                area.spaces[0].use_local_camera = True
                area.spaces[0].camera = export_cam


        funcs.export_to_svg_ops(obj, self.filepath)

        # restore all to previous state

        bpy.data.scenes["Scene"].render.resolution_x = resolution_x
        bpy.data.scenes["Scene"].render.resolution_y = resolution_y

        for area in areas_view_modes:
            area_object = area[0]

            area_object.spaces[0].region_3d.view_perspective = 'PERSP'
            # area_object.spaces[0].region_3d.view_perspective = area[1]
            area_object.spaces[0].use_local_camera = area[2]
            area_object.spaces[0].camera = area[3]

        funcs.select_object_solo(export_cam)
        bpy.ops.object.delete()

        funcs.select_object_solo(obj)
    
        context.scene.sgf_settings.last_used_filepath = os.path.dirname(self.filepath)
        

        return {'FINISHED'} 


class SGF_OT_export_to_svg_multiple(bpy.types.Operator, ExportHelper):
    """Export multiple files to .svg"""
    bl_idname = 'sgf.export_to_svg_multiple'
    bl_label='Export SVG'
    bl_options = {'UNDO'}

    filepath = ''

    filename_ext = ".svg"

    filter_glob: StringProperty( # type: ignore
        default="*.svg",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def solo_layer_on_sgf_object(self, obj, sgf_layers, target_layer):

        modifier = funcs.get_sgf_modifier(obj)

        for layer in sgf_layers:
            funcs.set_geonode_value_proper(
                modifier=modifier, 
                input_name=layer[0], 
                value=bool(layer[0] == target_layer[0])
            )

        # display outer edge by default
        # funcs.set_geonode_value_proper(modifier, 'show_edge', True)

    def execute(self, context):
        
        obj = context.object
        modifier = funcs.get_sgf_modifier(obj)


        
        
        # print(temp_filepath)


        sgf_layers = [
            ['show_edge',  obj.sgf_settings.show_edge],
            ['show_grid_x', obj.sgf_settings.show_grid_x],
            ['show_grid_y', obj.sgf_settings.show_grid_y],
            ['show_hoshis', obj.sgf_settings.show_hoshis],
            ['show_black_stones', obj.sgf_settings.show_black_stones],
            ['show_white_stones', obj.sgf_settings.show_white_stones],
        ]

        for layer in sgf_layers:
            if layer[1] == True:

                print(f'exporting layer {layer[0]}')

                self.solo_layer_on_sgf_object(obj, sgf_layers, layer)

                svg_filepath = funcs.get_svg_filepath_for_single_export_from_modifier(modifier, user_filepath=self.filepath)
                # filename = funcs.build_filename_from_selection(self, context)
                

                bpy.ops.sgf.export_to_svg(
                    # filepath = os.path.join(filename, filepath)
                    filepath = svg_filepath
                )

        for layer in sgf_layers:
            funcs.set_geonode_value_proper(
                modifier=modifier, 
                input_name=layer[0], 
                value=bool(layer[1])
            )


        context.scene.sgf_settings.last_used_filepath = os.path.dirname(self.filepath)


        return {'FINISHED'} 


classes = [    
    SGF_OT_add_new,
    SGF_OT_change_sgf_file,
    SGF_OT_bouton,
    SGF_OT_increment_current_move,
    SGF_OT_export_to_svg,
    SGF_OT_export_to_svg_multiple,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)