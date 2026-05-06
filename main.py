import streamlit as st
import random
import time
from collections import deque

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="AI Quest Game",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",import streamlit as st
import random
import time
from collections import deque

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="AI Quest Game",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# DEFAULTS
# ============================================================
DEFAULT_ROWS = 20
DEFAULT_COLS = 24

# ============================================================
# CSS (Modern UI + responsive board)
# ============================================================
APP_CSS = """
<style>
.block-container { max-width: 1400px; padding-top: 1.2rem; padding-bottom: 2.0rem; }

.stApp {
  background: radial-gradient(1200px 800px at 20% 0%, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0.00) 60%),
              #070b14;
}

.card {
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 16px 16px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.10);
}
.card, .card * { color: #0f172a !important; }

.hero-title { font-size: 2.2rem; font-weight: 900; letter-spacing: -0.02em; margin: 0; }
.hero-subtitle { margin-top: 0.25rem; font-size: 1.05rem; color: rgba(15, 23, 42, 0.75) !important; }
.muted { color: rgba(15, 23, 42, 0.65) !important; font-size: 0.95rem; }

.grid-wrap { width: 100%; display: flex; justify-content: center; }
.board-scroll { width: 100%; overflow-x: auto; padding-bottom: 6px; }
.board {
  display: grid;
  gap: var(--gap);
  padding: 14px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
  border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.12);
  width: max-content;
  margin: 0 auto;
}

.cell {
  width: var(--cell);
  height: var(--cell);
  border-radius: calc(var(--cell) * 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font);
  border: 1px solid rgba(0,0,0,0.06);
  user-select: none;
  font-weight: 800;
}

/* base cell types */
.cell-empty   { background: #f1f5f9; color: #334155; }
.cell-wall    { background: #0f172a; color: #e5e7eb; }
.cell-agent   { background: #e0f2fe; color: #0284c7; border-color: rgba(2,132,199,0.25); }
.cell-goal    { background: #fef3c7; color: #b45309; border-color: rgba(180,83,9,0.25); }

/* overlays */
.cell-visited { background: #dcfce7; color: #166534; border-color: rgba(22,101,52,0.22); }
.cell-path    { background: #86efac; color: #14532d; border-color: rgba(20,83,45,0.20); }

/* minimax */
.cell-wizard  { background: #ede9fe; color: #6d28d9; border-color: rgba(109,40,217,0.25); }
.cell-enemy   { background: #fee2e2; color: #b91c1c; border-color: rgba(185,28,28,0.25); }

/* kmeans zones */
.cell-zone1 { background: #fee2e2; color: #7f1d1d; }
.cell-zone2 { background: #dbeafe; color: #1e3a8a; }
.cell-zone3 { background: #fef9c3; color: #713f12; }
.cell-centroid { background: #000000; color: #ffffff; }

.badges { display: flex; flex-wrap: wrap; gap: 10px; }
.badge {
  background: #f8fafc;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 999px;
  padding: 8px 10px;
  font-size: 0.92rem;
  color: rgba(30, 41, 59, 0.85);
}
.badge strong { color: rgba(15, 23, 42, 0.95); }

.logbox {
  background: #0b1220;
  color: #e5e7eb;
  border-radius: 16px;
  padding: 12px 14px;
  border: 1px solid rgba(255,255,255,0.08);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 0.9rem;
  line-height: 1.45rem;
  max-height: 360px;
  overflow-y: auto;
  white-space: pre-wrap;
}

/* Make Streamlit text readable on dark background */
html, body, [class*="css"] { color: #e5e7eb; }
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# ============================================================
# CSP-BASED DUNGEON GENERATION (your logic, generalized)
# ============================================================

def create_empty_dungeon(rows, cols):
    return [["X" for _ in range(cols)] for _ in range(rows)]

def carve_guaranteed_path(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    r, c = start
    grid[r][c] = "."
    while (r, c) != goal:
        if random.random() < 0.5:
            if c < cols - 1:
                c += 1
        else:
            if r < rows - 1:
                r += 1
        grid[r][c] = "."

def add_random_openings(grid, prob=0.25):
    rows, cols = len(grid), len(grid[0])
    for r in range(rows):
        for c in range(cols):
            if random.random() < prob:
                grid[r][c] = "."

def is_valid(grid, r, c):
    rows, cols = len(grid), len(grid[0])
    return 0 <= r < rows and 0 <= c < cols and grid[r][c] != "X"

def get_neighbors(r, c, grid):
    moves = [(-1,0),(1,0),(0,-1),(0,1)]
    res = []
    for dr, dc in moves:
        nr, nc = r + dr, c + dc
        if is_valid(grid, nr, nc):
            res.append((nr, nc))
    return res

def path_exists_bfs(grid, start, goal):
    q = deque([start])
    visited = set([start])
    while q:
        r, c = q.popleft()
        if (r, c) == goal:
            return True
        for nb in get_neighbors(r, c, grid):
            if nb not in visited:
                visited.add(nb)
                q.append(nb)
    return False

def generate_dungeon(rows, cols, open_prob=0.25, max_tries=200):
    start = (0, 0)
    goal = (rows - 1, cols - 1)
    for _ in range(max_tries):
        grid = create_empty_dungeon(rows, cols)
        carve_guaranteed_path(grid, start, goal)
        add_random_openings(grid, prob=open_prob)
        if path_exists_bfs(grid, start, goal):
            grid[start[0]][start[1]] = "A"
            grid[goal[0]][goal[1]] = "G"
            return grid
    grid = create_empty_dungeon(rows, cols)
    carve_guaranteed_path(grid, start, goal)
    grid[start[0]][start[1]] = "A"
    grid[goal[0]][goal[1]] = "G"
    return grid

def find_symbol(grid, sym):
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == sym:
                return (r, c)
    return None

# ============================================================
# Shared helpers for search algorithms
# ============================================================

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def reconstruct_path(parent, start, goal):
    if goal not in parent and goal != start:
        return []
    path = []
    node = goal
    while node != start:
        path.append(node)
        node = parent[node]
    path.append(start)
    path.reverse()
    return path

def bfs_find_path(grid, start, goal):
    """Used by CSP proof path highlighting."""
    q = deque([start])
    visited = set([start])
    parent = {}
    while q:
        cur = q.popleft()
        if cur == goal:
            return reconstruct_path(parent, start, goal)
        for nb in get_neighbors(*cur, grid):
            if nb not in visited:
                visited.add(nb)
                parent[nb] = cur
                q.append(nb)
    return []

# ============================================================
# Algorithms (7)
# ============================================================

def bfs(grid, start, goal):
    q = deque([start])
    visited = set([start])
    parent = {}
    nodes = 0
    logs = [f"🚦 BFS started at {start}"]
    while q:
        cur = q.popleft()
        nodes += 1
        logs.append(f"🔍 Exploring {cur}")
        if cur == goal:
            logs.append("🏆 Goal reached!")
            break
        for nb in get_neighbors(*cur, grid):
            if nb not in visited:
                visited.add(nb)
                parent[nb] = cur
                q.append(nb)
    path = reconstruct_path(parent, start, goal)
    return visited, path, nodes, logs

def dfs(grid, start, goal):
    stack = [start]
    visited = set([start])
    parent = {}
    nodes = 0
    logs = [f"🧗 DFS started at {start}"]
    while stack:
        cur = stack.pop()
        nodes += 1
        logs.append(f"🔍 Exploring {cur}")
        if cur == goal:
            logs.append("🏆 Goal reached!")
            break
        for nb in get_neighbors(*cur, grid):
            if nb not in visited:
                visited.add(nb)
                parent[nb] = cur
                stack.append(nb)
    path = reconstruct_path(parent, start, goal)
    return visited, path, nodes, logs

def astar(grid, start, goal):
    open_list = [(heuristic(start, goal), 0, start)]
    visited = set()
    parent = {}
    g_cost = {start: 0}
    nodes = 0
    logs = [f"✨ A* started at {start} (h={heuristic(start, goal)})"]
    while open_list:
        open_list.sort()
        f, g, cur = open_list.pop(0)
        if cur in visited:
            continue
        visited.add(cur)
        nodes += 1
        logs.append(f"🔍 Exploring {cur} with f={f}")
        if cur == goal:
            logs.append("🏆 Goal reached!")
            break
        for nb in get_neighbors(*cur, grid):
            new_g = g + 1
            if nb not in g_cost or new_g < g_cost[nb]:
                g_cost[nb] = new_g
                parent[nb] = cur
                open_list.append((new_g + heuristic(nb, goal), new_g, nb))
    path = reconstruct_path(parent, start, goal)
    return visited, path, nodes, logs

def hill_climbing(grid, start, goal, max_restarts=10, max_steps=3000):
    cur = start
    trail = [cur]
    restarts = 0
    steps = 0
    logs = [f"⛰️ Hill Climbing started at {start}"]
    while cur != goal and steps < max_steps:
        steps += 1
        neighbors = get_neighbors(*cur, grid)
        if not neighbors:
            logs.append("❌ No neighbors available. Stop.")
            break

        best = None
        best_dist = heuristic(cur, goal)
        for nb in neighbors:
            d = heuristic(nb, goal)
            if d < best_dist:
                best = nb
                best_dist = d

        if best is None:
            restarts += 1
            logs.append(f"🧱 Stuck at {cur}. Restart #{restarts}")
            if restarts > max_restarts:
                logs.append("❌ Too many restarts. Stop.")
                break
            cur = random.choice(neighbors)
            logs.append(f"🎲 Random move to {cur}")
        else:
            cur = best
            logs.append(f"➡️ Move to {cur}")

        trail.append(cur)

    if cur == goal:
        logs.append("🏆 Goal reached!")
    return trail, restarts, logs

# ----- Minimax (separate 6x6 demo) -----
def minimax_grid_fixed_6x6():
    return [
        ['W', '.', '.', 'X', '.', '.'],
        ['.', 'X', '.', '.', '.', 'X'],
        ['.', '.', '.', 'X', '.', '.'],
        ['X', '.', 'X', '.', '.', '.'],
        ['.', '.', '.', '.', 'X', '.'],
        ['.', 'X', '.', '.', '.', 'G'],
    ]

def evaluate_game_state(wizard_pos, enemy_pos, goal_pos):
    if wizard_pos == goal_pos:
        return 1000
    if wizard_pos == enemy_pos:
        return -1000
    return manhattan(wizard_pos, enemy_pos) - manhattan(wizard_pos, goal_pos)

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def minimax(mini_grid, wizard_pos, enemy_pos, goal_pos, depth, is_wizard_turn):
    if depth == 0 or wizard_pos == goal_pos or wizard_pos == enemy_pos:
        return evaluate_game_state(wizard_pos, enemy_pos, goal_pos)

    wr, wc = wizard_pos
    er, ec = enemy_pos

    if is_wizard_turn:
        best = -99999
        for next_w in get_neighbors(wr, wc, mini_grid):
            best = max(best, minimax(mini_grid, next_w, enemy_pos, goal_pos, depth - 1, False))
        return best
    else:
        best = 99999
        enemy_moves = get_neighbors(er, ec, mini_grid)
        if not enemy_moves:
            return evaluate_game_state(wizard_pos, enemy_pos, goal_pos)
        for next_e in enemy_moves:
            best = min(best, minimax(mini_grid, wizard_pos, next_e, goal_pos, depth - 1, True))
        return best

def minimax_game(mini_grid, wizard_start, enemy_start, goal_pos, depth=3, max_turns=12):
    wizard = wizard_start
    enemy = enemy_start
    wizard_trail = [wizard]
    enemy_trail = [enemy]
    nodes_eval = 0
    logs = ["⚔️ Minimax game started!"]

    for turn in range(1, max_turns + 1):
        # Wizard move (MAX)
        wr, wc = wizard
        moves = get_neighbors(wr, wc, mini_grid)
        if not moves:
            logs.append("🧱 Wizard trapped. Game over.")
            return wizard, enemy, wizard_trail, enemy_trail, nodes_eval, "Wizard trapped", turn, logs

        best_move = None
        best_score = -99999
        for mv in moves:
            nodes_eval += 1
            score = minimax(mini_grid, mv, enemy, goal_pos, depth, False)
            if score > best_score:
                best_score = score
                best_move = mv

        wizard = best_move
        wizard_trail.append(wizard)
        logs.append(f"🧙 Turn {turn}: Wizard → {wizard} (score={best_score})")

        if wizard == goal_pos:
            logs.append("🏆 Wizard wins!")
            return wizard, enemy, wizard_trail, enemy_trail, nodes_eval, "Wizard wins", turn, logs
        if wizard == enemy:
            logs.append("💀 Enemy wins! (caught wizard)")
            return wizard, enemy, wizard_trail, enemy_trail, nodes_eval, "Enemy wins", turn, logs

        # Enemy move (simple chase)
        er, ec = enemy
        enemy_moves = get_neighbors(er, ec, mini_grid)
        if enemy_moves:
            best_e = None
            best_d = 99999
            for mv in enemy_moves:
                d = manhattan(mv, wizard)
                if d < best_d:
                    best_d = d
                    best_e = mv
            enemy = best_e
            enemy_trail.append(enemy)
            logs.append(f"👾 Turn {turn}: Enemy → {enemy} (chasing)")

        if enemy == wizard:
            logs.append("💀 Enemy wins! (caught wizard)")
            return wizard, enemy, wizard_trail, enemy_trail, nodes_eval, "Enemy wins", turn, logs

    logs.append("⏳ Draw (turn limit).")
    return wizard, enemy, wizard_trail, enemy_trail, nodes_eval, "Draw", max_turns, logs

# ----- CSP demo on current dungeon -----
def csp_validate_and_prove_path(grid):
    """Show CSP idea: constraint is 'a path must exist'. Return proof path using BFS."""
    start = find_symbol(grid, "A")
    goal = find_symbol(grid, "G")
    if start is None or goal is None:
        return False, [], ["❌ CSP: Start/Goal not found."]
    ok = path_exists_bfs(grid, start, goal)
    logs = [f"🧩 CSP: Solvable constraint check = {ok}"]
    proof = bfs_find_path(grid, start, goal) if ok else []
    if proof:
        logs.append(f"✅ CSP: Proof path found by BFS. Length={len(proof)-1}")
    return ok, proof, logs

# ----- K-Means clustering -----
def euclidean(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) ** 0.5

def get_all_open_cells(grid):
    cells = []
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] != "X":
                cells.append((r, c))
    return cells

def assign_cells_to_clusters(open_cells, centroids):
    clusters = {i: [] for i in range(len(centroids))}
    for cell in open_cells:
        best_i = 0
        best_d = 99999
        for i, cent in enumerate(centroids):
            d = euclidean(cell, cent)
            if d < best_d:
                best_d = d
                best_i = i
        clusters[best_i].append(cell)
    return clusters

def recalc_centroids(clusters, old_centroids):
    new_centroids = []
    for i in clusters:
        cells = clusters[i]
        if not cells:
            new_centroids.append(old_centroids[i])
        else:
            avg_r = sum(p[0] for p in cells) / len(cells)
            avg_c = sum(p[1] for p in cells) / len(cells)
            new_centroids.append((round(avg_r), round(avg_c)))
    return new_centroids

def run_kmeans(grid, k=3, max_iter=20, seed=5):
    open_cells = get_all_open_cells(grid)
    logs = [f"📌 K-Means: clustering {len(open_cells)} open cells into K={k} zones"]
    if len(open_cells) < k:
        return {}, [], 0, logs + ["❌ Not enough open cells for K-Means."]

    random.seed(seed)
    centroids = random.sample(open_cells, k)
    logs.append(f"🎯 Initial centroids = {centroids}")

    for it in range(1, max_iter + 1):
        clusters = assign_cells_to_clusters(open_cells, centroids)
        new_centroids = recalc_centroids(clusters, centroids)
        sizes = [len(clusters[i]) for i in range(k)]
        logs.append(f"🔁 Iter {it}: sizes={sizes}, centroids={new_centroids}")

        if new_centroids == centroids:
            logs.append("✅ Converged!")
            return clusters, centroids, it, logs

        centroids = new_centroids

    logs.append("⏳ Max iterations reached.")
    return clusters, centroids, max_iter, logs

# ============================================================
# UI: Auto cell sizing (NOT a slider)
# ============================================================

def cell_emoji(ch):
    return {"A": "🤖", "G": "🏆", "X": "⬛", "W": "🧙", "E": "👾"}.get(ch, "")

def auto_cell_size(rows, cols, target_board_width_px=760):
    usable = max(360, target_board_width_px - 40)
    max_dim = max(rows, cols)
    gap = 5 if max_dim >= 22 else 7
    cell = (usable - (cols - 1) * gap) // cols
    cell = int(max(16, min(38, cell)))
    font = int(max(11, min(18, cell * 0.52)))
    return cell, gap, font

def render_grid_html(grid, visited=None, path=None, overlay=None):
    rows, cols = len(grid), len(grid[0])
    visited = visited or set()
    path = path or []
    path_set = set(path)
    overlay = overlay or {}

    cell, gap, font = auto_cell_size(rows, cols, target_board_width_px=760)
    board_style = f"--cell:{cell}px;--gap:{gap}px;--font:{font}px;grid-template-columns: repeat({cols}, var(--cell));"

    html = '<div class="grid-wrap"><div class="board-scroll">'
    html += f'<div class="board" style="{board_style}">'

    for r in range(rows):
        for c in range(cols):
            ch = grid[r][c]
            pos = (r, c)

            # base chars
            if ch == "X":
                klass = "cell cell-wall"
            elif ch == "A":
                klass = "cell cell-agent"
            elif ch == "G":
                klass = "cell cell-goal"
            elif ch == "W":
                klass = "cell cell-wizard"
            elif ch == "E":
                klass = "cell cell-enemy"
            else:
                # kmeans overlay
                tag = overlay.get(pos, "")
                if tag == "zone1":
                    klass = "cell cell-zone1"
                elif tag == "zone2":
                    klass = "cell cell-zone2"
                elif tag == "zone3":
                    klass = "cell cell-zone3"
                elif tag == "centroid":
                    klass = "cell cell-centroid"
                else:
                    if pos in path_set:
                        klass = "cell cell-path"
                    elif pos in visited:
                        klass = "cell cell-visited"
                    else:
                        klass = "cell cell-empty"

            html += f'<div class="{klass}" title="{pos}">{cell_emoji(ch)}</div>'

    html += "</div></div></div>"
    return html

# ============================================================
# SESSION STATE
# ============================================================

ALGOS = ["BFS", "DFS", "A*", "Hill Climbing", "Minimax", "CSP", "K-Means"]

def init_state():
    if "rows" not in st.session_state:
        st.session_state.rows = DEFAULT_ROWS
    if "cols" not in st.session_state:
        st.session_state.cols = DEFAULT_COLS
    if "open_prob" not in st.session_state:
        st.session_state.open_prob = 0.25

    if "grid" not in st.session_state:
        st.session_state.grid = generate_dungeon(st.session_state.rows, st.session_state.cols, st.session_state.open_prob)

    if "selected_algo" not in st.session_state:
        st.session_state.selected_algo = "BFS"

    if "visited" not in st.session_state:
        st.session_state.visited = set()
    if "path" not in st.session_state:
        st.session_state.path = []
    if "overlay" not in st.session_state:
        st.session_state.overlay = {}

    if "nodes_explored" not in st.session_state:
        st.session_state.nodes_explored = 0
    if "steps_taken" not in st.session_state:
        st.session_state.steps_taken = 0
    if "status" not in st.session_state:
        st.session_state.status = "Idle"
    if "logs" not in st.session_state:
        st.session_state.logs = []

    # Hill climbing
    if "hc_restarts" not in st.session_state:
        st.session_state.hc_restarts = 0

    # Minimax
    if "mm_nodes" not in st.session_state:
        st.session_state.mm_nodes = 0
    if "mm_turns" not in st.session_state:
        st.session_state.mm_turns = 0
    if "mm_result" not in st.session_state:
        st.session_state.mm_result = ""
    if "mm_wizard_trail" not in st.session_state:
        st.session_state.mm_wizard_trail = []
    if "mm_enemy_trail" not in st.session_state:
        st.session_state.mm_enemy_trail = []

    # CSP
    if "csp_ok" not in st.session_state:
        st.session_state.csp_ok = True

    # KMeans
    if "km_iters" not in st.session_state:
        st.session_state.km_iters = 0

def reset_run_state():
    st.session_state.visited = set()
    st.session_state.path = []
    st.session_state.overlay = {}
    st.session_state.nodes_explored = 0
    st.session_state.steps_taken = 0
    st.session_state.status = "Idle"
    st.session_state.logs = []
    st.session_state.hc_restarts = 0

    st.session_state.mm_nodes = 0
    st.session_state.mm_turns = 0
    st.session_state.mm_result = ""
    st.session_state.mm_wizard_trail = []
    st.session_state.mm_enemy_trail = []

    st.session_state.csp_ok = True
    st.session_state.km_iters = 0

def log_add(msg):
    st.session_state.logs.append(msg)

init_state()

# If user changes rows/cols, auto-regenerate a matching dungeon (so grid isn't mismatched)
def ensure_grid_size_matches():
    g = st.session_state.grid
    if len(g) != st.session_state.rows or len(g[0]) != st.session_state.cols:
        st.session_state.grid = generate_dungeon(st.session_state.rows, st.session_state.cols, st.session_state.open_prob)
        reset_run_state()
        log_add("🔁 Grid resized → dungeon regenerated automatically.")

# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
<div class="card">
  <div class="hero-title">🏆 AI Quest Game</div>
  <div class="hero-subtitle">Visualizing AI Algorithms</div>
  <div class="muted">CSP-based dungeon generation ✅ • BFS ✅ • DFS ✅ • A* ✅ • Hill Climbing ✅ • Minimax ✅ • CSP ✅ • K-Means ✅</div>
</div>
""",
    unsafe_allow_html=True,
)
st.write("")

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🎛️ Controls")

    st.session_state.selected_algo = st.selectbox(
        "🎯 Select Algorithm",
        ALGOS,
        index=ALGOS.index(st.session_state.selected_algo),
    )

    speed = st.slider("⏱️ Speed (delay)", 0.0, 0.6, 0.10, 0.05)

    st.markdown("---")
    st.markdown("### 🧩 Dungeon Settings (CSP-based)")

    st.session_state.rows = st.select_slider("Rows", options=[12, 16, 20, 24], value=st.session_state.rows)
    st.session_state.cols = st.select_slider("Cols", options=[16, 20, 24, 28], value=st.session_state.cols)
    st.session_state.open_prob = st.slider("Open cell probability", 0.10, 0.45, float(st.session_state.open_prob), 0.05)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧪 Generate New Dungeon", use_container_width=True):
            st.session_state.grid = generate_dungeon(st.session_state.rows, st.session_state.cols, st.session_state.open_prob)
            reset_run_state()
            log_add("🧪 New CSP-based dungeon generated.")

    with c2:
        if st.button("🧼 Reset", use_container_width=True):
            reset_run_state()
            log_add("🧼 Reset done (kept dungeon).")

    run_clicked = st.button("▶️ Run Algorithm", type="primary", use_container_width=True)

