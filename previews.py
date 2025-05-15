import bpy
import os

from bpy.props import *
from sys import path

from . import funcs



def generate_previews(pcoll_name):

    pcoll = preview_collections[pcoll_name]
    image_location = pcoll.images_location
    VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg')

    enum_items = []

    for i, image in enumerate(os.listdir(image_location)):
        if image.endswith(VALID_EXTENSIONS):
            
            item_name = image

            filepath = os.path.join(image_location, image)
            thumb = pcoll.load(image, filepath, 'IMAGE')
            enum_items.append((image, item_name.capitalize(), item_name.capitalize(), thumb.icon_id, i))

    return enum_items


def setup_new_preview_collection(name, dir):
    preview_collections[name] = bpy.utils.previews.new()
    preview_collections[name].images_location = os.path.join(addon_path, dir)


addon_path = os.path.dirname(__file__)
preview_collections = {}

def register():
    import bpy.utils.previews

    setup_new_preview_collection(name="sgf_icons", dir=r'.\icons')

    bpy.types.Scene.sgf_icons = bpy.props.EnumProperty( # type: ignore
            name='icons UI',
            items=generate_previews('sgf_icons'),
        )

def unregister():
    for pcoll in preview_collections.values():
            bpy.utils.previews.remove(pcoll)

    preview_collections.clear()