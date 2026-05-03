# ============================================================
# AI QUEST GAME (Streamlit) — UI + ALL 7 Algorithms (Single File)
# Modern, clean UI + beginner-friendly code
#
# Algorithms included:
# 1) BFS (Shortest path)
# 2) DFS (A path, not always shortest)
# 3) A* (Shortest + fewer nodes using heuristic)
# 4) Hill Climbing (Greedy + random restart)
# 5) Minimax (Wizard vs Enemy, small 6x6 demo)
# 6) CSP (Validate solvable dungeon by placing walls + backtracking)
# 7) K-Means (Cluster open cells into zones)
# ============================================================

import streamlit as st
import random
import time

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Quest Game",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ============================================================
# MODERN CSS (Cards + Grid)
# ============================================================
APP_CSS = """
<style>
.block-container { max-width: 1050px; padding-top: 1.1rem; padding-bottom: 2rem; }

.card {
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 16px 16px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.hero-title { font-size: 2.2rem; font-weight: 850; letter-spacing: -0.02em; margin: 0; }
.hero-subtitle { margin-top: 0.25rem; color: rgba(30, 41, 59, 0.75); font-size: 1.05rem; }
.muted { color: rgba(30, 41, 59, 0.65); font-size: 0.95rem; }

.grid-wrap { display: flex; justify-content: center; }
.board {
  display: grid;
  gap: 8px;
  padding: 14px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
  border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
}

.cell {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  border: 1px solid rgba(0,0,0,0.06);
  user-select: none;
}

.cell-empty   { background: #f1f5f9; color: #334155; }
.cell-wall    { background: #111827; color: #e5e7eb; }
.cell-agent   { background: #e0f2fe; color: #0284c7; border-color: rgba(2,132,199,0.25); }
.cell-goal    { background: #fef3c7; color: #b45309; border-color: rgba(180,83,9,0.25); }

.cell-visited { background: #dcfce7; color: #166534; border-color: rgba(22,101,52,0.22); }
.cell-path    { background: #a7f3d0; color: #065f46; border-color: rgba(6,95,70,0.25); }

.cell-wizard  { background: #ede9fe; color: #6d28d9; border-color: rgba(109,40,217,0.25); }
.cell-enemy   { background: #fee2e2; color: #b91c1c; border-color: rgba(185,28,28,0.25); }

.cell-zone1 { background: #fee2e2; color: #7f1d1d; }  /* red-ish */
.cell-zone2 { background: #dbeafe; color: #1e3a8a; }  /* blue-ish */
.cell-zone3 { background: #fef9c3; color: #713f12; }  /* yellow-ish */
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
  max-height: 320px;
  overflow-y: auto;
  white-space: pre-wrap;
}
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# ============================================================
# SECTION 1: GRID SETUP + HELPERS (from your notebook style)
# ============================================================

def create_grid_fixed_8x8():
    """Fixed 8x8 grid (consistent for viva)."""
    return [
        ['A', '.', '.', 'X', '.', '.', '.', '.'],
        ['.', 'X', '.', 'X', '.', 'X', '.', '.'],
        ['.', 'X', '.', '.', '.', 'X', '.', '.'],
        ['.', '.', '.', 'X', '.', '.', '.', 'X'],
        ['X', 'X', '.', 'X', '.', 'X', '.', '.'],
        ['.', '.', '.', '.', '.', 'X', 'X', '.'],
        ['.', 'X', 'X', 'X', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', 'X', '.', 'G'],
    ]

def generate_grid(n, wall_prob=0.22):
    """Random grid for 6/8/10/12 sizes."""
    grid = [["." for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            if (r, c) in [(0, 0), (n-1, n-1)]:
                continue
            if random.random() < wall_prob:
                grid[r][c] = "X"
    grid[0][0] = "A"
    grid[n-1][n-1] = "G"
    return grid

def find_position(grid, symbol):
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == symbol:
                return (r, c)
    return None

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def is_valid_move(grid, row, col):
    num_rows = len(grid)
    num_cols = len(grid[0])
    if row < 0 or row >= num_rows:
        return False
    if col < 0 or col >= num_cols:
        return False
    if grid[row][col] == "X":
        return False
    return True

def get_neighbors(grid, row, col):
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    valid = []
    for dr, dc in directions:
        rr, cc = row + dr, col + dc
        if is_valid_move(grid, rr, cc):
            valid.append((rr, cc))
    return valid

def reconstruct_path(parent_map, start, goal):
    path = []
    cur = goal
    while cur != start:
        path.append(cur)
        cur = parent_map[cur]
    path.append(start)
    path.reverse()
    return path

# ============================================================
# SECTION 2–4: PATHFINDING (BFS / DFS / A* / Hill Climbing)
# Implemented as generators so Streamlit can animate
# Each yield: visited_set, path_or_None, log_message
# ============================================================

def bfs_steps(grid, start, goal):
    queue = [start]
    visited = set([start])
    parent = {}
    nodes = 0

    yield visited, None, f"🚦 BFS started at {start}"

    while queue:
        cur = queue.pop(0)
        nodes += 1
        yield visited, None, f"🔍 Exploring node {cur}"

        if cur == goal:
            path = reconstruct_path(parent, start, goal)
            yield visited, path, f"🏆 Goal reached! Nodes explored={nodes}, Path length={len(path)-1}"
            return

        r, c = cur
        for nb in get_neighbors(grid, r, c):
            if nb not in visited:
                visited.add(nb)
                parent[nb] = cur
                queue.append(nb)
                yield visited, None, f"➕ Enqueue {nb}"

    yield visited, None, "❌ BFS failed (no path)."

def dfs_steps(grid, start, goal):
    stack = [start]
    visited = set([start])
    parent = {}
    nodes = 0

    yield visited, None, f"🧗 DFS started at {start}"

    while stack:
        cur = stack.pop()
        nodes += 1
        yield visited, None, f"🔍 Exploring node {cur}"

        if cur == goal:
            path = reconstruct_path(parent, start, goal)
            yield visited, path, f"🏆 Goal reached! Nodes explored={nodes}, Path length={len(path)-1}"
            return

        r, c = cur
        for nb in get_neighbors(grid, r, c):
            if nb not in visited:
                visited.add(nb)
                parent[nb] = cur
                stack.append(nb)
                yield visited, None, f"➕ Push {nb}"

    yield visited, None, "❌ DFS failed (no path)."

def astar_steps(grid, start, goal):
    open_list = []
    h_start = manhattan_distance(start, goal)
    open_list.append((h_start, 0, start))  # (f, g, pos)

    visited = set()
    parent = {}
    g_cost = {start: 0}
    nodes = 0

    yield visited, None, f"✨ A* started at {start} (h={h_start})"

    while open_list:
        open_list.sort(key=lambda x: x[0])
        f, g, cur = open_list.pop(0)

        if cur in visited:
            continue

        visited.add(cur)
        nodes += 1
        h = manhattan_distance(cur, goal)
        yield visited, None, f"🔍 Exploring {cur} with f={f}=g({g})+h({h})"

        if cur == goal:
            path = reconstruct_path(parent, start, goal)
            yield visited, path, f"🏆 Goal reached! Nodes explored={nodes}, Path length={len(path)-1}"
            return

        r, c = cur
        for nb in get_neighbors(grid, r, c):
            if nb in visited:
                continue

            new_g = g + 1
            if nb not in g_cost or new_g < g_cost[nb]:
                g_cost[nb] = new_g
                parent[nb] = cur
                f_nb = new_g + manhattan_distance(nb, goal)
                open_list.append((f_nb, new_g, nb))
                yield visited, None, f"➕ Add/Update {nb} with f={f_nb}"

    yield visited, None, "❌ A* failed (no path)."

def hill_climbing_steps(grid, start, goal, max_restarts=10, max_steps=200):
    all_open = []
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] != "X":
                all_open.append((r, c))

    cur = start
    total_path = [cur]
    visited_run = set([cur])
    nodes_explored = 0
    restarts = 0
    steps = 0

    yield set(total_path), None, f"⛰️ Hill Climbing started at {start}"

    while steps < max_steps:
        steps += 1
        nodes_explored += 1
        cur_dist = manhattan_distance(cur, goal)
        yield set(total_path), None, f"📍 At {cur}, distance={cur_dist}"

        if cur == goal:
            yield set(total_path), list(total_path), f"🏆 Goal reached! steps={len(total_path)-1}, restarts={restarts}"
            return

        r, c = cur
        neighbors = get_neighbors(grid, r, c)

        best = None
        best_dist = cur_dist
        for nb in neighbors:
            if nb in visited_run:
                continue
            d = manhattan_distance(nb, goal)
            if d < best_dist:
                best_dist = d
                best = nb

        if best is None:
            restarts += 1
            yield set(total_path), None, f"🧱 Stuck at {cur} (local max). Restart #{restarts}"

            if restarts > max_restarts:
                yield set(total_path), None, "❌ Too many restarts. Hill Climbing stopped."
                return

            cur = random.choice(all_open)
            visited_run = set([cur])
            total_path.append(cur)
            yield set(total_path), None, f"🎲 Restarted at {cur}"
        else:
            cur = best
            visited_run.add(cur)
            total_path.append(cur)
            yield set(total_path), None, f"➡️ Move to {cur}"

    yield set(total_path), None, "❌ Step limit reached. Hill Climbing stopped."

# ============================================================
# SECTION 6: MINIMAX (6x6 adversarial demo)
# ============================================================

def minimax_grid_fixed_6x6():
    # W=Wizard, E=Enemy, G=Goal, X=Wall, .=Empty
    return [
        ['W', '.', '.', 'X', '.', '.'],
        ['.', 'X', '.', '.', '.', 'X'],
        ['.', '.', '.', 'X', '.', '.'],
        ['X', '.', 'X', '.', '.', '.'],
        ['.', '.', '.', '.', 'X', '.'],
        ['.', 'X', '.', '.', '.', 'G'],
    ]

def evaluate_game_state(wizard_pos, enemy_pos, goal_pos):
    wizard_to_goal = manhattan_distance(wizard_pos, goal_pos)
    enemy_to_wizard = manhattan_distance(enemy_pos, wizard_pos)

    if wizard_pos == goal_pos:
        return 1000
    if wizard_pos == enemy_pos:
        return -1000

    return enemy_to_wizard - wizard_to_goal

def minimax(mini_grid, wizard_pos, enemy_pos, goal_pos, depth, is_wizard_turn):
    if depth == 0 or wizard_pos == goal_pos or wizard_pos == enemy_pos:
        return evaluate_game_state(wizard_pos, enemy_pos, goal_pos)

    wr, wc = wizard_pos
    er, ec = enemy_pos

    if is_wizard_turn:
        best_score = -99999
        for next_w in get_neighbors(mini_grid, wr, wc):
            score = minimax(mini_grid, next_w, enemy_pos, goal_pos, depth - 1, False)
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = 99999
        enemy_neighbors = get_neighbors(mini_grid, er, ec)
        if not enemy_neighbors:
            return evaluate_game_state(wizard_pos, enemy_pos, goal_pos)
        for next_e in enemy_neighbors:
            score = minimax(mini_grid, wizard_pos, next_e, goal_pos, depth - 1, True)
            best_score = min(best_score, score)
        return best_score

def minimax_game_steps(mini_grid, wizard_start, enemy_start, goal_pos, depth=3, max_turns=12):
    wizard = wizard_start
    enemy = enemy_start
    nodes_eval = 0

    yield wizard, enemy, None, {"nodes": 0, "turn": 0, "result": ""}, "⚔️ Minimax game started!"

    for turn in range(1, max_turns + 1):
        # Wizard turn (MAX)
        wr, wc = wizard
        moves = get_neighbors(mini_grid, wr, wc)
        if not moves:
            yield wizard, enemy, None, {"nodes": nodes_eval, "turn": turn, "result": "Wizard trapped"}, "🧱 Wizard is trapped!"
            return

        best_move = None
        best_score = -99999
        for mv in moves:
            nodes_eval += 1
            score = minimax(mini_grid, mv, enemy, goal_pos, depth, False)
            if score > best_score:
                best_score = score
                best_move = mv

        wizard = best_move
        yield wizard, enemy, None, {"nodes": nodes_eval, "turn": turn, "result": ""}, f"🧙 Wizard moves to {wizard} (score={best_score})"

        if wizard == goal_pos:
            yield wizard, enemy, None, {"nodes": nodes_eval, "turn": turn, "result": "Wizard wins"}, "🏆 Wizard wins! Reached goal."
            return
        if wizard == enemy:
            yield wizard, enemy, None, {"nodes": nodes_eval, "turn": turn, "result": "Enemy wins"}, "💀 Enemy wins! Caught wizard."
            return

        # Enemy turn (simple chase)
        er, ec = enemy
        enemy_moves = get_neighbors(mini_grid, er, ec)
        if enemy_moves:
            best_e = None
            best_d = 99999
            for mv in enemy_moves:
                d = manhattan_distance(mv, wizard)
                if d < best_d:
                    best_d = d
                    best_e = mv
            enemy = best_e

        yield wizard, enemy, None, {"nodes": nodes_eval, "turn": turn, "result": ""}, f"👾 Enemy moves to {enemy} (chasing)"

        if enemy == wizard:
            yield wizard, enemy, None, {"nodes": nodes_eval, "turn": turn, "result": "Enemy wins"}, "💀 Enemy wins! Caught wizard."
            return

    yield wizard, enemy, None, {"nodes": nodes_eval, "turn": max_turns, "result": "Draw"}, "⏳ Game ended (turn limit)."

# ============================================================
# SECTION 7: CSP (Validate solvable by placing walls + backtracking)
# ============================================================

def check_path_exists_bfs(test_grid, start_pos, goal_pos):
    queue = [start_pos]
    visited = set([start_pos])

    while queue:
        cur = queue.pop(0)
        if cur == goal_pos:
            return True
        r, c = cur
        for nb in get_neighbors(test_grid, r, c):
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return False

def csp_steps(base_grid, start_pos, goal_pos, attempts_limit=8, seed=7):
    # copy
    csp_grid = [list(row) for row in base_grid]

    ok = check_path_exists_bfs(csp_grid, start_pos, goal_pos)
    yield csp_grid, {"walls": 0, "backtracks": 0, "attempts": 0, "path_ok": ok}, "🧩 CSP: Initial path check..."

    if not ok:
        yield csp_grid, {"walls": 0, "backtracks": 0, "attempts": 0, "path_ok": False}, "❌ CSP: Original grid not solvable."
        return

    candidates = []
    for r in range(len(csp_grid)):
        for c in range(len(csp_grid[0])):
            if csp_grid[r][c] == "." and (r, c) != start_pos and (r, c) != goal_pos:
                candidates.append((r, c))

    random.seed(seed)
    random.shuffle(candidates)

    walls = 0
    backtracks = 0
    attempts = 0

    for pos in candidates[:attempts_limit]:
        attempts += 1
        r, c = pos
        csp_grid[r][c] = "X"
        yield csp_grid, {"walls": walls, "backtracks": backtracks, "attempts": attempts, "path_ok": True}, f"🧱 CSP: Trying wall at {pos}..."

        still_ok = check_path_exists_bfs(csp_grid, start_pos, goal_pos)
        if still_ok:
            walls += 1
            yield csp_grid, {"walls": walls, "backtracks": backtracks, "attempts": attempts, "path_ok": True}, f"✅ CSP: Kept wall at {pos} (path still exists)."
        else:
            csp_grid[r][c] = "."
            backtracks += 1
            yield csp_grid, {"walls": walls, "backtracks": backtracks, "attempts": attempts, "path_ok": True}, f"↩️ CSP: Backtrack! Wall at {pos} removed (constraint violated)."

    final_ok = check_path_exists_bfs(csp_grid, start_pos, goal_pos)
    yield csp_grid, {"walls": walls, "backtracks": backtracks, "attempts": attempts, "path_ok": final_ok}, f"🏁 CSP done. Path ok = {final_ok}"

# ============================================================
# SECTION 8: K-MEANS (Cluster open cells into zones)
# ============================================================

def euclidean_distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def get_all_open_cells(grid):
    open_cells = []
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] != "X":
                open_cells.append((r, c))
    return open_cells

def assign_cells_to_clusters(open_cells, centroids):
    clusters = {i: [] for i in range(len(centroids))}
    for cell in open_cells:
        best_i = 0
        best_d = 99999
        for i, cent in enumerate(centroids):
            d = euclidean_distance(cell, cent)
            if d < best_d:
                best_d = d
                best_i = i
        clusters[best_i].append(cell)
    return clusters

def recalculate_centroids(clusters, old_centroids):
    new_centroids = []
    for i in clusters:
        cells = clusters[i]
        if not cells:
            new_centroids.append(old_centroids[i])  # keep if empty cluster
        else:
            avg_r = sum(p[0] for p in cells) / len(cells)
            avg_c = sum(p[1] for p in cells) / len(cells)
            new_centroids.append((round(avg_r), round(avg_c)))
    return new_centroids

def kmeans_steps(grid, k=3, max_iterations=20, seed=5):
    open_cells = get_all_open_cells(grid)
    if len(open_cells) < k:
        yield None, None, {"iterations": 0}, "❌ Not enough open cells for K-Means."
        return

    random.seed(seed)
    centroids = random.sample(open_cells, k)
    yield None, None, {"iterations": 0, "centroids": centroids}, f"🎯 K-Means: Initial centroids = {centroids}"

    for it in range(1, max_iterations + 1):
        clusters = assign_cells_to_clusters(open_cells, centroids)
        new_centroids = recalculate_centroids(clusters, centroids)

        sizes = [len(clusters[i]) for i in range(k)]
        yield clusters, centroids, {"iterations": it, "centroids": centroids, "sizes": sizes}, f"🔁 Iteration {it}: sizes={sizes}, new_centroids={new_centroids}"

        if new_centroids == centroids:
            yield clusters, centroids, {"iterations": it, "centroids": centroids, "sizes": sizes}, "✅ Converged! Centroids stopped moving."
            return

        centroids = new_centroids

    yield clusters, centroids, {"iterations": max_iterations, "centroids": centroids}, "⏳ Max iterations reached."

# ============================================================
# UI RENDERING HELPERS
# ============================================================

def cell_emoji(ch):
    mapping = {
        "A": "🤖",
        "G": "🏆",
        "X": "⬛",
        "W": "🧙",
        "E": "👾",
    }
    return mapping.get(ch, "")

def render_grid_html(grid, visited=None, path=None, overlay=None):
    """
    overlay is optional dict {(r,c): "zone1"/"zone2"/"zone3"/"centroid"} for K-Means.
    """
    n = len(grid)
    visited = visited or set()
    path = path or []
    overlay = overlay or {}

    board_style = f"grid-template-columns: repeat({n}, 44px);"
    html = f'<div class="grid-wrap"><div class="board" style="{board_style}">'

    for r in range(n):
        for c in range(n):
            ch = grid[r][c]
            pos = (r, c)

            # base classes
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
                # overlays (kmeans zones) for open cells
                if overlay.get(pos) == "zone1":
                    klass = "cell cell-zone1"
                elif overlay.get(pos) == "zone2":
                    klass = "cell cell-zone2"
                elif overlay.get(pos) == "zone3":
                    klass = "cell cell-zone3"
                elif overlay.get(pos) == "centroid":
                    klass = "cell cell-centroid"
                else:
                    # pathfinding overlays
                    if path and pos in path:
                        klass = "cell cell-path"
                    elif visited and pos in visited:
                        klass = "cell cell-visited"
                    else:
                        klass = "cell cell-empty"

            html += f'<div class="{klass}" title="{pos}">{cell_emoji(ch)}</div>'

    html += "</div></div>"
    return html

def log_add(msg):
    st.session_state.logs.append(msg)

# ============================================================
# SESSION STATE INIT
# ============================================================

def init_state():
    if "grid_size" not in st.session_state:
        st.session_state.grid_size = 8
    if "use_fixed_grid" not in st.session_state:
        st.session_state.use_fixed_grid = True
    if "grid" not in st.session_state:
        st.session_state.grid = create_grid_fixed_8x8()

    if "visited" not in st.session_state:
        st.session_state.visited = set()
    if "path" not in st.session_state:
        st.session_state.path = []
    if "status" not in st.session_state:
        st.session_state.status = "Idle"
    if "nodes_explored" not in st.session_state:
        st.session_state.nodes_explored = 0
    if "steps_taken" not in st.session_state:
        st.session_state.steps_taken = 0
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "selected_algo" not in st.session_state:
        st.session_state.selected_algo = "BFS"

    # minimax state
    if "minimax_wizard" not in st.session_state:
        st.session_state.minimax_wizard = (0, 0)
    if "minimax_enemy" not in st.session_state:
        st.session_state.minimax_enemy = (5, 0)
    if "minimax_turn" not in st.session_state:
        st.session_state.minimax_turn = 0
    if "minimax_nodes" not in st.session_state:
        st.session_state.minimax_nodes = 0
    if "minimax_result" not in st.session_state:
        st.session_state.minimax_result = ""

    # csp state
    if "csp_walls" not in st.session_state:
        st.session_state.csp_walls = 0
    if "csp_backtracks" not in st.session_state:
        st.session_state.csp_backtracks = 0
    if "csp_path_ok" not in st.session_state:
        st.session_state.csp_path_ok = True

    # kmeans state
    if "kmeans_overlay" not in st.session_state:
        st.session_state.kmeans_overlay = {}
    if "kmeans_iterations" not in st.session_state:
        st.session_state.kmeans_iterations = 0
    if "kmeans_centroids" not in st.session_state:
        st.session_state.kmeans_centroids = []

def reset_visual_state():
    st.session_state.visited = set()
    st.session_state.path = []
    st.session_state.status = "Idle"
    st.session_state.nodes_explored = 0
    st.session_state.steps_taken = 0
    st.session_state.logs = []
    st.session_state.kmeans_overlay = {}
    st.session_state.kmeans_iterations = 0
    st.session_state.kmeans_centroids = []
    st.session_state.csp_walls = 0
    st.session_state.csp_backtracks = 0
    st.session_state.csp_path_ok = True
    st.session_state.minimax_turn = 0
    st.session_state.minimax_nodes = 0
    st.session_state.minimax_result = ""
    st.session_state.minimax_wizard = (0, 0)
    st.session_state.minimax_enemy = (5, 0)

init_state()

# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="card">
  <div class="hero-title">AI Quest Game</div>
  <div class="hero-subtitle">Visualizing AI Algorithms</div>
  <div class="muted">
    ✅ BFS • ✅ DFS • ✅ A* • ✅ Hill Climbing • ✅ Minimax • ✅ CSP • ✅ K-Means
  </div>
</div>
""",
    unsafe_allow_html=True,
)
st.write("")