# Apply size matching after sidebar changes
ensure_grid_size_matches()

# ============================================================
# MAIN LAYOUT
# ============================================================
left, right = st.columns([1.7, 1], gap="large")

with left:
    st.markdown(
        '<div class="card"><h3 style="margin:0;">🗺️ Dungeon Board</h3>'
        '<div class="muted">A=🤖 • G=🏆 • X=⬛ • Visited=🟩 • Path/Trail=🟢 • Minimax: W=🧙 E=👾</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    grid_placeholder = st.empty()

with right:
    status_placeholder = st.empty()

    st.write("")
    st.markdown('<div class="card"><h3 style="margin:0 0 10px 0;">🧾 Log Panel</h3>', unsafe_allow_html=True)
    log_placeholder = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

def render_status_panel():
    algo = st.session_state.selected_algo

    # Path length label changes per algo
    if algo == "Hill Climbing":
        path_label = "Trail Steps"
        path_value = max(0, len(st.session_state.path) - 1)
        extra = f"<div class='badge'>🔁 <strong>Restarts:</strong> {st.session_state.hc_restarts}</div>"
    elif algo == "Minimax":
        path_label = "Wizard Turns"
        path_value = st.session_state.mm_turns
        extra = (
            f"<div class='badge'>🧮 <strong>Nodes Evaluated:</strong> {st.session_state.mm_nodes}</div>"
            f"<div class='badge'>🏁 <strong>Result:</strong> {st.session_state.mm_result or '—'}</div>"
        )
    elif algo == "CSP":
        path_label = "Proof Path Len (BFS)"
        path_value = max(0, len(st.session_state.path) - 1)
        extra = f"<div class='badge'>✅ <strong>Solvable:</strong> {st.session_state.csp_ok}</div>"
    elif algo == "K-Means":
        path_label = "N/A"
        path_value = 0
        extra = f"<div class='badge'>🔁 <strong>Iterations:</strong> {st.session_state.km_iters}</div>"
    else:
        path_label = "Path Length"
        path_value = max(0, len(st.session_state.path) - 1)
        extra = ""

    html = f"""
    <div class="card">
      <h3 style="margin:0 0 10px 0;">📊 Status Panel</h3>
      <div class="badges">
        <div class="badge">🧠 <strong>Algorithm:</strong> {algo}</div>
        <div class="badge">📌 <strong>Status:</strong> {st.session_state.status}</div>
        <div class="badge">🧭 <strong>Nodes Explored:</strong> {st.session_state.nodes_explored}</div>
        <div class="badge">🛤️ <strong>{path_label}:</strong> {path_value}</div>
        <div class="badge">👣 <strong>Steps Taken:</strong> {st.session_state.steps_taken}</div>
        {extra}
      </div>
    </div>
    """
    status_placeholder.markdown(html, unsafe_allow_html=True)

def render_view():
    algo = st.session_state.selected_algo

    if algo == "Minimax":
        base = minimax_grid_fixed_6x6()
        # overlay wizard/enemy into a copy
        wiz = st.session_state.mm_wizard_trail[-1] if st.session_state.mm_wizard_trail else (0, 0)
        ene = st.session_state.mm_enemy_trail[-1] if st.session_state.mm_enemy_trail else (5, 0)
        display = [list(row) for row in base]
        display[wiz[0]][wiz[1]] = "W"
        display[ene[0]][ene[1]] = "E"
        visited = set(st.session_state.mm_enemy_trail)
        path = list(st.session_state.mm_wizard_trail)
        grid_html = render_grid_html(display, visited=visited, path=path, overlay={})
    else:
        grid_html = render_grid_html(
            st.session_state.grid,
            visited=st.session_state.visited,
            path=st.session_state.path,
            overlay=st.session_state.overlay,
        )

    grid_placeholder.markdown(grid_html, unsafe_allow_html=True)

    logs_text = "\n".join(st.session_state.logs[-250:]) if st.session_state.logs else "No logs yet…"
    log_placeholder.markdown(f'<div class="logbox">{logs_text}</div>', unsafe_allow_html=True)

    render_status_panel()

# initial render
render_view()

# ============================================================
# RUN
# ============================================================
def run_selected_algorithm(delay):
    reset_run_state()
    st.session_state.status = "Running"
    log_add(f"🚀 Running {st.session_state.selected_algo}...")
    render_view()

    algo = st.session_state.selected_algo

    # ---- PATHFINDING on CSP dungeon ----
    if algo in ["BFS", "DFS", "A*", "Hill Climbing", "CSP", "K-Means"]:
        grid = st.session_state.grid
        start = find_symbol(grid, "A")
        goal = find_symbol(grid, "G")
        if start is None or goal is None:
            st.session_state.status = "Completed"
            log_add("❌ Start/Goal not found.")
            render_view()
            return

        if algo == "BFS":
            visited, path, nodes, logs = bfs(grid, start, goal)
            st.session_state.visited = set(visited)
            st.session_state.path = list(path)
            st.session_state.nodes_explored = nodes
            st.session_state.steps_taken = len(logs)
            st.session_state.logs.extend(logs)

        elif algo == "DFS":
            visited, path, nodes, logs = dfs(grid, start, goal)
            st.session_state.visited = set(visited)
            st.session_state.path = list(path)
            st.session_state.nodes_explored = nodes
            st.session_state.steps_taken = len(logs)
            st.session_state.logs.extend(logs)

        elif algo == "A*":
            visited, path, nodes, logs = astar(grid, start, goal)
            st.session_state.visited = set(visited)
            st.session_state.path = list(path)
            st.session_state.nodes_explored = nodes
            st.session_state.steps_taken = len(logs)
            st.session_state.logs.extend(logs)

        elif algo == "Hill Climbing":
            trail, restarts, logs = hill_climbing(grid, start, goal)
            st.session_state.path = list(trail)
            st.session_state.visited = set(trail)
            st.session_state.nodes_explored = len(set(trail))
            st.session_state.hc_restarts = restarts
            st.session_state.steps_taken = len(logs)
            st.session_state.logs.extend(logs)

        elif algo == "CSP":
            ok, proof, logs = csp_validate_and_prove_path(grid)
            st.session_state.csp_ok = ok
            st.session_state.path = list(proof)  # highlight proof path
            st.session_state.visited = set()
            st.session_state.nodes_explored = len(proof)
            st.session_state.steps_taken = len(logs)
            st.session_state.logs.extend(logs)

        elif algo == "K-Means":
            clusters, centroids, iters, logs = run_kmeans(grid, k=3)
            st.session_state.km_iters = iters
            st.session_state.nodes_explored = len(get_all_open_cells(grid))
            st.session_state.steps_taken = len(logs)
            st.session_state.logs.extend(logs)

            # build overlay colors
            overlay = {}
            for i, cells in clusters.items():
                tag = "zone1" if i == 0 else ("zone2" if i == 1 else "zone3")
                for p in cells:
                    overlay[p] = tag
            for cent in centroids:
                overlay[cent] = "centroid"
            st.session_state.overlay = overlay

    # ---- MINIMAX separate board ----
    if algo == "Minimax":
        mini = minimax_grid_fixed_6x6()
        wizard_start = (0, 0)
        enemy_start = (5, 0)
        goal_pos = (5, 5)

        wizard, enemy, wtrail, etrail, nodes_eval, result, turns, logs = minimax_game(
            mini, wizard_start, enemy_start, goal_pos, depth=3, max_turns=12
        )

        st.session_state.mm_wizard_trail = wtrail
        st.session_state.mm_enemy_trail = etrail
        st.session_state.mm_nodes = nodes_eval
        st.session_state.mm_turns = turns
        st.session_state.mm_result = result

        st.session_state.nodes_explored = nodes_eval
        st.session_state.steps_taken = len(logs)
        st.session_state.logs.extend(logs)

    st.session_state.status = "Completed"
    log_add("✅ Completed.")
    render_view()
    time.sleep(delay)

if run_clicked:
    run_selected_algorithm(speed)

st.caption("AI Quest Game • All 7 algorithms restored • CSP-based solvable dungeon • One file")
)

