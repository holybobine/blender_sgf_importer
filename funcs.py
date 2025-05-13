import bpy
import bmesh

import os
import math

from .sgfmill import sgf
from .sgfmill import sgf_moves
from .sgfmill import ascii_boards


def get_geonode_inputs_from_modifier(modifier):
    if bpy.app.version < (4, 0, 0):
        inputs = modifier.node_group.inputs
    elif bpy.app.version >= (4, 0, 0):
        inputs = modifier.node_group.interface.items_tree

    return inputs

# geonodes funcs
def set_geonode_value_proper(modifier, input_name, value):
    for i in get_geonode_inputs_from_modifier(modifier):
        if i.name == input_name:

            input_type = type(i.default_value).__name__
            value_type = type(value).__name__

            if input_type == value_type:
                modifier[i.identifier] = value
                i.default_value = i.default_value

def get_geonode_value_proper(modifier, input_name):
    for i in get_geonode_inputs_from_modifier(modifier):
        if i.name == input_name:
            return modifier[i.identifier]

def reset_geonode_value(modifier, input_name):
    for i in get_geonode_inputs_from_modifier(modifier):
        if i.name == input_name:
            modifier[i.identifier] = i.default_value
            i.default_value = i.default_value

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

def append_from_blend_file(blendfile, section, target, forceImport=False):

    obj_selection = bpy.context.selected_objects
    obj_active = bpy.context.object

    doAppend = True
    result = True

    dataSet = ''

    #choose correct data set from section name
    if section == 'Object':
        dataSet = bpy.data.objects
    elif section == 'Material':
        dataSet = bpy.data.materials
    elif section == 'NodeTree':
        dataSet = bpy.data.node_groups

    alreadyExist = dataSet.get(target)

    if alreadyExist and not forceImport:
        # print('-INF- '+section+' "'+target+'" already in scene, skipping import.')
        pass
    else:
        #append command, with added backslashes to fit python filepath formating

        new_datablock = None

        old_set = set(dataSet[:])

        result = bpy.ops.wm.append(
                                    filepath=blendfile + "\\"+section+"\\" + target,
                                    directory=blendfile + "\\"+section+"\\",
                                    filename=target
                                )

        new_set = set(dataSet[:]) - old_set

        new_datablock = list(new_set)[0]

        if new_datablock == None:
            print('-ERR- Failed importing '+section+' "'+target+'" from "'+blendfile+'"')
            result = False
        else:
            # print(f'-INF- successfully imported {new_datablock}')
            result = new_datablock

        # bpy.ops.object.select_all(action='DESELECT')

        for o in bpy.data.objects:
            o.select_set(False)

        for o in obj_selection:
            o.select_set(True)

        bpy.context.view_layer.objects.active = obj_active

        for lib in bpy.data.libraries:
            if lib.name == os.path.basename(blendfile):
                # print(f'-INF- removing lib {lib}')
                bpy.data.batch_remove(ids=(lib,))

        return result

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
def alert(text = "", title = "Message Box", icon = 'INFO'):

    print('- ALERT -', text)

    def draw(self, context):
        self.layout.label(text=text)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def update_geonode_value_from_property(self, prop_name):

    obj = self.id_data
    modifier = get_sgf_modifier(obj)
    value = obj.sgf_settings[prop_name]

    # convert property value to boolean if gn value is of boolean type
    gn_value = get_geonode_value_proper(modifier, prop_name)
    gn_value_type = type(gn_value).__name__

    if gn_value_type == 'bool':
        value = bool(value)
    elif gn_value_type == 'float':
        value = float(value)
    elif gn_value_type == 'int':
        value = int(value)

    set_geonode_value_proper(modifier, prop_name, value)

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
    col.scale_x = 0.55
    col.scale_y = 0.6

    for line in lines_array:
        row = col.row(align=True)

        for char in line:
            if char == '-':
                row.label(text='', icon='BLANK1')
            if char == '.':
                row.label(text='', icon='DOT')
            elif char == '#':
                row.label(text='', icon='HOLDOUT_OFF')
            elif char == 'o':
                row.label(text='', icon='RADIOBUT_ON')


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
    # asset_filename = 'sgf_importer_assets_b4.2.blend'
    asset_filename = 'sgf_importer_assets_b3.2.0.blend'
    asset_filePath = os.path.join(addon_path, 'blend_assets', asset_filename)

    append_from_blend_file(asset_filePath, 'NodeTree', 'procedural_goban', forceImport=False)

    obj = create_new_object('sgf_object')
    
    mod = obj.modifiers.new("SGF_geonodes", 'NODES')
    # mod.node_group = bpy.data.node_groups['procedural_goban'].copy()
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
    set_geonode_value_proper(modifier, 'sgf_filepath', sgf_path)
    set_geonode_value_proper(modifier, 'board_name', os.path.basename(sgf_path))

    

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

    board_size = get_geonode_value_proper(modifier, 'board_size')

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
    board_name = get_geonode_value_proper(modifier, 'board_name')

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
        basename = get_geonode_value_proper(modifier, 'board_name')

    if os.path.splitext(basename)[1] in ['.svg', '.sgf']:
        basename = os.path.splitext(basename)[0]

    # add suffix for each visible element
    edge = '-edge' if get_geonode_value_proper(modifier, 'show_edge') else ''
    grid_x = '-gridX' if get_geonode_value_proper(modifier, 'show_grid_x') else ''
    grid_y = '-gridY' if get_geonode_value_proper(modifier, 'show_grid_y') else ''
    hoshis = '-hoshis' if get_geonode_value_proper(modifier, 'show_hoshis') else ''
    black = '-black' if get_geonode_value_proper(modifier, 'show_black_stones') else ''
    white = '-white' if get_geonode_value_proper(modifier, 'show_white_stones') else ''

    for element in [edge, grid_x, grid_y, hoshis, black, white]:
        basename += element

    # add last_used_filepath
    scn_filepath = bpy.context.scene.sgf_settings.last_used_filepath
    svg_filepath = os.path.join(scn_filepath, basename + '.svg')

    return svg_filepath

def export_to_svg_ops(obj, svg_filepath):
    
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

    # set_geonode_value_proper(duplicate_modifier, 'show_edge', obj.sgf_settings.show_edge)
    # set_geonode_value_proper(duplicate_modifier, 'show_grid_x', obj.sgf_settings.show_grid_x)
    # set_geonode_value_proper(duplicate_modifier, 'show_grid_y', obj.sgf_settings.show_grid_y)
    # set_geonode_value_proper(duplicate_modifier, 'show_hoshis', obj.sgf_settings.show_hoshis)
    # set_geonode_value_proper(duplicate_modifier, 'show_black_stones', obj.sgf_settings.show_black_stones)
    # set_geonode_value_proper(duplicate_modifier, 'show_white_stones', obj.sgf_settings.show_white_stones)
    set_geonode_value_proper(duplicate_modifier, 'stone_display', 0)
    set_geonode_value_proper(duplicate_modifier, 'show_bounds_cross', True)

    # apply modifier
    bpy.ops.object.modifier_apply(modifier=duplicate_modifier.name)

    # convert to gpencil
    bpy.ops.object.convert(target='CURVE')
    bpy.context.object.data.dimensions = '2D'
    bpy.ops.object.convert(target='GPENCIL')

    set_line_thickness_on_gp_object(bpy.context.object, 0.05)

    # bpy.ops.object.mode_set(mode = 'EDIT_GPENCIL')
    # bpy.ops.object.mode_set(mode = 'OBJECT')

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




