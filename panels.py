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
        
        obj = context.object
        modifier = funcs.get_sgf_modifier(context.object)

        
        layout.operator(operator='sgf.import', text='Import .sgf file', icon='FILEBROWSER')

        # layout.operator(operator='sgf.bouton')


class SGF_PT_settings_panel(bpy.types.Panel):
    bl_label = "SGF Settings"
    bl_idname = "SGF_PT_settings_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SGF Importer"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        
        obj = context.object
        modifier = funcs.get_sgf_modifier(context.object)

        funcs.draw_prop_geonode(layout, modifier, 'board_name', label_name='Nom')

        col = layout.column(align=True)
        col.prop(obj.sgf_settings, 'current_move', text='Coup')

        row = col.row(align=True)
        op = row.operator('sgf.increment_current_move', text='<<')
        op.value = -10
        op = row.operator('sgf.increment_current_move', text='<')
        op.value = -1
        op = row.operator('sgf.increment_current_move', text='>')
        op.value = 1
        op = row.operator('sgf.increment_current_move', text='>>')
        op.value = 10

        col = layout.column(align=True)
        col.prop(obj.sgf_settings, 'board_width', text='Largeur (cm)')
        col.prop(obj.sgf_settings, 'board_height', text='Hauteur (cm)')

        col = layout.column(align=True)
        funcs.draw_prop_geonode(col, modifier, 'hoshi_radius', label_name='Hoshi (mm)')
        funcs.draw_prop_geonode(col, modifier, 'stone_radius', label_name='Pierres (mm)')
        funcs.draw_prop_geonode(layout, modifier, 'showStones')

        box = layout.box()
        col = box.column()
        col.enabled = False

        col.label(text='Espacement (horizontal) : %.2f mm'%obj.sgf_settings.spacing_x)
        col.label(text='Espacement (vertical) : %.2f mm'%obj.sgf_settings.spacing_y)


classes = [    
    SGF_PT_main_panel,
    SGF_PT_settings_panel,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)