import bpy
import os

from . import funcs



def poll_draw_sgf_panel(context):
    if not context.object:
        return
    
    if not context.object.sgf_settings.is_sgf_object:
        return
    
    if not context.object.modifiers:
        return

    return True

class SGF_PT_main_panel(bpy.types.Panel):
    bl_label = "SGF Importer"
    bl_idname = "SGF_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SGF Importer"

    def draw(self, context):
        layout = self.layout
        scn = context.scene  
        
        # layout.operator(operator='sgf.bouton')

        if not bool(poll_draw_sgf_panel(context)):
            op = layout.operator(operator='sgf.add_new', text='New board from .sgf file', icon='ADD')

            return
        
        row = layout.row(align=True)
        op = row.operator(operator='sgf.change_sgf_file', text='Change .sgf file', icon='FILEBROWSER')
        op = row.operator(operator='sgf.add_new', text='', icon='ADD')

        if not os.path.exists(context.object.sgf_settings.sgf_filepath):

            box = layout.box()
            box.alert = True

            box.label(text='Can\'t locate .sgf file', icon='ERROR')

            return
        
        

        obj = context.object
        modifier = funcs.get_sgf_modifier(context.object)

        # sgf_path = context.object.sgf_settings.sgf_filepath
        # board_size = context.object.sgf_settings.board_size
        # ascii_board = funcs.get_ascii_board_from_sgf_file(sgf_path)

        # funcs.display_ascii_board(layout, ascii_board, board_size)

        row = layout.row()

        box = row.box()
        box.label(text='%s (%s)'%(obj.sgf_settings.PB, obj.sgf_settings.PB_rank), icon='NODE_MATERIAL')

        box = row.box()
        box.label(text='%s (%s)'%(obj.sgf_settings.PW, obj.sgf_settings.PW_rank), icon='SHADING_SOLID')

        box = layout.box()
        split = box.split(factor=0.5)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        split.enabled = False

        # col1.label(text='Date :')
        # col2.label(text=obj.sgf_settings.game_date)

        col1.label(text='Result :')
        col2.label(text=obj.sgf_settings.game_result)

        col1.label(text='Komi :')
        col2.label(text=obj.sgf_settings.game_komi)
        
        col1.label(text='Handicap :')
        col2.label(text=obj.sgf_settings.game_handicap)

        

        col = layout.column(align=True)

        row = col.row(align=True)
        row.scale_x = 20.0
        op = row.operator('sgf.increment_current_move', text='', icon='REW')
        op.value = -9999
        op = row.operator('sgf.increment_current_move', text='', icon='FRAME_PREV')
        op.value = -10
        op = row.operator('sgf.increment_current_move', text='', icon='TRIA_LEFT')
        op.value = -1
        op = row.operator('sgf.increment_current_move', text='', icon='TRIA_RIGHT')
        op.value = 1
        op = row.operator('sgf.increment_current_move', text='', icon='FRAME_NEXT')
        op.value = 10
        op = row.operator('sgf.increment_current_move', text='', icon='FF')
        op.value = 9999

        col.prop(obj.sgf_settings, 'current_move', text='Move')

