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

        layout.label(text='hello')

        layout.operator(operator='sgf.import', text='Import')
        layout.operator(operator='sgf.bouton')


        funcs.draw_prop_geonode(layout, modifier, 'Move')

classes = [    
    SGF_PT_main_panel,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)