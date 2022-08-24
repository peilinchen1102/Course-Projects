#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

from tabnanny import check
from turtle import update
import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION
def check_bomb(board, r, c):
    """
    Check to see if location (r,c) on the board has a bomb

    Returns true if bomb exists and false otherwise

    Parameters:
        board (2d array): list of list representation of game 
        r (int): row index
        c (int): column index
        num_rows (int): row dimension of board
        num_cols (int): col dimension of board
    """
    num_rows = len(board)
    num_cols = len(board[0])

    if 0 <= r < num_rows and 0 <= c < num_cols:
            # if neighbor is a bomb
            if board[r][c] == '.':
                return True
    return False

def calc_bomb(board, r, c):
    """
    Calculate the number of bombs in neighbors of (r,c)

    Returns the number of bombs found

    Parameters:
        board (2d array): list of list representation of game 
        r (int): row index
        c (int): column index
        num_rows (int): row dimension of board
        num_cols (int): col dimension of board
    """
    neighbor_bombs = 0
    neighbors = {(r-1,c-1), (r,c-1), (r+1,c-1), (r-1,c), (r+1,c), (r-1,c+1), (r,c+1),(r+1,c+1)}
    

    # loop through all 8 neighboring squares
    for r, c in neighbors:
        # if index is valid
        if check_bomb(board, r, c):
            neighbor_bombs+=1
    return neighbor_bombs

def calc_revealed(game, r, c):
    """
    Calculate the number of revealed squares recursively

    Returns the number of revealed squares

    Parameters:
        game (dict):  Game state
        r (int): row index
        c (int): column index
    """
    revealed = 0
    neighbors = {(r-1,c-1), (r,c-1), (r+1,c-1), (r-1,c), (r+1,c), (r-1,c+1), (r,c+1),(r+1,c+1)}
    num_rows = len(game['board'])
    num_cols = len(game['board'][0])

    # loop through all neighbors
    for r,c in neighbors:
        # if the index is valid
        if 0 <= r < num_rows and 0 <= c < num_cols:
            # check for not bombs that are not visible and reveal them
            if not check_bomb(game['board'], r, c) and game['visible'][r][c] == False:
                revealed += dig_2d(game, r, c)
    return revealed

def calc_covered_and_bombs(game):
    """
    Calculate the number of covered squares and the number of bombs in the game board

    Returns number of bombs and covered squares

    Parameters:
        game (dict): Game state
    """
    bombs = 0  # set number of bombs to 0
    covered_squares = 0
    for r in range(game['dimensions'][0]):
        # for each r,
        for c in range(game['dimensions'][1]):
            # for each c,
            if game['board'][r][c] == '.':
                if game['visible'][r][c] == True:
                    # if the game visible is True, and the board is '.', add 1 to
                    # bombs
                    bombs += 1
            elif game['visible'][r][c] == False:
                covered_squares += 1
    return (bombs, covered_squares)

def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    
    """
    # board = []
    # visible = []
    # board_0 = set()
    # # loop each row
    # for r in range(num_rows):
    #     row = []
    #     visible_row = []
    #     # loop col
    #     for c in range(num_cols):
    #         # if bomb add it to board
    #         if [r, c] in bombs or (r, c) in bombs:
    #             row.append('.')
    #         # else add a 0 and add the index of 0 to board_0
    #         else:
    #             row.append(0)
    #             board_0.add((r,c))
    #         # make everything not visible
    #         visible_row.append(False)
    #     visible.append(visible_row)
    #     board.append(row)
    
    # for r, c in board_0:
    #     if board[r][c] == 0:
    #         # calculate number for neighboring bombs
    #         board[r][c] = calc_bomb(board, r, c)
    
    # return {
    #     'dimensions': (num_rows, num_cols),
    #     'board': board,
    #     'visible': visible,
    #     'state': 'ongoing'}

    return new_game_nd((num_rows,num_cols), bombs)
def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['visible'][bomb_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """

    
    # if game['state'] == 'defeat' or game['state'] == 'victory':
    #  # keep the state the same
    #     return 0

    # if game['board'][row][col] == '.':
    #     game['visible'][row][col] = True
    #     game['state'] = 'defeat'
    #     return 1


    # if game['visible'][row][col] != True:
    #     game['visible'][row][col] = True
    #     revealed = 1
    # else:
    #     return 0

    # # # recursively find number of squares revealed by checking neighbors    
    # if game['board'][row][col] == 0:
    #     revealed += calc_revealed(game, row, col)
        

    # for r in range(game['dimensions'][0]):
    #     # for each r,
    #     for c in range(game['dimensions'][1]):
    #         # for each c,
           
    #         if game['visible'][r][c] == False and  game['board'][r][c] != '.': 
    #             game['state'] = 'ongoing'
    #             return revealed


   
    # game['state'] = 'victory'
    # return revealed
    
    return dig_nd(game, (row, col))
