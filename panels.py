import bpy
import os

from . import funcs





class SGF_PT_main_panel(bpy.types.Panel):
    bl_label = "SGF Importer"
    bl_idname = "SGF_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SGF Importer"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        
        

        if context.object:
            row = layout.row(align=True)
        
            op = row.operator(operator='sgf.import', text='Choose .sgf file', icon='FILEBROWSER')
            op.action = 'UPDATE'
            op = row.operator(operator='sgf.import', text='', icon='ADD')
            op.action = 'NEW'
        else:
            op = layout.operator(operator='sgf.import', text='New board from .sgf file', icon='ADD')
            op.action = 'NEW'

        # layout.operator(operator='sgf.bouton')

        if not context.object:
            return

        obj = context.object
        modifier = funcs.get_sgf_modifier(context.object)

        col = layout.column(align=True)
        col.prop(obj.sgf_settings, 'current_move', text='Coup')

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

        box = layout.box()
        split = box.split(factor=0.3)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        split.enabled = False

        col1.label(text='Noir :')
        col2.label(text='%s (%s)'%(obj.sgf_settings.PB, obj.sgf_settings.PB_rank))

        col1.label(text='Blanc :')
        col2.label(text='%s (%s)'%(obj.sgf_settings.PW, obj.sgf_settings.PW_rank))

        box = layout.box()
        split = box.split(factor=0.3)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        split.enabled = False

        col1.label(text='Date :')
        col2.label(text=obj.sgf_settings.game_date)

        col1.label(text='Komi :')
        col2.label(text=obj.sgf_settings.game_komi)
        
        col1.label(text='Handicap :')
        col2.label(text=obj.sgf_settings.game_handicap)

        col1.label(text='Résultat :')
        col2.label(text=obj.sgf_settings.game_result)



class SGF_PT_board_settings(bpy.types.Panel):
    bl_label = "Board Settings"
    bl_idname = "SGF_PT_board_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SGF Importer"

    @classmethod
    def poll(self, context):
        return context.object

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
        funcs.draw_prop_geonode(col2, modifier, 'board_name', label=False)

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

classes = [    
    SGF_PT_main_panel,
    SGF_PT_board_settings,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)