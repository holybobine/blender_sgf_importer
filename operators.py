import bpy
import os
import bmesh
import mathutils

from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import *
from . import funcs





class SGF_OT_import(bpy.types.Operator, ImportHelper):
    """"""
    bl_idname = 'sgf.import'
    bl_label='Import .sgf'
    bl_options = {'UNDO'}

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
                funcs.select_object_solo(obj)
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

        return {'FINISHED'} 


class SGF_OT_export_to_svg(bpy.types.Operator, ExportHelper):
    """"""
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

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        obj = context.object
        modifier = funcs.get_sgf_modifier(context.object)

        split = layout.split(factor=0.4)
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column()

        col1.label(text='Board')
        col1.label(text='')
        col1.label(text='')
        col2.prop(scn.sgf_settings, 'export_outer_edge')
        col2.prop(scn.sgf_settings, 'export_grid')
        col2.prop(scn.sgf_settings, 'export_hoshis')

        col1.separator()
        col2.separator()

        col1.label(text='Stones')
        col2.prop(scn.sgf_settings, 'export_black_stones')
        col2.prop(scn.sgf_settings, 'export_white_stones')
    
    def execute(self, context):

        obj = context.object

        # store values to be restored

        obj_loc = obj.location.copy()
        obj_rot = obj.rotation_euler.copy()
        obj_sca = obj.scale.copy()

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


        # reset obj transforms

        obj_x = -1 - funcs.get_bound_box_min_from_obj(obj)[1]
        obj_y = 1 - funcs.get_bound_box_max_from_obj(obj)[1]

        obj.location = (0, 0, 0)
        # obj.location = (-1, 1, 0)
        obj.rotation_euler = (0, 0, 0)
        obj.scale = (1, 1, 1)


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

        obj.location = obj_loc
        obj.rotation_euler = obj_rot
        obj.scale = obj_sca

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
    

        

        return {'FINISHED'} 
    


classes = [    
    SGF_OT_import,
    SGF_OT_bouton,
    SGF_OT_increment_current_move,
    SGF_OT_export_to_svg,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)