def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['visible'] indicates which squares should be visible.  If
    xray is True (the default is False), game['visible'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    
    """
    # # initialize an empty game
    # board = []
    # # loop each row of game board
    # for r in range(game['dimensions'][0]):
    #     # loop each game element
    #     row = []
    #     for element, visible in zip(game['board'][r], game['visible'][r]):
    #         key = element
    #         # replace element 0 with empty space
    #         if element == 0:
    #             key = " "
    #         # if xray is true then ignore visible
    #         if xray:
    #             row.append(str(key))
    #         # if visible add element, else hide it with "_"
    #         else:
    #             if visible:
    #                 row.append(str(key))
    #             else:
    #                 row.append("_")
    #     board.append(row)
    # return board
    return render_nd(game,xray)

def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    # initialize an empty str
    str_board = ""
    # print(game['board'], game['visible'])
    # loop each row of game board
    for r in range(len(game['board'])):
        # loop each game element
        for element, visible in zip(game['board'][r], game['visible'][r]):
            key = element
            # replace element 0 with empty str
            if element == 0:
                key = " "
            # if xray is true then ignore visible
            if xray:
                str_board += str(key)
            # if visible add element, else hide it with "_"
            else:
                if visible:
                    str_board += str(key)
                else:
                    str_board += "_"
        # add new line between each row except last row
        if r != len(game['board'])-1:
            str_board += "\n"
    # print(str_board)
    return str_board

# N-D IMPLEMENTATION



def build_nd_board(dimensions, value):
    """
    Returns a n dimension board with values at every spot

    Parameters:
        dimensions (tuple): dimension of the game
        value: any default input eg. 0, False

    >>> build_nd_board((2,3), 0)
    [[0, 0, 0], [0, 0, 0]]
    """
    # create a helper function
    def build_nd_board_helper(current_coordinate = tuple([0 for i in range(len(dimensions))]), level=0):
        # length of the row
        length = dimensions[level]
        
        if level == len(dimensions) - 1:
            board = []
            
            # loop through each index of the row
            for i in range(length):
                # previous levels plus the current row index
                coordinate = current_coordinate[:level] + (i, ) + current_coordinate[level + 2:]

                current_value = value
                
                # if value is callable set current value to it
                if callable(value):
                    current_value = value(coordinate)
                
                # add the value to the board
                board.append(current_value)
            
            return board
            
        board = []
        for i in range(length):
            new_coordinate = current_coordinate[:level] + (i, ) + current_coordinate[level + 2:]
            # recursive step for building the board
            board.append(build_nd_board_helper(new_coordinate, level + 1))

        return board

    return build_nd_board_helper()


def update_values(board, coordinate, value):
    """
    Update the value at the coordinate location

    Returns a board with updated value

    Parameters:
        board (list of lists): game representation
        coordinate (tuple): location on game board
        value: the value to update

    Returns:
        A game board

    >>> update_values([[0,0], [0,0]], (1,0), '.')
    [[0, 0], ['.', 0]]
    """
    # base case if dimension is just one
    if len(coordinate) == 1:
        board[coordinate[0]] = value
        
    else:
        # recursively index to the value
        update_values(board[coordinate[0]], coordinate[1:], value)
    
    return board

def nd_all_coord(dimensions):
    """
    Returns all possible coordinates in a game board

    Parameters:
        dimensions (tuple): dimensions of the game board

    >>> nd_all_coord((2,2)) == {(0, 0), (0, 1), (1, 0), (1, 1)}
    True
    >>> nd_all_coord((2,2,2)) == {(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0), (0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 1)}
    True
    """
    result= set()

    # base case 
    if len(dimensions) == 1:
        neighbors = set()
        # for adding location elements from 0 to dimension [0]
        for i in range(dimensions[0]):
            neighbors.add((0+i,))
        return neighbors
    else:
        # recursively go to next dimension
        neighbors = nd_all_coord(dimensions[1:])
        # loop through again and add the neighbors
        for neighbor in neighbors:
            for i in range(dimensions[0]):
                result.add((0+i,)+neighbor)
    return result

def nd_neighbors(dimensions, coordinate):
    """
    Find all neighbors of the coordinate

    Returns the set of neighbors

    Parameters:
        dimensions (tuple): dimension of the game board
        board (list of lists): representation of the game
        coordinate (tuple): the location 
    
    >>> nd_neighbors((10,20),(5,13)) == {(4, 12), (4, 13), (4, 14), (5, 12), (5, 13), (5, 14), (6, 12), (6, 13), (6, 14)}
    True
    """

    result= set()
    # base case
    if len(coordinate) == 1:
        neighbors = set()
        # find neighbor one less and one more
        for i in [-1,0, 1]:
            if 0 <= coordinate[0]+i < dimensions[0]:
                neighbors.add((coordinate[0]+i,))
        return neighbors
    else:
        # recursively find neighbors for each dimension
        neighbors = nd_neighbors(dimensions[1:], coordinate[1:])
        for neighbor in neighbors:
            for i in [-1,0, 1]:
                # condition checking if neighbor is within the index
                if 0 <= coordinate[0]+i < dimensions[0]:
                    result.add((coordinate[0]+i,)+neighbor)
    return result

def nd_check_bomb(board, coord, value):
    """
    Check if there's a value at location coord equal to value

    Returns a boolean value to see if values are equal

    Parameters:
        board (list of lists): a game representation 
        coord (tuple): the location
        value: any value eg, str, boolean
    >>> nd_check_bomb([[2,'.'], [1,0], [1,0]], (0,1), '.' )
    True

    >>> nd_check_bomb([[True, False], [True,False], [False,False]], (0,1), False)
    True

    >>> nd_check_bomb([[True, False], [True,False], [False,False]], (0,1), True)
    False

    >>> nd_check_bomb([[[0, 0], [1, 1], [1, 1]], [[0, 0], [1, 1], ['.', 1]], [[0, 0], [1, 1], [1, 1]]], (1,2,0), '.')
    True
    """
    # base case check bomb
    if len(coord) == 1:
        if board[coord[0]] == value:
            return True
      
    else:
        return nd_check_bomb(board[coord[0]], coord[1:], value)
    return False
# def nd_calc_covered_and_bombs(game):
#     dimensions = game['dimensions']
#     board = game['board']
    
#     if len(dimensions) == 1:
#         board[coordinate[0]] = value
        
#     else:
#         update_values(board[coordinate[0]], coordinate[1:], value)
    
#     return board

def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    # build empty board
    visible = build_nd_board(dimensions, False)

    bombs_set =  set(bombs)

    def fill_tile(coordinate):
        if coordinate in bombs:
            return "."

        # find the intersection between neighbors and bombs to find all neighboring bombs
        # eliminate a for loop, very fast
        neighbor_bombs = len(bombs_set & nd_neighbors(dimensions, coordinate))
        
        
        return neighbor_bombs
    # call fill tile function to build the empty board with bombs inside
    board = build_nd_board(dimensions, fill_tile)
    
    return {'board': board, 'dimensions': dimensions, 'state': 'ongoing', 'visible': visible}



def dig_nd(game, coordinates, all_coord = None):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed
    >>> g = {'dimensions': (6,6), 
    ...         'board':   [[0, 0, 1, 1, 2, '.'], 
    ...                     [0, 0, 2, '.', 3, 1], 
    ...                     [1, 1, 2, '.', 2, 0], 
    ...                     ['.', 1, 1, 1, 1, 0], 
    ...                     [1, 1, 0, 0, 0, 0], 
    ...                     [0, 0, 0, 0, 0, 0]],
    ...         'visible':  [[True, True, True, False, False, False],
    ...                     [True, True, True, False, False, False],
    ...                     [True, True, True, False, False, False],
    ...                     [False, False, False, False, False, False],
    ...                     [False, False, False, False, False, False],
    ...                     [False, False, False, False, False, False]],
    ...         'state': 'ongoing' }
    >>> dig_nd(g, (5,4))
    21
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_nd(game, (0,3))
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    """

    dimensions = game['dimensions']
    board = game['board']
    visible = game['visible']
    if all_coord == None:
        all_coord = nd_all_coord(dimensions)
            


    dimensions = game['dimensions']
    board = game['board']
    visible = game['visible']
    if game['state'] == 'defeat' or game['state'] == 'victory':
    # keep the state the same
        return 0

    
    # if bomb is revealed return defeat
    if nd_check_bomb(board, coordinates, '.'):
        update_values(visible, coordinates, True)
        game['state'] = 'defeat'
        return 1
        
    # recursive helper function
    def dig_nd_rec(game, coordinates, all_coord = None, bombs = None):
        
        
        # if value visible return same
        if not nd_check_bomb(visible, coordinates, False):
            return 0
        # if value not visible then update to make it visible
        else:
            update_values(visible, coordinates, True)
            revealed = 1
            
        

        # recursive step to check all revealed
        if nd_get_val(board, coordinates) == 0:
            neighbors = nd_neighbors(dimensions, coordinates)
            # for each neighbor, check and update recursively
            for neighbor in neighbors:
                revealed += dig_nd_rec(game, neighbor, all_coord)

        return revealed

    # call helper function to return revealed
    revealed = dig_nd_rec(game, coordinates, all_coord)

    # loop through all coords to check game state
    for coord in all_coord:
        if nd_check_bomb(visible, coord, False) and not nd_check_bomb(board, coord, '.'):
            game['state'] = 'ongoing'
            return revealed


    # else, game state is victory
    game['state'] = 'victory'
    return revealed



    
def nd_get_val(board, coord):
    """
    Returns the value of the board at a given coordinate

    Parameters:
        board (list of lists): nd array representation of a game
        coord (tuple): location on the board
    """
    if len(coord) == 1:
        return board[coord[0]]
      
    else:
        return nd_get_val(board[coord[0]], coord[1:])

def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['visible'] array indicates which squares should be
    visible.  If xray is True (the default is False), the game['visible'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    dimensions = game['dimensions']
    board = game['board']
    visible = game['visible']

    # create an empty nd array
    result = build_nd_board(dimensions, 0)
    # find all coordinates in the dimension
    all_coord = nd_all_coord(dimensions)

    # loop through all coordinates in the board
    for coord in all_coord:
        # retrieve the value at each coordinate
        key = nd_get_val(board, coord)
        # if the value is 0 change it to empty str
        if key == 0:
            key = ' '
        # ignore visible and display everything
        if xray:
            update_values(result, coord, str(key))
        # check to see if visible and return accordingly
        else:
            if nd_check_bomb(visible, coord, True):
                update_values(result, coord, str(key))
            else:
                update_values(result, coord, '_')
    return result


    

if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    
    render_2d_board({'dimensions': (2, 4),
                      'state': 'ongoing',
                      'board': [['.', 3, 1, 0],
                                ['.', '.', 1, 0]],
                      'visible':  [[True, True, True, False],
                                [False, False, True, False]]}, False)

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
