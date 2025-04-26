import bpy
import bmesh
from pathlib import Path
import math

from sgfmill import sgf
from sgfmill import sgf_moves
from sgfmill import boards
from sgfmill import ascii_boards

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
            invert_checkbox=invert_checkbox
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
    
    
def add_vertices_from_sgf_file(obj, sgf_path, move_number=None):
    bpy.ops.object.mode_set(mode='EDIT')
    obj.modifiers["GeometryNodes"].show_viewport = False

    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    
    for vg in obj.vertex_groups:
        obj.vertex_groups.remove(vg)
        
    stone_color = obj.vertex_groups.new(name='stone_color')

    ascii_board = get_ascii_board_from_sgf_file(sgf_path, move_number)
    board_array = [char for char in ascii_board if char in ['.', 'o', '#']]

    
    i = 0
    
    for c in board_array:
        if c in ['o', '#']:
            posX = (i%19)/18
            posY = (-(math.floor(i/19))+18)/18
            posZ = 0.0
            
            color_value = 0.0 if c == 'o' else 1.0 if c =='#' else 0.5
            
            bpy.ops.object.mode_set(mode='EDIT')
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            vert = bm.verts.new((posX, posY, posZ))  # add a new vert
            vcount = len(me.vertices)
            
            bpy.ops.object.mode_set(mode='OBJECT')
            stone_color.add([vcount], color_value, 'ADD' )
            
        i += 1

                
    obj.modifiers["GeometryNodes"].show_viewport = True

       
    
    
