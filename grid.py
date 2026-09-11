# Controls:
#   Left click  : cycle a cell  normal (cost 1) -> costly (cost 5) -> wall -> normal
#   Right click : place / move the goal cell
#   Start cell  : fixed at bottom-left (green)
#
# AI-use note (per DA Honor Code): this scaffolding file was written with help
# from Claude (Anthropic) to learn pygame basics: the game loop, event handling,
# pixel->grid coordinate math, and drawing. See README for details.

import math
import pygame

# ---------- constants ----------
CELL = 24                 # pixel size of one square
COLS, ROWS = 30, 30       # grid dimensions
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL

COST_NORMAL = 1
COST_MUD = 5              # "costly" terrain
WALL = math.inf           # a wall is just an infinitely expensive cell
last_cell = None          # last cell cycled during the current drag; None = not dragging

# colors (R, G, B)
WHITE = (255, 255, 255)   # normal cell
BROWN = (181, 136, 99)    # costly cell ("mud")
BLACK = (30, 30, 30)      # wall
GREEN = (80, 200, 120)    # start
PURPLE = (160, 60, 200)   # goal
GRID_LINE = (200, 200, 200)

# ---------- state ----------
# grid[row][col] holds the COST of stepping onto that cell.
# 2D list construction: one row of COLS values, repeated ROWS times.
grid = [[COST_NORMAL for _ in range(COLS)] for _ in range(ROWS)]

start = (ROWS - 1, 0)     # (row, col) — bottom-left corner
goal = (0, COLS - 1)      # default goal top-right; movable with right click


def cycle_cell(row, col):
    """Advance one cell through normal -> mud -> wall -> normal."""
    if grid[row][col] == COST_NORMAL:
        grid[row][col] = COST_MUD
    elif grid[row][col] == COST_MUD:
        grid[row][col] = WALL
    else:
        grid[row][col] = COST_NORMAL


def cell_color(row, col):
    """Decide what color a cell should be drawn, checking special cells first."""
    if (row, col) == start:
        return GREEN
    if (row, col) == goal:
        return PURPLE
    if grid[row][col] == WALL:
        return BLACK
    if grid[row][col] == COST_MUD:
        return BROWN
    return WHITE


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Project1_Pathfinding")
    clock = pygame.time.Clock()

    global goal, last_cell
    running = True
    while running:                                  # ---- the game loop ----
        # 1) EVENTS: everything the user did since last frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:           # window's X button
                running = False

            elif event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
                mx, my = event.pos
                col, row = mx // CELL, my // CELL
                if not (0 <= row < ROWS and 0 <= col < COLS):
                    continue
                if (row, col) != last_cell and (row, col) not in (start, goal):
                    cycle_cell(row, col)
                    last_cell = (row, col)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                col, row = mx // CELL, my // CELL
                if not (0 <= row < ROWS and 0 <= col < COLS):
                    continue
                if event.button == 1:
                    if (row, col) not in (start, goal):
                        cycle_cell(row, col)
                        last_cell = (row, col)
                elif event.button == 3:
                    if (row, col) != start and grid[row][col] != WALL:
                        goal = (row, col)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                last_cell = None

        # 2) DRAW: repaint the whole grid from the data, every frame
        screen.fill(GRID_LINE)
        for row in range(ROWS):
            for col in range(COLS):
                rect = (col * CELL + 1, row * CELL + 1, CELL - 2, CELL - 2)
                pygame.draw.rect(screen, cell_color(row, col), rect)

        # 3) SHOW the finished frame, then wait for next tick
        pygame.display.flip()
        clock.tick(60)                              # cap at 60 frames/sec

    pygame.quit()


if __name__ == "__main__":
    main()