# ============================================================
# DEFAULTS
# ============================================================
DEFAULT_ROWS = 20
DEFAULT_COLS = 24

# ============================================================
# CSS (Modern UI)
# ============================================================
APP_CSS = """
<style>
.block-container { max-width: 1400px; padding-top: 1.2rem; padding-bottom: 2.0rem; }

.stApp {
  background: radial-gradient(1200px 800px at 20% 0%, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0.00) 60%),
              #070b14;
}

.card {
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 16px 16px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.10);
}
.card, .card * { color: #0f172a !important; }

.hero-title { font-size: 2.2rem; font-weight: 900; letter-spacing: -0.02em; margin: 0; }
.hero-subtitle { margin-top: 0.25rem; font-size: 1.05rem; color: rgba(15, 23, 42, 0.75) !important; }
.muted { color: rgba(15, 23, 42, 0.65) !important; font-size: 0.95rem; }

.grid-wrap { width: 100%; display: flex; justify-content: center; }
.board-scroll { width: 100%; overflow-x: auto; padding-bottom: 6px; }

/* Board uses CSS variables */
.board {
  display: grid;
  gap: var(--gap);
  padding: 14px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
  border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.12);
  width: max-content;
  margin: 0 auto;
}

.cell {
  width: var(--cell);
  height: var(--cell);
  border-radius: calc(var(--cell) * 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font);
  border: 1px solid rgba(0,0,0,0.06);
  user-select: none;
}

.cell-empty   { background: #f1f5f9; color: #334155; }
.cell-wall    { background: #0f172a; color: #e5e7eb; }
.cell-agent   { background: #e0f2fe; color: #0284c7; border-color: rgba(2,132,199,0.25); }
.cell-goal    { background: #fef3c7; color: #b45309; border-color: rgba(180,83,9,0.25); }
.cell-visited { background: #dcfce7; color: #166534; border-color: rgba(22,101,52,0.22); }
.cell-path    { background: #86efac; color: #14532d; border-color: rgba(20,83,45,0.20); }

.badges { display: flex; flex-wrap: wrap; gap: 10px; }
.badge {
  background: #f8fafc;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 999px;
  padding: 8px 10px;
  font-size: 0.92rem;
  color: rgba(30, 41, 59, 0.85);
}
.badge strong { color: rgba(15, 23, 42, 0.95); }

.logbox {
  background: #0b1220;
  color: #e5e7eb;
  border-radius: 16px;
  padding: 12px 14px;
  border: 1px solid rgba(255,255,255,0.08);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 0.9rem;
  line-height: 1.45rem;
  max-height: 360px;
  overflow-y: auto;
  white-space: pre-wrap;
}

html, body, [class*="css"] { color: #e5e7eb; }
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# ============================================================
# CSP-BASED DUNGEON GENERATION
# ============================================================

def create_empty_dungeon(rows, cols):
    return [["X" for _ in range(cols)] for _ in range(rows)]

def carve_guaranteed_path(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    r, c = start
    grid[r][c] = "."
    while (r, c) != goal:
        if random.random() < 0.5:
            if c < cols - 1:
                c += 1
        else:
            if r < rows - 1:
                r += 1
        grid[r][c] = "."

def add_random_openings(grid, prob=0.25):
    rows, cols = len(grid), len(grid[0])
    for r in range(rows):
        for c in range(cols):
            if random.random() < prob:
                grid[r][c] = "."

def is_valid(grid, r, c):
    rows, cols = len(grid), len(grid[0])
    return 0 <= r < rows and 0 <= c < cols and grid[r][c] != "X"

def get_neighbors(r, c, grid):
    moves = [(-1,0),(1,0),(0,-1),(0,1)]
    res = []
    for dr, dc in moves:
        nr, nc = r+dr, c+dc
        if is_valid(grid, nr, nc):
            res.append((nr, nc))
    return res

def path_exists_bfs(grid, start, goal):
    q = deque([start])
    visited = set([start])
    while q:
        r, c = q.popleft()
        if (r, c) == goal:
            return True
        for nb in get_neighbors(r, c, grid):
            if nb not in visited:
                visited.add(nb)
                q.append(nb)
    return False

def generate_dungeon(rows, cols, open_prob=0.25, max_tries=200):
    start = (0, 0)
    goal = (rows - 1, cols - 1)
    for _ in range(max_tries):
        grid = create_empty_dungeon(rows, cols)
        carve_guaranteed_path(grid, start, goal)
        add_random_openings(grid, prob=open_prob)
        if path_exists_bfs(grid, start, goal):
            grid[start[0]][start[1]] = "A"
            grid[goal[0]][goal[1]] = "G"
            return grid
    # fallback
    grid = create_empty_dungeon(rows, cols)
    carve_guaranteed_path(grid, start, goal)
    grid[start[0]][start[1]] = "A"
    grid[goal[0]][goal[1]] = "G"
    return grid

def find_symbol(grid, sym):
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == sym:
                return (r, c)
    return None

# ============================================================
# ALGORITHMS
# ============================================================

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def reconstruct_path(parent, start, goal):
    if goal not in parent and goal != start:
        return []
    path = []
    node = goal
    while node != start:
        path.append(node)
        node = parent[node]
    path.append(start)
    path.reverse()
    return path

def bfs(grid, start, goal):
    q = deque([start])
    visited = set([start])
    parent = {}
    nodes = 0
    logs = [f"🚦 BFS started at {start}"]
    while q:
        cur = q.popleft()
        nodes += 1
        logs.append(f"🔍 Exploring {cur}")
        if cur == goal:
            logs.append("🏆 Goal reached!")
            break
        for nb in get_neighbors(*cur, grid):
            if nb not in visited:
                visited.add(nb)
                parent[nb] = cur
                q.append(nb)
    path = reconstruct_path(parent, start, goal)
    return visited, path, nodes, logs

def dfs(grid, start, goal):
    stack = [start]
    visited = set([start])
    parent = {}
    nodes = 0
    logs = [f"🧗 DFS started at {start}"]
    while stack:
        cur = stack.pop()
        nodes += 1
        logs.append(f"🔍 Exploring {cur}")
        if cur == goal:
            logs.append("🏆 Goal reached!")
            break
        for nb in get_neighbors(*cur, grid):
            if nb not in visited:
                visited.add(nb)
                parent[nb] = cur
                stack.append(nb)
    path = reconstruct_path(parent, start, goal)
    return visited, path, nodes, logs

def astar(grid, start, goal):
    open_list = [(heuristic(start, goal), 0, start)]
    visited = set()
    parent = {}
    g_cost = {start: 0}
    nodes = 0
    logs = [f"✨ A* started at {start} (h={heuristic(start, goal)})"]
    while open_list:
        open_list.sort()
        f, g, cur = open_list.pop(0)
        if cur in visited:
            continue
        visited.add(cur)
        nodes += 1
        logs.append(f"🔍 Exploring {cur} with f={f}")
        if cur == goal:
            logs.append("🏆 Goal reached!")
            break
        for nb in get_neighbors(*cur, grid):
            new_g = g + 1
            if nb not in g_cost or new_g < g_cost[nb]:
                g_cost[nb] = new_g
                parent[nb] = cur
                open_list.append((new_g + heuristic(nb, goal), new_g, nb))
    path = reconstruct_path(parent, start, goal)
    return visited, path, nodes, logs

def hill_climbing(grid, start, goal, max_restarts=10, max_steps=3000):
    cur = start
    trail = [cur]
    restarts = 0
    steps = 0
    logs = [f"⛰️ Hill Climbing started at {start}"]
    while cur != goal and steps < max_steps:
        steps += 1
        neighbors = get_neighbors(*cur, grid)
        if not neighbors:
            logs.append("❌ No neighbors available. Stop.")
            break

        best = None
        best_dist = heuristic(cur, goal)
        for nb in neighbors:
            d = heuristic(nb, goal)
            if d < best_dist:
                best = nb
                best_dist = d

        if best is None:
            restarts += 1
            logs.append(f"🧱 Stuck at {cur}. Restart #{restarts}")
            if restarts > max_restarts:
                logs.append("❌ Too many restarts. Stop.")
                break
            cur = random.choice(neighbors)
            logs.append(f"🎲 Random move to {cur}")
        else:
            cur = best
            logs.append(f"➡️ Move to {cur}")

        trail.append(cur)

    if cur == goal:
        logs.append("🏆 Goal reached!")
    return trail, restarts, logs

# ============================================================
# UI: Auto cell sizing (NO slider)
# ============================================================

def cell_emoji(ch):
    return {"A": "🤖", "G": "🏆", "X": "⬛"}.get(ch, "")

def auto_cell_size(rows, cols, target_board_width_px=780):
    """
    Fix for your request:
    - Cell size is NOT controlled by user
    - It automatically fits the board width
    - Bigger grid => smaller cells
    - Smaller grid => bigger cells
    """
    # We reserve space for gaps and padding (rough estimate)
    # board padding left+right ~ 28px, so subtract
    usable = max(360, target_board_width_px - 40)

    # choose gap based on grid size
    max_dim = max(rows, cols)
    gap = 5 if max_dim >= 22 else 7

    # approximate cell size to fit width: cols*c + (cols-1)*gap <= usable
    cell = (usable - (cols - 1) * gap) // cols

    # clamp to keep UI clean
    cell = int(max(18, min(42, cell)))

    # font scales with cell
    font = int(max(11, min(18, cell * 0.50)))
    return cell, gap, font

def render_grid_html(grid, visited=None, path=None):
    rows, cols = len(grid), len(grid[0])
    visited = visited or set()
    path = path or []
    path_set = set(path)

    cell, gap, font = auto_cell_size(rows, cols, target_board_width_px=780)

    board_style = (
        f"--cell:{cell}px;--gap:{gap}px;--font:{font}px;"
        f"grid-template-columns: repeat({cols}, var(--cell));"
    )

    html = '<div class="grid-wrap"><div class="board-scroll">'
    html += f'<div class="board" style="{board_style}">'

    for r in range(rows):
        for c in range(cols):
            ch = grid[r][c]
            pos = (r, c)

            if ch == "X":
                klass = "cell cell-wall"
            elif ch == "A":
                klass = "cell cell-agent"
            elif ch == "G":
                klass = "cell cell-goal"
            else:
                if pos in path_set:
                    klass = "cell cell-path"
                elif pos in visited:
                    klass = "cell cell-visited"
                else:
                    klass = "cell cell-empty"

            html += f'<div class="{klass}" title="{pos}">{cell_emoji(ch)}</div>'

    html += "</div></div></div>"
    return html

# ============================================================
# SESSION STATE
# ============================================================

def init_state():
    if "rows" not in st.session_state:
        st.session_state.rows = DEFAULT_ROWS
    if "cols" not in st.session_state:
        st.session_state.cols = DEFAULT_COLS
    if "open_prob" not in st.session_state:
        st.session_state.open_prob = 0.25

    if "grid" not in st.session_state:
        st.session_state.grid = generate_dungeon(st.session_state.rows, st.session_state.cols, st.session_state.open_prob)

    if "selected_algo" not in st.session_state:
        st.session_state.selected_algo = "BFS"

    if "visited" not in st.session_state:
        st.session_state.visited = set()
    if "path" not in st.session_state:
        st.session_state.path = []
    if "nodes_explored" not in st.session_state:
        st.session_state.nodes_explored = 0
    if "steps_taken" not in st.session_state:
        st.session_state.steps_taken = 0
    if "status" not in st.session_state:
        st.session_state.status = "Idle"
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "hc_restarts" not in st.session_state:
        st.session_state.hc_restarts = 0

def reset_run_state():
    st.session_state.visited = set()
    st.session_state.path = []
    st.session_state.nodes_explored = 0
    st.session_state.steps_taken = 0
    st.session_state.status = "Idle"
    st.session_state.logs = []
    st.session_state.hc_restarts = 0

def log_add(msg):
    st.session_state.logs.append(msg)

init_state()

# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="card">
  <div class="hero-title">🏆 AI Quest Game</div>
  <div class="hero-subtitle">Visualizing AI Algorithms</div>
  <div class="muted">CSP-based dungeon generation ✅ • BFS ✅ • DFS ✅ • A* ✅ • Hill Climbing ✅</div>
</div>
""",
    unsafe_allow_html=True,
)
st.write("")

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🎛️ Controls")

    st.session_state.selected_algo = st.selectbox(
        "🎯 Select Algorithm",
        ["BFS", "DFS", "A*", "Hill Climbing"],
        index=["BFS", "DFS", "A*", "Hill Climbing"].index(st.session_state.selected_algo),
    )

    speed = st.slider("⏱️ Speed (delay per step)", 0.0, 0.6, 0.10, 0.05)

    st.markdown("---")
    st.markdown("### 🧩 Dungeon Settings (CSP-based)")

    # Grid size sliders are allowed; cell size will auto-fit
    st.session_state.rows = st.select_slider("Rows", options=[12, 16, 20, 24], value=st.session_state.rows)
    st.session_state.cols = st.select_slider("Cols", options=[16, 20, 24, 28], value=st.session_state.cols)
    st.session_state.open_prob = st.slider("Open cell probability", 0.10, 0.45, float(st.session_state.open_prob), 0.05)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧪 Generate New Dungeon", use_container_width=True):
            st.session_state.grid = generate_dungeon(st.session_state.rows, st.session_state.cols, st.session_state.open_prob)
            reset_run_state()
            log_add("🧪 New CSP-based dungeon generated.")

    with c2:
        if st.button("🧼 Reset", use_container_width=True):
            reset_run_state()
            log_add("🧼 Reset done (kept dungeon).")

    run_clicked = st.button("▶️ Run Algorithm", type="primary", use_container_width=True)

