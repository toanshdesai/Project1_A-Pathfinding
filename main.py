# Controls:
#   Left click / drag : cycle cells  normal (cost 1) -> mud (cost 5) -> wall -> normal
#   Right click       : place / move the goal cell
#   Start cell        : fixed at bottom-left (green)
#   B / A / D         : select BFS / A* / Dijkstra (only while idle)
#   SPACE             : run the selected algorithm
#   R                 : reset the search (keeps the maze; unlocks editing)
#
# AI-use note (per DA Honor Code): pygame scaffolding, integration wiring, and
# debugging assistance by Claude (Anthropic). Search algorithms in bfs.py and
# astar.py written by me. See README for details.

import math
import pygame
import bfs
import astar
from collections import deque

# ---------- constants ----------
CELL = 24                 # pixel size of one square
COLS, ROWS = 30, 30       # grid dimensions
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL

COST_NORMAL = 1
COST_MUD = 5              # "costly" terrain
WALL = math.inf           # a wall is just an infinitely expensive cell
STEPS_PER_FRAME = 3       # search speed: cells expanded per frame

# colors (R, G, B)
WHITE = (255, 255, 255)   # normal cell
BROWN = (181, 136, 99)    # costly cell ("mud")
BLACK = (30, 30, 30)      # wall
GREEN = (80, 200, 120)    # start
PURPLE = (160, 60, 200)   # goal
GRID_LINE = (200, 200, 200)
BLUE = (70, 130, 220)     # final path
LIGHT_GREEN = (150, 230, 170)  # frontier (discovered, not yet expanded)
PINK = (235, 160, 160)    # explored

# ---------- state ----------
# grid[row][col] holds the COST of stepping onto that cell.
grid = [[COST_NORMAL for _ in range(COLS)] for _ in range(ROWS)]

start = (ROWS - 1, 0)     # (row, col) — bottom-left corner
goal = (0, COLS - 1)      # default goal top-right; movable with right click
last_cell = None          # last cell cycled during the current drag

search_state = "idle"     # "idle" | "running" | "done" | "no_path"
algorithm = "astar"       # "bfs" | "astar" | "dijkstra"
current_h = astar.manhattan   # heuristic in use; set at seed time

# BFS structures
queue = deque()
visited = set()
# A*/Dijkstra structures
open_heap = []
g_scores = {}
closed = set()
counter = 0
# shared
parent = {}
path = []


def cycle_cell(row, col):
    """Advance one cell through normal -> mud -> wall -> normal."""
    if grid[row][col] == COST_NORMAL:
        grid[row][col] = COST_MUD
    elif grid[row][col] == COST_MUD:
        grid[row][col] = WALL
    else:
        grid[row][col] = COST_NORMAL


def cell_color(row, col):
    """Cell color by priority: special cells, then search layers, then terrain.

    Priority matters: path cells are also explored cells, so path must be
    tested first. For A*, closed is tested BEFORE the heap because lazy
    deletion leaves stale heap entries for already-expanded cells.
    """
    cell = (row, col)
    if cell == start:
        return GREEN
    if cell == goal:
        return PURPLE
    if cell in path:
        return BLUE
    if algorithm == "bfs":
        if cell in queue:
            return LIGHT_GREEN
        if cell in visited:
            return PINK
    else:
        if cell in closed:
            return PINK
        if any(item[2] == cell for item in open_heap):
            return LIGHT_GREEN
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

    global goal, last_cell, search_state, algorithm, current_h
    global queue, visited, open_heap, g_scores, closed, counter, parent, path

    running = True
    while running:                                  # ---- the game loop ----
        # 1) EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEMOTION and event.buttons[0] == 1 \
                    and search_state == "idle":
                mx, my = event.pos
                col, row = mx // CELL, my // CELL
                if not (0 <= row < ROWS and 0 <= col < COLS):
                    continue
                if (row, col) != last_cell and (row, col) not in (start, goal):
                    cycle_cell(row, col)
                    last_cell = (row, col)

            elif event.type == pygame.MOUSEBUTTONDOWN and search_state == "idle":
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
                # unconditional: drag bookkeeping, not maze editing —
                # the idle-guard belongs only on things that mutate the maze
                last_cell = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and search_state == "idle":
                    parent = {}
                    path = []
                    if algorithm == "bfs":
                        queue = deque([start])
                        visited = {start}
                    else:               # astar and dijkstra share machinery
                        current_h = (astar.manhattan if algorithm == "astar"
                                     else astar.zero_h)
                        open_heap = [(current_h(start, goal), 0, start)]
                        g_scores = {start: 0}
                        closed = set()
                        counter = 0
                    search_state = "running"

                elif event.key == pygame.K_r:
                    # reset BOTH algorithm families; keep the maze
                    queue = deque()
                    visited = set()
                    open_heap = []
                    g_scores = {}
                    closed = set()
                    counter = 0
                    parent = {}
                    path = []
                    search_state = "idle"
                elif event.key == pygame.K_m and search_state == "idle":
                    for r in range(8, ROWS):
                        for c in range(10, 18):
                            grid[r][c] = COST_MUD
                    goal = (15,27)
                elif event.key == pygame.K_b and search_state == "idle":
                    algorithm = "bfs"
                elif event.key == pygame.K_a and search_state == "idle":
                    algorithm = "astar"
                elif event.key == pygame.K_d and search_state == "idle":
                    algorithm = "dijkstra"

        # ---- advance the search (between events and drawing) ----
        if search_state == "running":
            for _ in range(STEPS_PER_FRAME):
                if algorithm == "bfs":
                    search_state = bfs.bfs_step(grid, queue, visited, parent, goal)
                else:
                    search_state, counter = astar.astar_step(
                        grid, open_heap, g_scores, parent, closed,
                        goal, current_h, counter)
                if search_state != "running":
                    if search_state == "done":
                        path = bfs.reconstruct(parent, start, goal)
                        cost = sum(grid[r][c] for r, c in path[1:])
                        explored = len(visited) if algorithm == "bfs" else len(closed)
                        print(f"{algorithm}: cost={cost}, steps={len(path) - 1}, explored={explored}")
                    break

        # 2) DRAW: repaint the whole grid from the data, every frame
        screen.fill(GRID_LINE)
        for row in range(ROWS):
            for col in range(COLS):
                rect = (col * CELL + 1, row * CELL + 1, CELL - 2, CELL - 2)
                pygame.draw.rect(screen, cell_color(row, col), rect)

        # 3) SHOW the finished frame, then wait for next tick
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()