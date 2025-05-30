import bpy
import bmesh

import os
import math

from .sgfmill import sgf
from .sgfmill import sgf_moves
from .sgfmill import ascii_boards

from .previews import preview_collections


# geonodes funcs
def get_geonode_input_from_modifier(modifier, input_name):
    if bpy.app.version < (4, 0, 0):
        inputs = modifier.node_group.inputs
    elif bpy.app.version >= (4, 0, 0):
        inputs = modifier.node_group.interface.items_tree

    return inputs.get(input_name)

def get_geonode_value(modifier, input_name):
    input = get_geonode_input_from_modifier(modifier, input_name)
    return modifier[input.identifier]

def set_geonode_value(modifier, input_name, value):
    input = get_geonode_input_from_modifier(modifier, input_name)
    input_type = type(input.default_value).__name__

    if input_type == 'bool':
        value = bool(value)
    elif input_type == 'float':
        value = float(value)
    elif input_type == 'int':
        value = int(value)

    value_type = type(value).__name__

    if input_type == value_type:
        modifier[input.identifier] = value
    else:
        print(f'-ERR- setting {input.name} value')




def del_all_vertices_from_object(obj):
        if obj.mode == 'OBJECT':
            bm = bmesh.new()
            bm.from_mesh(obj.data)
        else:
            bm = bmesh.from_edit_mesh(obj.data)

        for vert in bm.verts:
            bm.verts.remove(vert)

        if obj.mode == 'OBJECT':
            bm.to_mesh(obj.data)
            bm.free()
        else:
            bmesh.update_edit_mesh(obj.data)


# utils funcs
def select_object_solo(obj):

    for o in bpy.context.scene.objects:
        o.select_set(False)

    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def append_node_group_from_blend_file(blend_filepath, target, forceImport=False):
    
    # test if target node group already exists in scene
    if bpy.data.node_groups.get(target) and not forceImport:
        return
    
    # import using bpy.data.libraries.load()
    # doc link : https://docs.blender.org/api/current/bpy.types.BlendDataLibraries.html#bpy.types.BlendDataLibraries.load
    try:
        with bpy.data.libraries.load(blend_filepath, link=False) as (data_from, data_to):
            data_to.node_groups = [target]

        return data_to.node_groups[0]
    
    except Exception as e:
        print(e)
        return


def del_all_vertices_in_obj(obj):
    bpy.ops.object.mode_set(mode='EDIT')

    me = obj.data
    bm = bmesh.from_edit_mesh(me)    

    verts = [v for v in bm.verts]
    
    bmesh.ops.delete(bm, geom=verts)
    bmesh.update_edit_mesh(me)
    
    bpy.ops.object.mode_set(mode='OBJECT')

def create_new_object(name='dummy', me=None):
    if not me:
        me = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)

    return obj

def update_all_viewports():
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()

def set_view_top():

    area_type = 'VIEW_3D'
    areas  = [area for area in bpy.context.window.screen.areas if area.type == area_type]

    with bpy.context.temp_override(
        window=bpy.context.window,
        area=areas[0],
        region=[region for region in areas[0].regions if region.type == 'WINDOW'][0],
        screen=bpy.context.window.screen
    ):
        bpy.ops.view3d.view_axis(type='TOP')
        bpy.ops.view3d.view_selected(use_all_regions=False)




# maths funcs
def get_bound_box_min_from_obj(obj):
    min_x = min([corner[0] for corner in obj.bound_box])
    min_y = min([corner[1] for corner in obj.bound_box])
    min_z = min([corner[2] for corner in obj.bound_box])

    return [min_x, min_y, min_z]

def get_bound_box_max_from_obj(obj):
    max_x = max([corner[0] for corner in obj.bound_box])
    max_y = max([corner[1] for corner in obj.bound_box])
    max_z = max([corner[2] for corner in obj.bound_box])

    return [max_x, max_y, max_z]




# UI funcs
# def alert(text = "", title = "Message Box", icon = 'INFO'):

#     print('- ALERT -', text)

#     def draw(self, context):
#         self.layout.label(text=text)

#     bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def update_geonode_value_from_property(self, prop_name):

    obj = self.id_data
    modifier = get_sgf_modifier(obj)
    value = obj.sgf_settings[prop_name]

    set_geonode_value(modifier, prop_name, value)

