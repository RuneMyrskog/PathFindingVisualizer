import math
import time

# AStar algorithm uses these constants to judge entries in the grid argument
BLOCKED = 0
UNBLOCKED = 1
CLOSED = 2
OPEN = 3

# directions one can travel from one node to another node
DIRECTIONS = [(-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1),
              (0, 1)]


class Node:
    """
    A Node in the AStar search algorithm
    """
    def __init__(self, pos, parent, g, h, f):
        self.pos = pos  # tuple of form (x, y) holding this nodes coordinates
        self.g = g  # total length of the PATH connecting this node to start
        self.h = h  # euclidean distance from this node to end
        self.f = f  # sum of self.g and self.h
        self.parent = parent  # previous node in path from start to this node


def get_path(node) ->[(int, int)]:
    """
    returns a list of positions in path from start node to node
    :param node: the node to trace to from the starting node
    :return [(int, int)]: list of positions in path
    """
    path = []

    while node is not None:
        path.append(node.pos)
        node = node.parent

    return path[::-1]


def distance(pos_1, pos_2) -> float:
    """
    return the euclidean distance between pos_1 and pos_2

    :param pos_1: tuple containing row and column number of first position
    :param pos_2: tuple containing row and column number of second position
    :return float: euclidean distance between pos_1 and pos_2
    """
    return math.sqrt((pos_1[0] - pos_2[0]) ** 2 + (pos_1[1] - pos_2[1]) ** 2)


def get_neighbour_position(curr_pos, direction) -> (int, int):

    return curr_pos[0] + direction[0], curr_pos[1] + direction[1]


def is_accessible(curr_pos, direction, grid):
    """

    :param curr_pos: current node position
    :param neighbour_pos: neighbour position
    :param direction: direction neighbour lies in
    :param grid:
    :return:
    """
    neighbour_pos = get_neighbour_position(curr_pos, direction)

    if -1 < neighbour_pos[0] < len(grid) and -1 < neighbour_pos[1] \
            < len(grid[0]):

        # skip square if its not a valid neighbour
        if grid[neighbour_pos[0]][neighbour_pos[1]] in {BLOCKED, CLOSED}:
            return False

        # skip neighbours which lie diagonally across blocked squares
        if direction[0] != 0 and direction[1] != 0:
            if grid[curr_pos[0] + direction[0]][
                curr_pos[1]] == BLOCKED and grid[curr_pos[0]][
                    curr_pos[1] + direction[1]] == BLOCKED:
                return False

        return True
    return False


def get_valid_neighbour_positions(node, grid) -> [(int, int)]:
    """
    checks each grid position around the Node node, returns list
    of these positions which are not closed or blocked or lie diagonally across
    blocked positions

    :param node: node whose neighbours are being checked
    :param grid: grid on which node and its neighbours lie
    :return [(int, int)]: list of valid neighbour positions
    """
    positions = []

    for direction in DIRECTIONS:

        if is_accessible(node.pos, direction, grid):
            positions.append(get_neighbour_position(node.pos, direction))

    return positions


def a_star_search(grid, start_pos, end_pos, delay = 0.0) -> [(int, int)]:
    """
    Use a-star path finding algorithm search for the shortest path from
    start_pos to end_pos in the 2d array grid, return a list of positions from
    start_pos to end_pos representing the shortest path, or the empty list if
    no path exists

    :param grid: 2d array representing 2d grid of positions
    :param start_pos: 2d index representing starting position
    :param end_pos: 2d index representing the ending position
    :param delay: optional
    :return [(int, int)]: list of positions on shortest path from start_pos
                          to end_pos, if it exists
    """

    open_set = set()
    open_set.add(Node(start_pos, None, 0, 0, 0))

    while open_set:
        time.sleep(delay)

        curr_best = min(open_set, key=lambda node: node.f)
        open_set.remove(curr_best)
        grid[curr_best.pos[0]][curr_best.pos[1]] = CLOSED  # closed

        if curr_best.pos == end_pos:
            print("length of shortest path: " + str(curr_best.f))
            return get_path(curr_best)

        for neighbour_pos in get_valid_neighbour_positions(curr_best, grid):

            g = curr_best.g + distance(neighbour_pos, curr_best.pos)
            h = distance(neighbour_pos, end_pos)
            f = g + h

            in_open_set = False
            for open_node in open_set:
                if open_node.pos == neighbour_pos:  # neighbour already in openset
                    in_open_set = True
                    if g < open_node.g:
                        open_node.parent = curr_best
                        open_node.g = g
                    break

            if not in_open_set:
                neighbour = Node(neighbour_pos, curr_best, g, h, f)
                open_set.add(neighbour)
                grid[neighbour_pos[0]][neighbour_pos[1]] = OPEN

    return []
