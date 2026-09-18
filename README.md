# Project1_Pathfinding

BFS, Dijkstra, and A\* implemented from scratch in Python, animated with PyGame.
The grid supports **weighted terrain** (normal = 1, mud = 5, wall = impassable),
which is what makes the differences between the three algorithms visible.

## Running it

```
pip install pygame
python main.py
```

Python 3.12.

| Key / Input | Action |
|---|---|
| Left click / drag | Cycle cells: normal (1) → mud (5) → wall → normal |
| Right click | Place / move the goal |
| `B` / `D` / `A` | Select BFS / Dijkstra / A\* (idle only) |
| `SPACE` | Run the selected algorithm |
| `R` | Reset the search, keep the maze |
| `M` | Load the "Toll Road" demo maze |
| `C` | Clear the maze |

Start is fixed bottom-left. Editing locks during a search — press `R` to unlock.

**Colors:** green = start, purple = goal, brown = mud, black = wall,
light green = frontier, pink = explored, blue = final path.

## How the three algorithms relate

Same search skeleton, different rule for which cell to expand next.
**g** = true cost from the start; **h** = estimated cost to the goal.

| Algorithm | Expands by | Optimal? | Cost-aware? |
|---|---|---|---|
| BFS | insertion order (FIFO queue) | Only on unweighted grids | No |
| Dijkstra | lowest **g** | Yes | Yes |
| A\* | lowest **g + h** | Yes, if h is admissible | Yes |

BFS finds the *fewest steps*, which on a weighted grid is not the cheapest
path — it can't see cost at all. Dijkstra adds cost awareness but has no sense
of direction, so it floods outward evenly. A\* adds direction: `f = g + h`
biases expansion toward the goal, returning Dijkstra's optimal path for far
less work, provided h is **admissible** (never overestimates).

Consequence used directly here: **A\* with `h = 0` is Dijkstra** (`f = g + 0 = g`).
Dijkstra isn't implemented separately — it's `astar_step` called with `zero_h`.

## Heuristic choice

**Manhattan distance**: `abs(dr) + abs(dc)`.

Movement is 4-directional and minimum step cost is 1, so Manhattan is exactly
the true minimum step count between two cells. That makes it both *admissible*
(never overestimates — mud only makes reality more expensive, which is allowed)
and *tight* (the largest admissible estimate available here, so A\* gets maximum
discriminating power). Euclidean is also admissible but strictly smaller — for
a cell 10 rows and 10 columns away it says 14.1 where Manhattan correctly says
20 — so it explores more cells for the same answer. Euclidean only becomes
correct once diagonal movement is allowed.

## Results — "Toll Road" maze (`M` key)

Mud band (cost 5) across columns 10–17 below row 8, clean corridor above, goal
at (15, 27). Every monotone route is 41 steps; the cheap route detours 16 steps
over the mud instead of paying the 8-cell toll.

| Algorithm | Path cost | Steps | Cells explored |
|---|---|---|---|
| A\* | 57 | 57 | 400 |
| Dijkstra | 57 | 57 | 796 |
| BFS | **73** | **41** | 749 |

1. **BFS's path is the shortest and the most expensive** — 41 steps, cost 73,
   straight through the mud. Fewest steps ≠ cheapest path.
2. **Dijkstra and A\* agree on cost**, as they must; both are optimal, so they
   can only differ in effort.
3. **A\* did half of Dijkstra's work** for the identical result. That gap is
   the heuristic.

### Unexpected finding: geometry matters

On an **empty** grid with start and goal at opposite corners, A\* explores all
900 cells — no better than Dijkstra. Corner-to-corner, every cell lies on some
monotone shortest path, so every cell's `f` ties at the same value. A heuristic
that can't discriminate is functionally `h = 0`, and A\* degrades to Dijkstra.
Moving the goal off-corner or adding any obstacle restores the advantage.
**A heuristic's value depends on problem geometry, not just the formula.**

## Code structure

```
main.py    PyGame UI: rendering, events, animation loop
bfs.py     neighbors(), bfs_step(), reconstruct()
astar.py   heuristics, astar_step(), headless test harness
```

`main.py` imports the algorithm modules; they import nothing from it. Neither
algorithm module contains PyGame code or global state — all data arrives as
parameters. That's why `python bfs.py` and `python astar.py` run standalone
tests, and why adding A\* required almost no UI changes.

**Cells store cost, not type.** A wall is just `math.inf` — too expensive to
ever enter — so the algorithms need no separate wall concept, and weighted
terrain came for free.

**One step per frame.** Search state lives outside the game loop; each frame
advances it `STEPS_PER_FRAME` expansions. The step functions return
`"running"` / `"done"` / `"no_path"`, which the caller assigns back into the
search state, so the search stops itself by reporting.

**A\* checks for the goal at pop time, not discovery time.** Correctness, not
style: the goal may first be *discovered* via an expensive route while a
cheaper one is still in the heap. Only when it's *popped* is its cost optimal.

**A\* can revisit cells; BFS can't.** BFS's first arrival at a cell is always
via a shortest route, so `visited` bans re-entry permanently. With weighted
terrain that's false, so A\* tests `new_g < g.get(n, inf)` and rewrites the
cell's cost and parent when it finds something cheaper.

**Lazy deletion.** `heapq` can't update entries, so improved cells are pushed
again and stale pops are discarded via the `closed` set — which doubles as the
drawing data for explored cells.

**Tie-breaking.** Heap entries are `(f, counter, cell)`; the counter breaks
f-ties deterministically instead of falling through to comparing cell tuples.

## Known limitations

- **4-directional only.** Manhattan is inadmissible with diagonals (5 rows +
  5 columns away is 5 diagonal moves, but Manhattan claims 10), so adding
  8-directional movement requires switching to octile distance.
- **Fast mouse drags skip cells**, since motion events sample the pointer
  rather than tracing its path.
- **Global state.** `main.py` carries ~14 module-level globals; bundling search
  state into a class would remove the `global` statement entirely.

## AI use and outside assistance

**FlintK12:** https://app.flintk12.com/activities/a-pathfinding-h-26efda/sessions/dee4ad8b-1ceb-4a11-a89b-9f6538af0d01

**Claude:** https://claude.ai/share/2797da4a-1da9-45bf-9334-536825896548