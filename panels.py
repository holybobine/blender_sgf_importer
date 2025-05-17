import bpy
import os

from . import funcs

def draw_prop_geonode(context, gn_modifier, input_name, label_name='', enabled=True, label=True, icon='NONE', toggle=-1, invert_checkbox=False):

    input = funcs.get_geonode_input_from_modifier(gn_modifier, input_name)
    input_id = input.identifier

    # print(input_id)

    if input_id:
        row = context.row(align=True)
        row.prop(
            data = gn_modifier,
            text = label_name if label_name != '' else input_name if label else '',
            property = '["%s"]'%input_id,
            icon = icon,
            emboss = True,
            toggle=toggle,
            invert_checkbox=invert_checkbox,
        )

        row.enabled = enabled

def alert(text = "", title = "Message Box", icon = 'INFO'):

    print('- ALERT -', text)

    def draw(self, context):
        self.layout.label(text=text)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)



def poll_draw_sgf_panel(context):
    if not context.object:
        return
    
    if not context.object.sgf_settings.is_sgf_object:
        return
    
    if not context.object.modifiers:
        return

    return True

def poll_draw_sgf_settings(context):
    if not bool(poll_draw_sgf_panel(context)):
        return

    if not context.object.sgf_settings.is_valid_sgf_file:
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
            op = layout.operator(operator='sgf.import_sgf_file', text='New board from .sgf file', icon='ADD')
            op.action = 'NEW'

            return
        
        row = layout.row(align=True)
        op = row.operator(operator='sgf.import_sgf_file', text='Change .sgf file', icon='FILEBROWSER')
        op.action = 'UPDATE'

        op = row.operator(operator='sgf.import_sgf_file', text='', icon='ADD')
        op.action = 'NEW'

        if not os.path.exists(context.object.sgf_settings.sgf_filepath):
            box = layout.box()
            box.alert = True
            box.label(text='Can\'t locate .sgf file', icon='ERROR')

            return
        
        

        obj = context.object
        modifier = funcs.get_sgf_modifier(context.object)

        # sgf_path = context.object.sgf_settings.sgf_filepath
        # board_size = context.object.sgf_settings.board_size

        # funcs.display_ascii_board(layout, sgf_path, board_size)

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

        if not obj.sgf_settings.is_valid_sgf_file:
            box = layout.box()
            box.alert = True
            box.label(text='Error while decoding .sgf file', icon='ERROR')

            return

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

        row = layout.row()

        svg_filepath = funcs.get_svg_filepath_for_multiple_export()
        op = row.operator(operator='sgf.export_board_to_svg', text='Export to SVG', icon='EXPORT')
        op.filepath = svg_filepath

class SGF_PT_board_settings(bpy.types.Panel):
    bl_label = "Board"
    bl_idname = "SGF_PT_board_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SGF Importer"
    bl_parent_id = "SGF_PT_main_panel"

    @classmethod
    def poll(self, context):
        return bool(poll_draw_sgf_settings(context))

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
        # draw_prop_geonode(row, modifier, 'show_board_name', label=False)
        row.prop(obj.sgf_settings, 'show_board_name', text='')   

        rrow = row.row()
        # rrow.enabled = funcs.get_geonode_value(modifier, 'show_board_name')
        rrow.enabled = obj.sgf_settings.show_board_name
        draw_prop_geonode(rrow, modifier, 'board_name', label=False)

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

        # box = layout.box()
        # col = box.column()
        # col.enabled = False

        # spacing_x = (obj.sgf_settings.board_width/19)
        # spacing_y = (obj.sgf_settings.board_height/19)

        # col.label(text='Line spacing X : %.2f mm'%spacing_x)
        # col.label(text='Line spacing Y : %.2f mm'%spacing_y)



class SGF_PT_stones_settings(bpy.types.Panel):
    bl_label = "Stones"
    bl_idname = "SGF_PT_stones_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SGF Importer"
    bl_parent_id = "SGF_PT_main_panel"

    @classmethod
    def poll(self, context):
        return bool(poll_draw_sgf_settings(context))

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        
        obj = context.object
        modifier = funcs.get_sgf_modifier(context.object)

        split = layout.split(factor=0.4)
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column()

        col1.label(text='Type')
        col2.prop(obj.sgf_settings, 'stone_display', text='')

        col1.label(text='Quality')
        row = col2.row()
        row.prop(obj.sgf_settings, 'stone_quality', expand=True)

        col1.label(text='Radius')
        col2.prop(obj.sgf_settings, 'stone_radius', text='')


classes = [    
    SGF_PT_main_panel,
    SGF_PT_board_settings,
    SGF_PT_stones_settings,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)