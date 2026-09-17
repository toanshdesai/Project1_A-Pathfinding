# astar.py — pure algorithm, no pygame
import heapq
import math

import bfs

WALL = math.inf


def manhattan(cell, goal):
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])


def zero_h(cell, goal):
    return 0        # A* with h=0 IS Dijkstra — free second algorithm


def astar_step(grid, open_heap, g, parent, closed, goal, h, counter):
    """One expansion. Returns ("running"|"done"|"no_path", counter)."""
    if not open_heap:
        return "no_path", counter
    f, _, current = heapq.heappop(open_heap)  # smallest-f entry; _ discards the counter
    if current in closed:
        return "running", counter
    closed.add(current)
    if current == goal:
        return "done", counter
    for n in bfs.neighbors(grid, current[0], current[1]):
        if n in closed:
            continue
        new_g = g[current] + grid[n[0]][n[1]]
        if new_g < g.get(n, math.inf):
            g[n] = new_g
            parent[n] = current
            counter += 1
            heapq.heappush(open_heap, (new_g + h(n, goal), counter, n))
    return "running", counter


# ---------------- headless test harness ----------------
# (AI-assisted: harness completed by Claude; algorithm above written by me)

def run_astar(grid, start, goal, h=manhattan):
    """Seed fresh state, run astar_step to completion.
    Returns (status, path, cost, explored) — explored = cells expanded.
    Pass h=zero_h to run Dijkstra with the exact same machinery."""
    open_heap = [(h(start, goal), 0, start)]   # seed and loop MUST share the same h
    g = {start: 0}          # cost-so-far dict — start costs nothing
    parent = {}
    closed = set()          # EMPTY — cells join at pop time, unlike visited in BFS
    counter = 0

    status = "running"
    while status == "running":
        status, counter = astar_step(grid, open_heap, g, parent,
                                     closed, goal, h, counter)

    if status == "done":
        return status, bfs.reconstruct(parent, start, goal), g[goal], len(closed)
    return status, None, None, len(closed)


if __name__ == "__main__":
    start_, goal_ = (0, 0), (2, 2)

    # Test 1: empty 3x3 — expect a 5-cell path, cost 4
    grid_ = [[1] * 3 for _ in range(3)]
    print("empty grid:      ", run_astar(grid_, start_, goal_))

    # Test 2: mud placed on the route test 1 shows A* prefers — expect a detour, cost still 4
    grid_ = [[1] * 3 for _ in range(3)]
    grid_[1][0] = 5     # mud
    grid_[2][0] = 5     # mud
    print("mud detour:      ", run_astar(grid_, start_, goal_))

    # Test 3: middle row all walls — expect no_path
    grid_ = [[1] * 3 for _ in range(3)]
    grid_[1][0] = grid_[1][1] = grid_[1][2] = WALL
    print("walled off:      ", run_astar(grid_, start_, goal_))

    # Test 4: Dijkstra vs A* — same optimal cost, but Dijkstra (h=0) must
    # explore MORE cells than A*. NOTE: start/goal must NOT be opposite
    # corners — corner-to-corner on an empty grid makes EVERY cell tie at
    # the same f = g + h, so A* explores everything, exactly like Dijkstra.
    # Same-row endpoints give off-line cells strictly higher f.
    N = 15
    grid_ = [[1] * N for _ in range(N)]
    s_, t_ = (7, 0), (7, 14)
    a_status, a_path, a_cost, a_explored = run_astar(grid_, s_, t_, h=manhattan)
    d_status, d_path, d_cost, d_explored = run_astar(grid_, s_, t_, h=zero_h)
    print(f"A*       : cost {a_cost}, explored {a_explored}")
    print(f"Dijkstra : cost {d_cost}, explored {d_explored}")