def display_ascii_board(layout, sgf_path, board_size):
    try:
        ascii_board = get_ascii_board_from_sgf_file(sgf_path)
    except:
        box = layout.box()
        box.alert = True
        box.label(text='Unable to generate .sgf preview', icon='ERROR')

        return

    if not ascii_board:
        return

    board_array = [char for char in ascii_board if char in ['.', 'o', '#']]
    
    lines_array = []
    line = []
    
    for i, char in enumerate(board_array):
        line.append(char)
        
        if len(line) == board_size:
            lines_array.append(line)
            line = []

    offset_array = ['-', '-', '-'] if board_size == 13 else ['-', '-', '-', '-', '-'] if board_size == 9 else []

    if board_size < 19:
        for i, line in enumerate(lines_array):
            lines_array[i] = offset_array + line + offset_array

        offset = int((19 - board_size)/2)
        blank_line = ['-' for i in range (0,board_size)]
        

        for i in range (0, offset):
            lines_array.insert(0, blank_line)
            lines_array.append(['-' for i in range (0, offset)])

    # build board preview
    box = layout.box()
    
    col = box.column(align=True)
    col.scale_x = 1
    col.scale_x = 0.55
    col.scale_y = 0.6

    grid_icon = preview_collections['sgf_icons']['grid_dot.png'].icon_id
    black_icon = preview_collections['sgf_icons']['stone_black.png'].icon_id
    white_icon = preview_collections['sgf_icons']['stone_white.png'].icon_id
    

    for line in lines_array:
        row = col.row(align=True)

        for char in line:
            if char == '-':
                row.label(text='', icon='BLANK1')
            if char == '.':
                row.label(text='', icon_value=grid_icon)
            elif char == '#':
                row.label(text='', icon_value=black_icon)
            elif char == 'o':
                row.label(text='', icon_value=white_icon)


    row = box.row()
    row.enabled = False

    row_L = row.row()
    row_L.alignment = 'LEFT'
    row_R = row.row()
    row_R.alignment = 'RIGHT'

    row_L.label(text='Board Preview')
    row_R.label(text=f'{board_size}x{board_size}')




# SGF funcs

def add_new_sgf_object(self, context):
    
    addon_path = os.path.dirname(__file__)
    asset_filename = 'sgf_importer_assets_b3.2.0.blend'
    asset_filePath = os.path.join(addon_path, 'blend_assets', asset_filename)

    append_node_group_from_blend_file(asset_filePath, 'procedural_goban')

    obj = create_new_object('sgf_object')
    
    mod = obj.modifiers.new("SGF_geonodes", 'NODES')
    mod.node_group = bpy.data.node_groups['procedural_goban']

    return obj

def get_sgf_modifier(obj):
    for m in obj.modifiers:
        if m.type == 'NODES':
            if m.node_group.name == 'procedural_goban':
                return m



def read_src_from_sgf_file(sgf_path):
    f = open(sgf_path, "rb")
    sgf_src = f.read()    
    f.close()

    return sgf_src

def get_sgf_game_from_file(sgf_path):
    sgf_src = read_src_from_sgf_file(sgf_path)
    sgf_game = sgf.Sgf_game.from_bytes(sgf_src)

    return sgf_game



def get_metadata_from_sgf_file(sgf_path, prefix, fail_value='unkown'):

    sgf_game = get_sgf_game_from_file(sgf_path)
    charset = sgf_game.get_charset()

    sgf_src = str(read_src_from_sgf_file(sgf_path).decode(charset))

    # will search for a string that's between '[]'
    # and preceeded by the given prefix

    try:
        result = sgf_src.split(prefix+'[')[1].split(']')[0]
        return result
    except Exception as e:
        return fail_value