# ============================================================
# SIDEBAR CONTROLS
# ============================================================

with st.sidebar:
    st.markdown("## 🎛️ Controls")

    st.session_state.selected_algo = st.selectbox(
        "🤖 Select Algorithm",
        ["BFS", "DFS", "A*", "Hill Climbing", "Minimax", "CSP", "K-Means"],
        index=["BFS", "DFS", "A*", "Hill Climbing", "Minimax", "CSP", "K-Means"].index(st.session_state.selected_algo),
    )

    speed = st.slider("⏱️ Speed (delay per step)", 0.0, 0.6, 0.15, 0.05)

    st.markdown("---")
    st.markdown("### 🧩 Grid Settings")

    use_fixed = st.toggle("Use fixed 8x8 grid (best for viva)", value=st.session_state.use_fixed_grid)
    st.session_state.use_fixed_grid = use_fixed

    if use_fixed:
        st.session_state.grid_size = 8
        wall_prob = 0.22
        st.caption("Using your fixed 8x8 grid for consistent results.")
    else:
        st.session_state.grid_size = st.select_slider("Grid Size", options=[6, 8, 10, 12], value=st.session_state.grid_size)
        wall_prob = st.slider("🧱 Wall Density (random grid)", 0.05, 0.40, 0.22, 0.01)

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧪 Generate New Grid", use_container_width=True):
            if st.session_state.use_fixed_grid:
                st.session_state.grid = create_grid_fixed_8x8()
            else:
                st.session_state.grid = generate_grid(st.session_state.grid_size, wall_prob)
            reset_visual_state()
            log_add("🧪 New grid generated.")

    with c2:
        if st.button("🧼 Reset", use_container_width=True):
            reset_visual_state()
            log_add("🧼 Reset done (kept grid).")

    run_clicked = st.button("▶️ Run Algorithm", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("### 💡 Key Insights")
    st.caption("1) BFS: shortest but explores more")
    st.caption("2) DFS: fast but not always shortest")
    st.caption("3) A*: heuristic power (fewer nodes)")
    st.caption("4) Hill Climbing: can get stuck → restarts")
    st.caption("5) Minimax: adversarial (wizard vs enemy)")
    st.caption("6) CSP: validates solvable dungeon")
    st.caption("7) K-Means: clusters zones (not pathfinding)")

# ============================================================
# MAIN LAYOUT (Grid + Status + Logs)
# ============================================================

left, right = st.columns([1.4, 1], gap="large")

with left:
    st.markdown(
        '<div class="card"><h3 style="margin:0;">🗺️ Main Grid Display</h3>'
        '<div class="muted">A=🤖, G=🏆, X=⬛ | Minimax: W=🧙, E=👾 | K-Means: Zones colored</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    grid_placeholder = st.empty()

with right:
    st.markdown('<div class="card"><h3 style="margin:0 0 10px 0;">📊 Status Panel</h3>', unsafe_allow_html=True)

    path_len = (len(st.session_state.path) - 1) if st.session_state.path else 0

    extra_line = ""
    if st.session_state.selected_algo == "Minimax":
        extra_line = f"<div class='badge'>⚔️ <strong>Turn:</strong> {st.session_state.minimax_turn}</div>" \
                     f"<div class='badge'>🧮 <strong>Nodes Evaluated:</strong> {st.session_state.minimax_nodes}</div>"
        if st.session_state.minimax_result:
            extra_line += f"<div class='badge'>🏁 <strong>Result:</strong> {st.session_state.minimax_result}</div>"
    if st.session_state.selected_algo == "CSP":
        extra_line = f"<div class='badge'>🧱 <strong>Walls placed:</strong> {st.session_state.csp_walls}</div>" \
                     f"<div class='badge'>↩️ <strong>Backtracks:</strong> {st.session_state.csp_backtracks}</div>" \
                     f"<div class='badge'>✅ <strong>Path valid:</strong> {st.session_state.csp_path_ok}</div>"
    if st.session_state.selected_algo == "K-Means":
        extra_line = f"<div class='badge'>🔁 <strong>Iterations:</strong> {st.session_state.kmeans_iterations}</div>"

    status_html = f"""
    <div class="badges">
      <div class="badge">🧠 <strong>Algorithm:</strong> {st.session_state.selected_algo}</div>
      <div class="badge">📌 <strong>Status:</strong> {st.session_state.status}</div>
      <div class="badge">🧭 <strong>Nodes Explored:</strong> {st.session_state.nodes_explored}</div>
      <div class="badge">🛤️ <strong>Path Length:</strong> {path_len}</div>
      <div class="badge">👣 <strong>Steps Taken:</strong> {st.session_state.steps_taken}</div>
      {extra_line}
    </div>
    """
    st.markdown(status_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="card"><h3 style="margin:0 0 10px 0;">🧾 Log Panel</h3>', unsafe_allow_html=True)
    log_placeholder = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# INITIAL RENDER
# ============================================================

def render_current_view():
    algo = st.session_state.selected_algo

    # Choose which grid is displayed
    if algo == "Minimax":
        g = minimax_grid_fixed_6x6()
        # put W/E on top for visualization
        wr, wc = st.session_state.minimax_wizard
        er, ec = st.session_state.minimax_enemy
        # copy for display
        display = [list(row) for row in g]
        display[wr][wc] = "W"
        display[er][ec] = "E"
        grid_html = render_grid_html(display, visited=set(), path=[], overlay={})
    elif algo == "K-Means":
        grid_html = render_grid_html(st.session_state.grid, visited=set(), path=[], overlay=st.session_state.kmeans_overlay)
    elif algo == "CSP":
        # grid might be modified during run; we store in st.session_state.grid directly
        grid_html = render_grid_html(st.session_state.grid, visited=set(), path=[], overlay={})
    else:
        grid_html = render_grid_html(st.session_state.grid, visited=st.session_state.visited, path=st.session_state.path, overlay={})

    grid_placeholder.markdown(grid_html, unsafe_allow_html=True)

    logs_text = "\n".join(st.session_state.logs) if st.session_state.logs else "No logs yet…"
    log_placeholder.markdown(f'<div class="logbox">{logs_text}</div>', unsafe_allow_html=True)

render_current_view()

# ============================================================
# RUN VISUALIZATION (per algorithm)
# ============================================================

def run_algorithm(selected_algo, delay):
    # Reset run-specific visuals, keep current grid
    st.session_state.visited = set()
    st.session_state.path = []
    st.session_state.nodes_explored = 0
    st.session_state.steps_taken = 0
    st.session_state.logs = []
    st.session_state.kmeans_overlay = {}
    st.session_state.kmeans_iterations = 0
    st.session_state.kmeans_centroids = []
    st.session_state.csp_walls = 0
    st.session_state.csp_backtracks = 0
    st.session_state.csp_path_ok = True
    st.session_state.minimax_turn = 0
    st.session_state.minimax_nodes = 0
    st.session_state.minimax_result = ""

    st.session_state.status = "Running"
    log_add(f"🚀 Running {selected_algo}...")

    # -------------------------
    # PATHFINDING ALGORITHMS
    # -------------------------
    if selected_algo in ["BFS", "DFS", "A*", "Hill Climbing"]:
        grid = st.session_state.grid
        start = find_position(grid, "A")
        goal = find_position(grid, "G")

        if start is None or goal is None:
            st.session_state.status = "Completed"
            log_add("❌ Start or Goal missing in grid.")
            return

        if selected_algo == "BFS":
            gen = bfs_steps(grid, start, goal)
        elif selected_algo == "DFS":
            gen = dfs_steps(grid, start, goal)
        elif selected_algo == "A*":
            gen = astar_steps(grid, start, goal)
        else:
            gen = hill_climbing_steps(grid, start, goal)

        found_path = False
        for visited, path, msg in gen:
            st.session_state.visited = set(visited)
            st.session_state.nodes_explored = len(st.session_state.visited)
            st.session_state.steps_taken += 1

            if msg:
                log_add(msg)

            if path:
                st.session_state.path = list(path)
                found_path = True

            render_current_view()
            time.sleep(delay)

            if found_path:
                break

        st.session_state.status = "Completed"
        log_add("✅ Completed." if found_path else "⚠️ Completed (no path found).")
        render_current_view()
        return

    # -------------------------
    # MINIMAX
    # -------------------------
    if selected_algo == "Minimax":
        mini_grid = minimax_grid_fixed_6x6()
        wizard_start = (0, 0)
        enemy_start = (5, 0)
        goal_pos = (5, 5)

        st.session_state.minimax_wizard = wizard_start
        st.session_state.minimax_enemy = enemy_start

        gen = minimax_game_steps(mini_grid, wizard_start, enemy_start, goal_pos, depth=3, max_turns=12)

        for wizard, enemy, _path, stats, msg in gen:
            st.session_state.minimax_wizard = wizard
            st.session_state.minimax_enemy = enemy

            st.session_state.steps_taken += 1
            st.session_state.minimax_turn = stats.get("turn", st.session_state.minimax_turn)
            st.session_state.minimax_nodes = stats.get("nodes", st.session_state.minimax_nodes)
            if stats.get("result"):
                st.session_state.minimax_result = stats["result"]

            if msg:
                log_add(msg)

            render_current_view()
            time.sleep(delay)

            if st.session_state.minimax_result:
                break

        st.session_state.status = "Completed"
        log_add("✅ Minimax completed.")
        render_current_view()
        return

    # -------------------------
    # CSP
    # -------------------------
    if selected_algo == "CSP":
        # CSP works on the main grid (8x8 or random)
        base_grid = st.session_state.grid
        start = find_position(base_grid, "A")
        goal = find_position(base_grid, "G")

        gen = csp_steps(base_grid, start, goal, attempts_limit=8, seed=7)

        for new_grid, stats, msg in gen:
            # Update the grid itself (so user sees walls being kept/removed)
            st.session_state.grid = [list(row) for row in new_grid]
            st.session_state.csp_walls = stats["walls"]
            st.session_state.csp_backtracks = stats["backtracks"]
            st.session_state.csp_path_ok = stats["path_ok"]

            st.session_state.steps_taken += 1
            st.session_state.nodes_explored = stats["attempts"]  # simple stat for CSP

            if msg:
                log_add(msg)

            render_current_view()
            time.sleep(delay)

        st.session_state.status = "Completed"
        log_add("✅ CSP validation completed.")
        render_current_view()
        return

    # -------------------------
    # K-MEANS
    # -------------------------
    if selected_algo == "K-Means":
        grid = st.session_state.grid
        k = 3

        gen = kmeans_steps(grid, k=k, max_iterations=20, seed=5)

        # We'll build overlay coloring after each iteration
        for clusters, centroids, stats, msg in gen:
            st.session_state.steps_taken += 1
            st.session_state.kmeans_iterations = stats.get("iterations", 0)
            st.session_state.kmeans_centroids = stats.get("centroids", [])

            if msg:
                log_add(msg)

            overlay = {}
            if clusters is not None:
                # color zones
                for i, cells in clusters.items():
                    tag = "zone1" if i == 0 else ("zone2" if i == 1 else "zone3")
                    for p in cells:
                        overlay[p] = tag

                # mark centroids
                for cent in centroids:
                    overlay[cent] = "centroid"

            st.session_state.kmeans_overlay = overlay
            st.session_state.nodes_explored = len(get_all_open_cells(grid))  # clustered cells count
            render_current_view()
            time.sleep(delay)

        st.session_state.status = "Completed"
        log_add("✅ K-Means completed.")
        render_current_view()
        return

# Trigger run
if run_clicked:
    run_algorithm(st.session_state.selected_algo, speed)

# ============================================================
# RESET EVERYTHING BUTTON
# ============================================================
st.write("")
if st.button("🔄 Reset Everything (Clear + New Grid)", use_container_width=True):
    if st.session_state.use_fixed_grid:
        st.session_state.grid = create_grid_fixed_8x8()
    else:
        st.session_state.grid = generate_grid(st.session_state.grid_size, 0.22)
    reset_visual_state()
    log_add("🔄 Full reset done.")
    st.rerun()

# ============================================================
# FOOTER
# ============================================================
st.caption("AI Quest Game • Streamlit • One-file UI + Logic • BFS/DFS/A*/HC/Minimax/CSP/K-Means")