# ============================================================
# MAIN LAYOUT
# ============================================================

left, right = st.columns([1.7, 1], gap="large")

with left:
    st.markdown(
        '<div class="card"><h3 style="margin:0;">🗺️ Dungeon Board</h3>'
        '<div class="muted">A=🤖 Agent • G=🏆 Goal • X=⬛ Wall • Visited=🟩 • Path=🟢</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    grid_placeholder = st.empty()

with right:
    status_placeholder = st.empty()

    st.write("")
    st.markdown('<div class="card"><h3 style="margin:0 0 10px 0;">🧾 Log Panel</h3>', unsafe_allow_html=True)
    log_placeholder = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

def render_status_panel():
    algo = st.session_state.selected_algo
    if algo == "Hill Climbing":
        path_label = "Trail Steps"
        extra = f"<div class='badge'>🔁 <strong>Restarts:</strong> {st.session_state.hc_restarts}</div>"
    else:
        path_label = "Path Length"
        extra = ""

    path_value = max(0, len(st.session_state.path) - 1)

    html = f"""
    <div class="card">
      <h3 style="margin:0 0 10px 0;">📊 Status Panel</h3>
      <div class="badges">
        <div class="badge">🧠 <strong>Algorithm:</strong> {algo}</div>
        <div class="badge">📌 <strong>Status:</strong> {st.session_state.status}</div>
        <div class="badge">🧭 <strong>Nodes Explored:</strong> {st.session_state.nodes_explored}</div>
        <div class="badge">🛤️ <strong>{path_label}:</strong> {path_value}</div>
        <div class="badge">👣 <strong>Steps Taken:</strong> {st.session_state.steps_taken}</div>
        {extra}
      </div>
    </div>
    """
    status_placeholder.markdown(html, unsafe_allow_html=True)

def render_view():
    grid_placeholder.markdown(
        render_grid_html(st.session_state.grid, st.session_state.visited, st.session_state.path),
        unsafe_allow_html=True,
    )

    logs_text = "\n".join(st.session_state.logs[-250:]) if st.session_state.logs else "No logs yet…"
    log_placeholder.markdown(f'<div class="logbox">{logs_text}</div>', unsafe_allow_html=True)
    render_status_panel()

# Ensure grid matches slider sizes if user changed rows/cols without regenerating yet
def ensure_grid_size_matches():
    g = st.session_state.grid
    if len(g) != st.session_state.rows or len(g[0]) != st.session_state.cols:
        st.session_state.grid = generate_dungeon(st.session_state.rows, st.session_state.cols, st.session_state.open_prob)
        reset_run_state()
        log_add("🔁 Grid resized → regenerated dungeon automatically.")

ensure_grid_size_matches()

# initial render
render_view()

# ============================================================
# RUN
# ============================================================

def run_selected_algorithm():
    reset_run_state()
    st.session_state.status = "Running"
    log_add(f"🚀 Running {st.session_state.selected_algo}...")
    render_view()

    grid = st.session_state.grid
    start = find_symbol(grid, "A")
    goal = find_symbol(grid, "G")

    if start is None or goal is None:
        st.session_state.status = "Completed"
        log_add("❌ Start or Goal not found in grid.")
        render_view()
        return

    algo = st.session_state.selected_algo

    if algo == "BFS":
        visited, path, nodes, logs = bfs(grid, start, goal)
        st.session_state.visited = set(visited)
        st.session_state.path = list(path)
        st.session_state.nodes_explored = nodes
        st.session_state.steps_taken = len(logs)
        st.session_state.logs.extend(logs)

    elif algo == "DFS":
        visited, path, nodes, logs = dfs(grid, start, goal)
        st.session_state.visited = set(visited)
        st.session_state.path = list(path)
        st.session_state.nodes_explored = nodes
        st.session_state.steps_taken = len(logs)
        st.session_state.logs.extend(logs)

    elif algo == "A*":
        visited, path, nodes, logs = astar(grid, start, goal)
        st.session_state.visited = set(visited)
        st.session_state.path = list(path)
        st.session_state.nodes_explored = nodes
        st.session_state.steps_taken = len(logs)
        st.session_state.logs.extend(logs)

    else:
        trail, restarts, logs = hill_climbing(grid, start, goal)
        st.session_state.path = list(trail)
        st.session_state.visited = set(trail)
        st.session_state.nodes_explored = len(set(trail))
        st.session_state.steps_taken = len(logs)
        st.session_state.hc_restarts = restarts
        st.session_state.logs.extend(logs)

    st.session_state.status = "Completed"
    log_add("✅ Completed.")
    render_view()

if run_clicked:
    run_selected_algorithm()
    time.sleep(speed)

st.caption("AI Quest Game • Auto-resizing grid cells • No cell-size slider • One file")
