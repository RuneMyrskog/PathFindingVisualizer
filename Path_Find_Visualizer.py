from __future__ import annotations
import AStar
import threading
import pygame
import tkinter as tk
from tkinter import Label, Entry, Button, messagebox

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

grid = [[AStar.UNBLOCKED for _ in range(ROWS)] for _ in range(COLS)]
start_pos = (10, 10) # default start position
end_pos = (70, 50) # default end position
updated = []


class AStarThread(threading.Thread):
    """
    Thread to run AStar algorithm on. After completing task, stores resulting
    shortest path that it found in path attribute for use in UI thread
    """

    path: [(int, int)]

    def run(self):
        self.path = AStar.a_star_search(grid, start_pos, end_pos, delay=DELAY)
        return


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


def assign_positions(window, start_entry, end_entry):

    for entry in {start_entry, end_entry}:
        if not ((entry[0].isdigit() and entry[1].isdigit())
                and (-1 < int(entry[0]) < COLS and -1 < int(entry[1]) < ROWS)):
            messagebox.showwarning(title="invalid entry",
                                   message="please enter valid positions")
            return

    global start_pos
    global end_pos
    start_pos = int(start_entry[0]), int(start_entry[1])
    end_pos = int(end_entry[0]), int(end_entry[1])
    window.destroy()


def popup():

    window = tk.Tk()
    start_x_label = Label(window, text="Start(x) (0 - {0}): ".format(COLS-1))
    start_x_box = Entry(window)
    start_x_label.grid(row=1, column=1)
    start_x_box.grid(row=1, column=2)
    start_x_box.insert(0, str(start_pos[0]))

    start_y_label = Label(window, text="Start(y) (0 - {0}):".format(ROWS-1))
    start_y_box = Entry(window)
    start_y_label.grid(row=2, column=1)
    start_y_box.grid(row=2, column=2)
    start_y_box.insert(0, str(start_pos[1]))

    end_x_label = Label(window, text="End(x) (0 - {0}): ".format(COLS-1))
    end_x_box = Entry(window)
    end_x_label.grid(row=1, column=3)
    end_x_box.grid(row=1, column=4)
    end_x_box.insert(0, str(end_pos[0]))

    end_y_label = Label(window, text="End(y) (0 - {0}):".format(ROWS-1))
    end_y_box = Entry(window)
    end_y_label.grid(row=2, column=3)
    end_y_box.grid(row=2, column=4)
    end_y_box.insert(0, str(end_pos[1]))

    obstacles_label = Label(window,
                            text="click/drag squares to create obstacles",
                            fg="green")
    obstacles_label.grid(row=3, column=2, columnspan=4)
    restart_label = Label(window, text="Press R to restart", fg="green")
    restart_label.grid(row=4, column=2, columnspan=4)
    start_label = Label(window,
                        text="Press SPACE to start path finding algorithm",
                        fg="green")
    start_label.grid(row=5, column=2, columnspan=4)

    submit = Button(window, text='Go', command=lambda: assign_positions(window, (start_x_box.get(), start_y_box.get()), (end_x_box.get(), end_y_box.get())))
    submit.grid(row=6, column=1, columnspan=4)

    window.mainloop()


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
    popup()
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
                    popup()
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