def load_game_metadata(obj, sgf_path):

    # set geonodes values
    modifier = get_sgf_modifier(obj)
    

    set_geonode_value(modifier, 'sgf_filepath', sgf_path)
    set_geonode_value(modifier, 'board_name', os.path.basename(sgf_path))

    # set custom properties values
    obj.sgf_settings.sgf_filepath = sgf_path
    obj.sgf_settings.current_move = get_last_move_from_sgf_file(sgf_path)
    obj.sgf_settings.move_max = get_last_move_from_sgf_file(sgf_path)
    

    # get values from sgf_src
    obj.sgf_settings.PB = get_metadata_from_sgf_file(sgf_path, 'PB')
    obj.sgf_settings.PW = get_metadata_from_sgf_file(sgf_path, 'PW')
    obj.sgf_settings.PB_rank = get_metadata_from_sgf_file(sgf_path, 'BR', fail_value='?')
    obj.sgf_settings.PW_rank = get_metadata_from_sgf_file(sgf_path, 'WR', fail_value='?')

    obj.sgf_settings.board_size = get_board_size(sgf_path)
    
    obj.sgf_settings.game_name = get_metadata_from_sgf_file(sgf_path, 'GN', fail_value='no name found for this game')
    obj.sgf_settings.game_event = get_metadata_from_sgf_file(sgf_path, 'EV')
    obj.sgf_settings.game_app = get_metadata_from_sgf_file(sgf_path, 'AP')
    obj.sgf_settings.game_rules = get_metadata_from_sgf_file(sgf_path, 'RU')
    obj.sgf_settings.game_date = get_metadata_from_sgf_file(sgf_path, 'DT')
    obj.sgf_settings.game_komi = get_metadata_from_sgf_file(sgf_path, 'KM')
    obj.sgf_settings.game_handicap = get_metadata_from_sgf_file(sgf_path, 'HA', fail_value='None')
    obj.sgf_settings.game_result = get_metadata_from_sgf_file(sgf_path, 'RE')

    

    # dump sgf_src content
    # sgf_src = read_src_from_sgf_file(sgf_path)
    # print(sgf_src)



def get_ascii_board_from_sgf_file(sgf_path, move_number=None):
    _description = """\
    Show the position from an SGF file. If a move number is specified, the position
    before that move is shown (this is to match the behaviour of GTP loadsgf).
    """
    
    f = open(sgf_path, "rb")
    sgf_src = f.read()    
    f.close()
        
    try:
        sgf_game = sgf.Sgf_game.from_bytes(sgf_src)
    except ValueError:
        raise Exception("bad sgf file")

    try:
        board, plays = sgf_moves.get_setup_and_moves(sgf_game)
    except ValueError as e:
        # raise Exception(str(e))
        print('-ERR-', str(e))

    if move_number is not None:
        move_number = max(0, move_number)
        plays = plays[:move_number]
    else:
        moves = [n for n in sgf_game.get_main_sequence()]
        last_move = len(moves)
        move_number = last_move
        plays = plays[:move_number]
        
    for colour, move in plays:
        if move is None:
            continue
        row, col = move
        try:
            board.play(row, col, colour)
        except ValueError:
            raise Exception("illegal move in sgf file")


    ascii_board = ascii_boards.render_board(board)
    
    
    return ascii_board

def get_board_size(sgf_path):
    try:
        return int(get_metadata_from_sgf_file(sgf_path, 'SZ'))
    except:
        print(f'-ERR- <{os.path.basename(sgf_path)}> failed to detect board size, default to 19x19')
        return 19

def get_last_move_from_sgf_file(sgf_path):
    sgf_game = get_sgf_game_from_file(sgf_path)

    move_max = len([node for node in sgf_game.get_main_sequence()])-1

    return move_max



def set_vertices_from_board_array(obj, board_array):

    modifier = get_sgf_modifier(obj)

    verts_array = []
    color_array = []

    board_size = get_geonode_value(modifier, 'board_size')

    for i, char in enumerate(board_array):
        if char in ['o', '#']:
            posX = (i%board_size)/(board_size-1)
            posY = (-(math.floor(i/board_size))+(board_size-1))/(board_size-1)
            posZ = 0.0
            
            color_value = 0.0 if char == 'o' else 1.0 if char =='#' else 0.5
            
            verts_array.append((posX, posY, posZ))
            color_array.append(color_value)            


    del_all_vertices_from_object(obj)

    mesh_data = obj.data
    mesh_data.from_pydata(verts_array, [], [])
    mesh_data.update()

    for vg in obj.vertex_groups:
        obj.vertex_groups.remove(vg)
        
    stone_color = obj.vertex_groups.new(name='stone_color')

    for i, color_value in enumerate(color_array):
        stone_color.add([i], color_value, 'ADD' )

