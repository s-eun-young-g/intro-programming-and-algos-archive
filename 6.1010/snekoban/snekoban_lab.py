"""
6.1010 Lab:
Snekoban Game
"""

# import json # optional import for loading test_levels
# import typing # optional import
# import pprint # optional import

# NO ADDITIONAL IMPORTS!


DIRECTION_VECTOR = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def make_new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    This function takes in the above representation and returns a dictionary
    with different elements in the game (player, targets, walls, computers) as keys
    and sets of tuples of their coordinates (stored as (j, i)) as values.
    """
    # obtaining height and width of board
    board_height = len(level_description)
    board_width = len(level_description[0])

    # initialzing dictionary to store new representation
    new_game = {
        "player": None,
        "computers": set(),
        "targets": set(),
        "walls": set(),
        "height": board_height,
        "width": board_width,
    }

    # iterating through each item in initial representation
    for j, row in enumerate(level_description):
        for i, tile in enumerate(row):
            for element in tile:
                if element == "player":
                    new_game["player"] = (j, i)
                elif element == "computer":
                    new_game["computers"].add((j, i))
                elif element == "target":
                    new_game["targets"].add((j, i))
                elif element == "wall":
                    new_game["walls"].add((j, i))

    return new_game


def victory_check(game):
    """
    Given a game representation (of the form returned from make_new_game),
    return a Boolean: True if the given game satisfies the victory condition,
    and False otherwise.

    Victory condition: every target is covered with a computer — every square containing
    a target also contains a computer
    """

    targets = game["targets"]
    computers = game["computers"]

    # game is unwinnable if there are no targets
    if len(targets) == 0:
        return False

    # inclusion test - check if all targets are covered by computers
    return targets <= computers


def step_game(game, direction):
    """
    Given a game representation (of the form returned from make_new_game),
    return a game representation (of that same form), representing the
    updated game after running one step of the game.  The user's input is given
    by direction, which is one of the following:
        {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """

    # make copy as to not mutate input
    new_game = {
        "player": game["player"],
        "computers": game["computers"].copy(),
        "targets": game["targets"].copy(),
        "walls": game["walls"].copy(),
        "height": game["height"],
        "width": game["width"],
    }

    # getting direction change
    j_change, i_change = DIRECTION_VECTOR[direction]
    player_j, player_i = new_game["player"]
    new_player_coords = (player_j + j_change, player_i + i_change)

    # check if player move is legal
    if not player_move_valid(new_game, new_player_coords):
        return game

    # check if player is pushing computer
    if check_computer(new_game, new_player_coords):

        # check if computer will be pushed out of bounds
        if computer_move_valid(new_game, new_player_coords, direction):

            # move computer
            new_computer_coords = (
                new_player_coords[0] + j_change,
                new_player_coords[1] + i_change,
            )
            new_game["computers"].remove(new_player_coords)
            new_game["computers"].add(new_computer_coords)

        else:
            return game

    # move player
    new_game["player"] = new_player_coords

    return new_game


def dump_game(game):
    """
    Given a game representation (of the form returned from make_new_game),
    convert it back into a level description that would be a suitable input to
    make_new_game (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.

    Takes a game state in the format of a dictionary with elements as keys and their
    coordinates as tuples (j, i) as values and returns a list of lists, nested such that
    the first level lists represent rows and the lists within those lists represent
    the content of each tile in the row.
    """

    level_description = []

    # iterating through the game, add each element to correct place in
    # list of lists (level description)
    for j in range(game["height"]):
        row = []
        for i in range(game["width"]):
            tile = []
            coords = (j, i)
            if coords == game["player"]:
                tile.append("player")
            if coords in game["computers"]:
                tile.append("computer")
            if coords in game["targets"]:
                tile.append("target")
            if coords in game["walls"]:
                tile.append("wall")
            row.append(tile)
        level_description.append(row)

    return level_description


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from make_new_game), find
    a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """

    # initializing bfs agenda and visited
    agenda = [(game, [])]
    visited = set()
    visited.add(make_game_tuple(game))

    # test edge case (game is already won)
    if victory_check(game):
        return []

    # bfs
    while agenda:
        current_game, path = agenda.pop(0)

        # iterating through direction vector
        for direction in DIRECTION_VECTOR:
            next_game = step_game(current_game, direction)
            tuple_game = make_game_tuple(next_game)

            if tuple_game not in visited:
                visited.add(tuple_game)
                # add direction, not game state, to path
                new_path = path + [direction]

                if victory_check(next_game):
                    return new_path

                agenda.append((next_game, new_path))

    return None


# HELPER FUNCTIONS

# helper function to check legality of move


def is_in_bounds(game, coords):
    """
    A helper function that checks
    if a tile is within the bounds of the board.
    """
    j, i = coords
    return 0 <= j < game["height"] and 0 <= i < game["width"]


def check_wall(game, coords):
    """
    A helper function that checks
    if a tile contains a wall.
    """
    return coords in game["walls"]


def check_computer(game, coords):
    """
    A helper function that checks
    if a tile contains a computer.
    """
    return coords in game["computers"]


def player_move_valid(game, coords):
    """
    A helper function that checks if the player
    can move to the given position (i.e. if move in
    in bounds and not into a wall).
    """
    return is_in_bounds(game, coords) and not check_wall(game, coords)


def computer_move_valid(game, computer_coords, direction):
    """
    A helper function that checks if a computer can be
    pushed in the given direction (i.e. if move
    is in bounds, not into a wall, and computers are not stacked).
    """
    j_change, i_change = DIRECTION_VECTOR[direction]
    next_coords = (computer_coords[0] + j_change, computer_coords[1] + i_change)
    return (
        is_in_bounds(game, next_coords)
        and not check_wall(game, next_coords)
        and not check_computer(game, next_coords)
    )


def make_game_tuple(game):
    """
    A helper function that takes in a game and returns a
    tuple containing the player coordinates as one entry and
    a sorted tuple of the coordinates of computers on the board
    as another entry.
    """
    game_tuple = (game["player"], tuple(sorted(game["computers"])))

    return game_tuple


"""
if __name__ == "__main__":
    game = make_new_game([
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ])
    print(victory_check(game))

    print(dump_game(game))
"""
