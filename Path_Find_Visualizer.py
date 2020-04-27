from __future__ import annotations
import pygame
import AStar
import threading

# color constants
OPEN_COLOR = (0, 255, 0)
CLOSED_COLOR = (255, 0, 0)
PATH_COLOR = (0, 0, 0)
UNBLOCKED_COLOR = (100, 10, 200)
BLOCKED_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (0, 0, 0)

# delay for visualization purpose
DELAY = 0.001

# screen size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# grid/block constants
COLS = 80
ROWS = 60
BLOCK_BUFFER = 4200 / (ROWS * COLS)  # number of pixels of padding in between each node
BLOCK_WIDTH = (SCREEN_WIDTH - BLOCK_BUFFER * (COLS + 1)) / COLS
BLOCK_HEIGHT = (SCREEN_HEIGHT - BLOCK_BUFFER * (ROWS + 1)) / ROWS


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(BACKGROUND_COLOR)

grid = [[AStar.UNBLOCKED for _ in range(ROWS)] for _ in range(COLS)]
start_pos = (10, 10)
end_pos = (70, 50)
updated = []


def is_endpoint(pos) -> bool:

    return pos in {start_pos, end_pos}


def get_display_coord(pos) -> (float, float):
    """
    return the screen pixel coordinates of the square in position pos in the
    grid
    :param pos: tuple containing the square's row and column number to convert
    :return: tuple containing the coordinates of the square with respect to the
     displays pixels
    """
    x_pix = pos[0] * (BLOCK_BUFFER + BLOCK_WIDTH) + BLOCK_BUFFER
    y_pix = pos[1] * (BLOCK_BUFFER + BLOCK_HEIGHT) + BLOCK_BUFFER

    return x_pix, y_pix


def get_grid_coord(pixel) -> (int, int):
    """
    convert the screen coordinates in pixel into 2d index of the grid

    :param pixel: tuple of screen coordinates
    :return: tuple of the 2d index into grid
    """
    x = int((pixel[0] - BLOCK_BUFFER) / (BLOCK_BUFFER + BLOCK_WIDTH))
    y = int((pixel[1] - BLOCK_BUFFER) / (BLOCK_BUFFER + BLOCK_HEIGHT))
    return x, y


def reset_display():
    """
    restore every square represented in grid to their default state. Set all
    squares to 1 in grid representing non-obstacle terrain, draw each square
    with the default color chosen for them

    :return: None
    """
    screen.fill(BACKGROUND_COLOR)

    for x in range(COLS):
        for y in range(ROWS):

            if is_endpoint((x, y)):
                color = PATH_COLOR
            else:
                color = UNBLOCKED_COLOR

            grid[x][y] = 1
            update_block((x, y), color)

    pygame.display.update()


def update_block(pos, color):
    """
    paints the block at grid position pos with color color, and adds this block
    to the list of updated blocks

    :param pos: 2d index of this block in grid
    :param color: color to paint block with
    :return: None
    """
    x_pix, y_pix = get_display_coord(pos)
    rect = (x_pix, y_pix, BLOCK_WIDTH, BLOCK_HEIGHT)

    pygame.draw.rect(screen, color, rect)
    updated.append(rect)


def update_grid():
    """
    updates every block in the grid according to the value at its index
    :return: None
    """
    for i in range(COLS):
        for j in range(ROWS):
            if not is_endpoint((i, j)):

                if grid[i][j] == AStar.CLOSED:
                    update_block((i, j), CLOSED_COLOR)

                if grid[i][j] == AStar.OPEN:
                    update_block((i, j), OPEN_COLOR)


class AStarThread(threading.Thread):
    """
    Thread to run AStar algorithm on. After completing task, stores resulting
    shortest path that it found in path attribute for use in UI thread
    """

    path: [(int, int)]

    def run(self):
        self.path = AStar.a_star_search(grid, start_pos, end_pos, delay=DELAY)
        return


def run_visualizer():
    """
    Main UI loop to update screen
    :return None
    """
    searching = False
    can_edit = True
    pressed = False
    running = True
    a_star_thread = None

    reset_display()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                pressed = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pressed = True

            if event.type == pygame.KEYDOWN and not searching:
                if event.key == pygame.K_SPACE:
                    a_star_thread = AStarThread()
                    a_star_thread.start()
                    searching = True
                    can_edit = False

                if event.key == pygame.K_r:
                    can_edit = True
                    reset_display()

        if pressed and can_edit:
            x, y = get_grid_coord(pygame.mouse.get_pos())

            if not is_endpoint((x, y)):
                grid[x][y] = 0
                update_block((x, y), BLOCKED_COLOR)

        if searching:
            update_grid()
            if not a_star_thread.is_alive():
                for pos in a_star_thread.path:
                    update_block(pos, PATH_COLOR)
                searching = False

        pygame.display.update(updated)
        updated.clear()


if __name__ == "__main__":
    run_visualizer()