def load_board_from_sgf_file(obj, sgf_path, move_number=None):

    # try to decode .sgf file
    try:
        ascii_board = get_ascii_board_from_sgf_file(sgf_path)
    except:
        print('-ERR- Error while decoding .sgf file')
        obj.sgf_settings.is_valid_sgf_file = False
        
        return

    # generate board mesh
    board_array = [char for char in ascii_board if char in ['.', 'o', '#']]
    set_vertices_from_board_array(obj, board_array)
    

    # load game metadata
    load_game_metadata(obj, sgf_path)

    # set board dimensions
    board_size = obj.sgf_settings.board_size
    line_spacing_x = 22.1
    line_spacing_y = 23.7

    obj.sgf_settings.board_width = line_spacing_x * (board_size-1)
    obj.sgf_settings.board_height = line_spacing_y * (board_size-1)

    # set object properties
    obj.sgf_settings.current_move = get_last_move_from_sgf_file(sgf_path)
    obj.sgf_settings.is_valid_sgf_file = True
    obj.sgf_settings.is_sgf_object = True

def update_board_from_move(self, context):

    obj = context.object
    modifier = get_sgf_modifier(obj)

    sgf_filepath = modifier["Socket_11"]
    current_move = obj.sgf_settings.current_move

    ascii_board = get_ascii_board_from_sgf_file(sgf_filepath, current_move)
    board_array = [char for char in ascii_board if char in ['.', 'o', '#']]

    if current_move <= 0:
        del_all_vertices_from_object(obj)
        return


    set_vertices_from_board_array(obj, board_array)





# Export to SVG funcs
def get_svg_filepath_for_multiple_export():

    modifier = get_sgf_modifier(bpy.context.object)
    board_name = get_geonode_value(modifier, 'board_name')

    if board_name == '':
        board_name = 'temp'

    scn_filepath = bpy.context.scene.sgf_settings.last_used_filepath

    svg_filepath = os.path.join(scn_filepath, board_name)

    return svg_filepath

def get_svg_filepath_for_single_export_from_modifier(modifier, user_filepath=None):

    # get basename
    if user_filepath:
        basename = os.path.basename(user_filepath)
    else:
        basename = get_geonode_value(modifier, 'board_name')

    if os.path.splitext(basename)[1] in ['.svg', '.sgf']:
        basename = os.path.splitext(basename)[0]

    # add suffix for each visible element
    edge = '-edge' if get_geonode_value(modifier, 'show_edge') else ''
    grid_x = '-gridX' if get_geonode_value(modifier, 'show_grid_x') else ''
    grid_y = '-gridY' if get_geonode_value(modifier, 'show_grid_y') else ''
    hoshis = '-hoshis' if get_geonode_value(modifier, 'show_hoshis') else ''
    black = '-black' if get_geonode_value(modifier, 'show_black_stones') else ''
    white = '-white' if get_geonode_value(modifier, 'show_white_stones') else ''

    for element in [edge, grid_x, grid_y, hoshis, black, white]:
        basename += element

    # add last_used_filepath
    scn_filepath = bpy.context.scene.sgf_settings.last_used_filepath
    svg_filepath = os.path.join(scn_filepath, basename + '.svg')

    return svg_filepath

def solo_layer_on_sgf_object(obj, sgf_layers, target_layer):

    modifier = get_sgf_modifier(obj)

    for layer in sgf_layers:
        set_geonode_value(
            modifier=modifier, 
            input_name=layer[0], 
            value=True if layer[0] == target_layer[0] else False
        )

def export_multiple_to_svg(obj, svg_filepath):
    scn = bpy.context.scene
    modifier = get_sgf_modifier(obj)

    sgf_layers = [
            ['show_edge',  scn.sgf_settings.export_edge],
            ['show_grid_x', scn.sgf_settings.export_grid_x],
            ['show_grid_y', scn.sgf_settings.export_grid_y],
            ['show_hoshis', scn.sgf_settings.export_hoshis],
            ['show_black_stones', scn.sgf_settings.export_black_stones],
            ['show_white_stones', scn.sgf_settings.export_white_stones],
        ]

    for layer in sgf_layers:
        if layer[1] == True:

            print(f'exporting layer {layer[0]}')

            solo_layer_on_sgf_object(obj, sgf_layers, layer)
            svg_filepath = get_svg_filepath_for_single_export_from_modifier(modifier, user_filepath=svg_filepath)
            
            export_to_svg(obj, svg_filepath)

    for layer in sgf_layers:
        print(layer[1])

        set_geonode_value(
            modifier=modifier, 
            input_name=layer[0], 
            value=layer[1]
        )

    # toggle editmode to force GN update
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')