class SGF_PT_board_settings(bpy.types.Panel):
    bl_label = "Board Settings"
    bl_idname = "SGF_PT_board_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SGF Importer"
    bl_parent_id = "SGF_PT_main_panel"

    @classmethod
    def poll(self, context):
        return bool(poll_draw_sgf_panel(context))

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        
        obj = context.object
        modifier = funcs.get_sgf_modifier(context.object)

        # layout.prop(obj.sgf_settings, 'board_width')
        # layout.prop(obj.sgf_settings, 'board_height')
        # layout.prop(obj.sgf_settings, 'hoshi_radius')
        # layout.prop(obj.sgf_settings, 'stone_radius')

        split = layout.split(factor=0.4)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Board Name')
        row = col2.row(align=True)
        funcs.draw_prop_geonode(row, modifier, 'show_board_name', label=False)

        rrow = row.row()
        rrow.enabled = funcs.get_geonode_value_proper(modifier, 'show_board_name')
        funcs.draw_prop_geonode(rrow, modifier, 'board_name', label=False) 

        col1.separator()
        col2.separator()

        col1.label(text='Outer Edge')
        col2.prop(obj.sgf_settings, 'outer_edge_ratio', text='')    

        col1.separator()
        col2.separator()

        col1.label(text='Width')
        col2.prop(obj.sgf_settings, 'board_width', text='')

        col1.label(text='Height')
        col2.prop(obj.sgf_settings, 'board_height', text='')

        col1.separator()
        col2.separator()

        col1.label(text='Hoshi')
        col2.prop(obj.sgf_settings, 'hoshi_radius', text='')

        col1.separator()
        col2.separator()

        col1.label(text='Stones')
        col2.prop(obj.sgf_settings, 'stone_radius', text='')

        row = col2.row(align=True)
        row.prop(obj.sgf_settings, 'stone_display', text='Wire', toggle=True, invert_checkbox=True)
        row.prop(obj.sgf_settings, 'stone_display', text='Mesh', toggle=True)

        # box = layout.box()
        # col = box.column()
        # col.enabled = False

        # spacing_x = (obj.sgf_settings.board_width/19)
        # spacing_y = (obj.sgf_settings.board_height/19)

        # col.label(text='Line spacing X : %.2f mm'%spacing_x)
        # col.label(text='Line spacing Y : %.2f mm'%spacing_y)

class SGF_PT_export_settings(bpy.types.Panel):
    bl_label = "Export"
    bl_idname = "SGF_PT_export_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SGF Importer"
    bl_parent_id = "SGF_PT_main_panel"

    @classmethod
    def poll(self, context):
        return bool(poll_draw_sgf_panel(context))

    def draw(self, context):

        layout = self.layout
        scn = context.scene
        

        obj = context.object
        modifier = funcs.get_sgf_modifier(context.object)


        split = layout.split(factor=0.4)
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column()

        

        col1.label(text='Export Method')
        row = col2.row(align=True)
        row.prop(obj.sgf_settings, 'export_method', text='')

        col1.separator()
        col2.separator()

        col1.label(text='Board')
        col1.label(text='')
        col1.label(text='')
        col1.label(text='')
        col2.prop(obj.sgf_settings, 'show_edge')
        col2.prop(obj.sgf_settings, 'show_grid_x')
        col2.prop(obj.sgf_settings, 'show_grid_y')
        col2.prop(obj.sgf_settings, 'show_hoshis')

        col1.separator()
        col2.separator()

        col1.label(text='Stones')
        col1.label(text='')
        col2.prop(obj.sgf_settings, 'show_black_stones')
        col2.prop(obj.sgf_settings, 'show_white_stones')

        nb_files = sum([
            obj.sgf_settings.show_edge,
            obj.sgf_settings.show_grid_x,
            obj.sgf_settings.show_grid_y,
            obj.sgf_settings.show_hoshis,
            obj.sgf_settings.show_black_stones,
            obj.sgf_settings.show_white_stones,
        ])

        row = layout.row()

        if nb_files == 0:
            row.alert=True
            row.enabled = False
            op_name = 'sgf.export_to_svg'
            op_text='Nothing to export'
            op_icon = 'ERROR'
            svg_filepath = ''
            

        elif obj.sgf_settings.export_method == 'single':
            op_name = 'sgf.export_to_svg'
            op_text='Export to .svg'
            op_icon = 'EXPORT'
            svg_filepath = funcs.get_svg_filepath_for_single_export_from_modifier(modifier)

        elif obj.sgf_settings.export_method == 'multiple':
            op_name = 'sgf.export_to_svg_multiple'
            # op_name = 'sgf.bouton'
            op_text=f'Export {nb_files} .svg files'
            op_icon = 'EXPORT'
            svg_filepath = funcs.get_svg_filepath_for_multiple_export()



        op = row.operator(operator=op_name, text=op_text, icon=op_icon)
        op.filepath = svg_filepath


classes = [    
    SGF_PT_main_panel,
    SGF_PT_board_settings,
    SGF_PT_export_settings,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)