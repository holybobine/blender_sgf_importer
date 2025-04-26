import bpy
import bmesh
from pathlib import Path
import math
import os

from sgfmill import sgf
from sgfmill import sgf_moves
from sgfmill import boards
from sgfmill import ascii_boards

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


def totuple(a):
    try:
        return tuple(totuple(i) for i in a)
    except TypeError:
        return a

def alert(text = "", title = "Message Box", icon = 'INFO'):

    print('- ALERT -', text)

    def draw(self, context):
        self.layout.label(text=text)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def get_sgf_modifier(obj):
    for m in obj.modifiers:
        if m.type == 'NODES':
            if m.node_group.name == 'procedural_goban':
                return m

def draw_prop_geonode(context, gn_modifier, input_name, label_name='', enabled=True, label=True, icon='NONE', toggle=-1, invert_checkbox=False):

    # input_id = next(i.identifier for i in gn_modifier.node_group.inputs if i.name == input_name)                  # 3.6
    input_id = next(i.identifier for i in gn_modifier.node_group.interface.items_tree if i.name == input_name)      # 4.0

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


_description = """\
Show the position from an SGF file. If a move number is specified, the position
before that move is shown (this is to match the behaviour of GTP loadsgf).
"""

def get_ascii_board_from_sgf_file(pathname, move_number=None):
    
    f = open(pathname, "rb")
    sgf_src = f.read()    
    f.close()
        
    try:
        sgf_game = sgf.Sgf_game.from_bytes(sgf_src)
    except ValueError:
        raise Exception("bad sgf file")

    try:
        board, plays = sgf_moves.get_setup_and_moves(sgf_game)
    except ValueError as e:
        raise Exception(str(e))
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

def del_all_vertices_in_obj(obj):
    bpy.ops.object.mode_set(mode='EDIT')

    me = obj.data
    bm = bmesh.from_edit_mesh(me)    

    verts = [v for v in bm.verts]
    
    bmesh.ops.delete(bm, geom=verts)
    bmesh.update_edit_mesh(me)
    
    bpy.ops.object.mode_set(mode='OBJECT')

def set_vertices_from_board_array(obj, board_array):

    verts_array = []
    color_array = []

    for i, char in enumerate(board_array):
        if char in ['o', '#']:
            posX = (i%19)/18
            posY = (-(math.floor(i/19))+18)/18
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
    

    ascii_board = get_ascii_board_from_sgf_file(sgf_path)
    board_array = [char for char in ascii_board if char in ['.', 'o', '#']]

    f = open(sgf_path, "rb")
    sgf_src = f.read()    
    f.close()

    game = sgf.Sgf_game.from_bytes(sgf_src)
    move_max = len([node for node in game.get_main_sequence()])

    obj.sgf_settings.current_move = move_max
    obj.sgf_settings.move_max = move_max

    modifier = get_sgf_modifier(obj)
    modifier["Socket_11"] = sgf_path
    modifier["Socket_16"] = os.path.basename(sgf_path)

    set_vertices_from_board_array(obj, board_array)
    


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

    if current_move != obj.sgf_settings.move_max:
        set_vertices_from_board_array(obj, board_array)

def update_board_size(self, context):
    obj = context.object
    modifier = get_sgf_modifier(obj)

    width = obj.sgf_settings.board_width
    height = obj.sgf_settings.board_height

    modifier["Socket_13"] = width
    modifier["Socket_14"] = height

    obj.sgf_settings.spacing_x = (width/19)*10
    obj.sgf_settings.spacing_y = (height/19)*10
