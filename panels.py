import bpy
import os

from . import funcs



def poll_draw_sgf_panel(context):
    if not context.object:
        return
    
    if not context.object.sgf_settings.is_sgf_object:
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
        
        

        # if context.object:
        #     row = layout.row(align=True)
        
        #     op = row.operator(operator='sgf.import', text='Choose .sgf file', icon='FILEBROWSER')
        #     op.action = 'UPDATE'
        #     op = row.operator(operator='sgf.import', text='', icon='ADD')
        #     op.action = 'NEW'
        # else:
            # op = layout.operator(operator='sgf.import', text='New board from .sgf file', icon='ADD')
            # op.action = 'NEW'

        op = layout.operator(operator='sgf.import', text='New board from .sgf file', icon='ADD')
        op.action = 'NEW'

        



class SGF_PT_sgf_settings(bpy.types.Panel):
    bl_label = "SGF Settings"
    bl_idname = "SGF_PT_sgf_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SGF Importer"

    @classmethod
    def poll(self, context):
        return bool(poll_draw_sgf_panel(context))

    def draw(self, context):

        layout = self.layout
        scn = context.scene
        

        obj = context.object
        modifier = funcs.get_sgf_modifier(context.object)

        # row = layout.row(align=True)
        # row.prop(obj.sgf_settings, 'sgf_filepath', text='')
        # op = row.operator(operator='sgf.import', text='', icon='FILEBROWSER')
        # op.action = 'UPDATE'



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

        col1.label(text='Komi :')
        col2.label(text=obj.sgf_settings.game_komi)
        
        col1.label(text='Handicap :')
        col2.label(text=obj.sgf_settings.game_handicap)

        col1.label(text='Result :')
        col2.label(text=obj.sgf_settings.game_result)

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

        op = row.operator(operator='sgf.import', text='Change .sgf file', icon='FILEBROWSER')
        op.action = 'UPDATE'

        row.operator(operator='sgf.bouton', text='Export to .csv', icon='EXPORT')



class SGF_PT_board_settings(bpy.types.Panel):
    bl_label = "Board Settings"
    bl_idname = "SGF_PT_board_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SGF Importer"

    @classmethod
    def poll(self, context):
        return bool(poll_draw_sgf_panel(context))

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        
        obj = context.object
        modifier = funcs.get_sgf_modifier(context.object)

        

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

        col1.label(text='Width (cm)')
        col2.prop(obj.sgf_settings, 'board_width', text='')

        col1.label(text='Height (cm)')
        col2.prop(obj.sgf_settings, 'board_height', text='')

        col1.separator()
        col2.separator()

        col1.label(text='Hoshi (mm)')
        col2.prop(obj.sgf_settings, 'hoshi_radius', text='')

        col1.label(text='Stones (mm)')
        col2.prop(obj.sgf_settings, 'stone_radius', text='')

        col1.separator()
        col2.separator()

        col1.label(text='Stones display')
        row = col2.row(align=True)
        row.prop(obj.sgf_settings, 'stone_display', text='Wire', toggle=True, invert_checkbox=True)
        row.prop(obj.sgf_settings, 'stone_display', text='Mesh', toggle=True)
        
        
        

        box = layout.box()
        col = box.column()
        col.enabled = False

        spacing_x = (obj.sgf_settings.board_width/19)*10
        spacing_y = (obj.sgf_settings.board_height/19)*10

        col.label(text='Espacement (horizontal) : %.2f mm'%spacing_x)
        col.label(text='Espacement (vertical) : %.2f mm'%spacing_y)


        

        

        
class SGF_PT_export_settings(bpy.types.Panel):
    bl_label = "Export settings"
    bl_idname = "SGF_PT_export_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'SGF_PT_sgf_settings'
    bl_category = "SGF Importer"

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

        col1.label(text='Board')
        col1.label(text='')
        col1.label(text='')
        funcs.draw_prop_geonode(col2, modifier, 'show_outer_edge', label_name='Outer Edge')
        funcs.draw_prop_geonode(col2, modifier, 'show_grid', label_name='Grid')
        funcs.draw_prop_geonode(col2, modifier, 'show_hoshis', label_name='Hoshis')

        col1.separator()
        col2.separator()

        col1.label(text='Stones')
        funcs.draw_prop_geonode(col2, modifier, 'show_black_stones', label_name='Black')
        funcs.draw_prop_geonode(col2, modifier, 'show_white_stones', label_name='White')

        
        # split = layout.split(factor=0.5)
        # col1 = split.column()
        # col1.alignment = 'RIGHT'
        # col2 = split.column()

        # funcs.draw_prop_geonode(col2, modifier, 'show_outer_edge', label_name='Edge', icon='MESH_PLANE')
        # funcs.draw_prop_geonode(col2, modifier, 'show_grid', label_name='Grid', icon='MESH_GRID')
        # funcs.draw_prop_geonode(col2, modifier, 'show_hoshis', label_name='Hoshis', icon='OUTLINER_DATA_POINTCLOUD')
        

        # funcs.draw_prop_geonode(col1, modifier, 'show_black_stones', label_name='Black Stones', icon='NODE_MATERIAL')
        # funcs.draw_prop_geonode(col1, modifier, 'show_white_stones', label_name='White Stones', icon='SHADING_SOLID')


classes = [    
    SGF_PT_main_panel,
    SGF_PT_sgf_settings,
    SGF_PT_board_settings,
    SGF_PT_export_settings,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)