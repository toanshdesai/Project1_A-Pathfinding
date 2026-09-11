# bfs.py — pure algorithm, no pygame, no globals from other files

from collections import deque
import math

WALL = math.inf   # bfs.py defines its own notion of "impassable"

def neighbors(grid, row, col):
    """Return a list of (row, col) tuples: in-bounds, non-wall, 4-directional."""

    rows = len(grid)
    cols = len(grid[0])

    results = []

    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != WALL:
            results.append((nr, nc))

    return results


def bfs_step(grid, queue, visited, parent, goal):
    """One expansion. Returns "running", "done", or "no_path"."""
    if not queue:
        return "no_path"

    current = queue.popleft()

    if current == goal:
        return "done"

    for n in neighbors(grid, current[0], current[1]):
        if n not in visited:
            visited.add(n)
            parent[n] = current
            queue.append(n)

    return "running"


def reconstruct(parent, start, goal):
    """Walk the breadcrumbs goal -> start, return the path start -> goal."""

    path = [goal]
    cur = goal

    while cur != start:
        cur = parent[cur]
        path.append(cur)

    return path[::-1]

if __name__ == "__main__":
    # tiny 3x3 test: no walls, start top-left, goal bottom-right
    g = [[1]*3 for _ in range(3)]
    queue = deque([ (0, 0) ])
    visited = { (0, 0) }
    parent = {}

    status = "running"
    while status == "running":
        status = bfs_step(g, queue, visited, parent, (2, 2))

    if status == "done":
        print(reconstruct(parent, (0, 0), (2, 2)))
    else:
        print(status)

    g[1][0] = g[1][1] = g[1][2] = WALL
    queue = deque([(0, 0)])
    visited = {(0, 0)}
    parent = {}
    status = "running"
    while status == "running":
        status = bfs_step(g, queue, visited, parent, (2, 2))

    if status == "done":
        print(reconstruct(parent, (0, 0), (2, 2)))
    else:
        print(status)