def export_to_svg(obj, filepath):

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

    export_cam = create_export_cam_above_object(obj)

    bpy.data.scenes["Scene"].render.resolution_x = 1080
    bpy.data.scenes["Scene"].render.resolution_y = 1080

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].region_3d.view_perspective = 'CAMERA'
            area.spaces[0].use_local_camera = True
            area.spaces[0].camera = export_cam


    export_single_object_to_svg(obj, filepath)

    # restore all to previous state

    bpy.data.scenes["Scene"].render.resolution_x = resolution_x
    bpy.data.scenes["Scene"].render.resolution_y = resolution_y

    for area in areas_view_modes:
        area_object = area[0]

        area_object.spaces[0].region_3d.view_perspective = 'PERSP'
        # area_object.spaces[0].region_3d.view_perspective = area[1]
        area_object.spaces[0].use_local_camera = area[2]
        area_object.spaces[0].camera = area[3]

    select_object_solo(export_cam)
    bpy.ops.object.delete()

    select_object_solo(obj)

    bpy.context.scene.sgf_settings.last_used_filepath = os.path.dirname(filepath)


def export_single_object_to_svg(obj, svg_filepath):
    
    # select object solo and duplicate
    select_object_solo(obj)

    obj_x = -1 - get_bound_box_min_from_obj(obj)[1]
    obj_y = 1 - get_bound_box_max_from_obj(obj)[1]

    bpy.ops.object.duplicate()
    bpy.context.object.location = (0, 0, 0)
    bpy.context.object.rotation_euler = (0, 0, 0)
    bpy.context.object.scale = (1, 1, 1)

    # set geonode values based on scene export values
    scn = bpy.context.scene
    duplicate_modifier = get_sgf_modifier(bpy.context.object)

    set_geonode_value(duplicate_modifier, 'stone_display', 0)
    set_geonode_value(duplicate_modifier, 'show_board_name', False)
    set_geonode_value(duplicate_modifier, 'show_bounds_cross', True)

    # apply modifier
    bpy.ops.object.modifier_apply(modifier=duplicate_modifier.name)

    # convert to gpencil
    bpy.ops.object.convert(target='CURVE')
    bpy.context.object.data.dimensions = '2D'
    bpy.ops.object.convert(target='GPENCIL')

    set_line_thickness_on_gp_object(bpy.context.object, 0.05)

    # export to svg
    bpy.ops.wm.gpencil_export_svg(filepath=svg_filepath)

    # delete duplicate and select back original object
    bpy.ops.object.delete()
    select_object_solo(obj)

def set_line_thickness_on_gp_object(gp_obj, thickness):
    for gpl in gp_obj.data.layers:
        gpf = gpl.active_frame
        # Loop all strokes in active frame
        for gps in gpf.strokes:
            # You can set the stroke width here to your liking
            gps.line_width = 1
            # Loop all points in stroke
            for p in gps.points:
                # Adjust thickness of this point,
                # by setting the pressure to the default 1.0.
                p.pressure = thickness

def create_export_cam_above_object(obj):
    dim_x = obj.dimensions[0]
    dim_y = obj.dimensions[1]

    min_x = get_bound_box_min_from_obj(obj)[0]
    min_y = get_bound_box_min_from_obj(obj)[1]

    cam_x = min_x + (dim_x/2)
    cam_y = min_y + (dim_y/2)
    cam_z = max(dim_x, dim_y)

    camera_data = bpy.data.cameras.new(name='Camera')
    camera_object = bpy.data.objects.new('Camera', camera_data)
    bpy.context.scene.collection.objects.link(camera_object)

    camera_object.location = (cam_x, cam_y, cam_z)

    # camera_data.type = 'ORTHO'
    # camera_data.ortho_scale = cam_z

    return camera_object




