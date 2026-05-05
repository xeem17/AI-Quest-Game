# ============================================================
# AI QUEST GAME — Streamlit Modern UI + "Full Marks" Core Logic
# ============================================================
# What you asked:
# - Replace old core logic with your new CSP-based dungeon generator
# - Keep the previous modern UI (cards, status panel, logs, grid HTML)
# - Keep everything in ONE file
# - Beginner-friendly
#
# Included algorithms (from your full fixed version):
# ✅ BFS, ✅ DFS, ✅ A*, ✅ Hill Climbing (restart)
#
# Notes:
# - Grid is large (20x24). We auto-shrink cell size for UI.
# - Path highlighting works for BFS/DFS/A*.
# - Hill climbing returns a "walk trail" (not guaranteed shortest).
# ============================================================

import streamlit as st
import random
import time
from collections import deque

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
# CONFIG (your "full marks" defaults)
# ============================================================
DEFAULT_ROWS = 20
DEFAULT_COLS = 24

# ============================================================
# MODERN CSS (cards + grid) + visibility
# ============================================================
APP_CSS = """
<style>
.block-container { max-width: 1150px; padding-top: 1.1rem; padding-bottom: 2rem; }

.card, .card * { color: #0f172a !important; }
.hero-subtitle, .muted { color: rgba(15, 23, 42, 0.70) !important; }

.card {
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 16px 16px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.hero-title { font-size: 2.2rem; font-weight: 850; letter-spacing: -0.02em; margin: 0; }
.hero-subtitle { margin-top: 0.25rem; font-size: 1.05rem; }
.muted { font-size: 0.95rem; }

.stApp {
  background: radial-gradient(1200px 800px at 20% 0%, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0.00) 60%),
              #070b14;
}

.grid-wrap { display: flex; justify-content: center; }
.board {
  display: grid;
  gap: 7px;
  padding: 14px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
  border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.14);
}

.cell {
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0,0,0,0.06);
  user-select: none;
  font-weight: 700;
}

.cell-empty   { background: #f1f5f9; color: #334155; }
.cell-wall    { background: #111827; color: #e5e7eb; }
.cell-agent   { background: #e0f2fe; color: #0284c7; border-color: rgba(2,132,199,0.25); }
.cell-goal    { background: #fef3c7; color: #b45309; border-color: rgba(180,83,9,0.25); }

.cell-visited { background: #dcfce7; color: #166534; border-color: rgba(22,101,52,0.22); }
.cell-path    { background: #a7f3d0; color: #065f46; border-color: rgba(6,95,70,0.25); }

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

html, body, [class*="css"]  { color: #e5e7eb; }
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

# ============================================================
# SECTION 1: CSP-BASED DUNGEON GENERATION (your logic)
# (Written in a way that supports variable rows/cols)
# ============================================================

def create_empty_dungeon(rows, cols):
    """Create grid filled with walls."""
    return [["X" for _ in range(cols)] for _ in range(rows)]

def carve_guaranteed_path(grid, start, goal):
    """Carve a path from start to goal."""
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
    """Add random walkable cells."""
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
            res.append((nr,nc))
    return res

def path_exists_bfs(grid, start, goal):
    """BFS check for CSP constraint."""
    queue = deque([start])
    visited = set([start])

    while queue:
        r, c = queue.popleft()
        if (r, c) == goal:
            return True
        for nb in get_neighbors(r, c, grid):
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return False

def generate_dungeon(rows, cols, open_prob=0.25, max_tries=200):
    """Full CSP-based dungeon generation (guarantees solvable)."""
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

    # fallback (should be rare)
    grid = create_empty_dungeon(rows, cols)
    carve_guaranteed_path(grid, start, goal)
    grid[start[0]][start[1]] = "A"
    grid[goal[0]][goal[1]] = "G"
    return grid

def find_symbol(grid, symbol):
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == symbol:
                return (r, c)
    return None

# ============================================================
# SECTION 2: Algorithms (your core logic, but return logs + stats)
# ============================================================

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

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
    queue = deque([start])
    visited = set([start])
    parent = {}
    nodes = 0
    logs = [f"🚦 BFS started at {start}"]

    while queue:
        cur = queue.popleft()
        nodes += 1
        logs.append(f"🔍 Exploring {cur}")

        if cur == goal:
            logs.append("🏆 Goal reached!")
            break

        for nb in get_neighbors(*cur, grid):
            if nb not in visited:
                visited.add(nb)
                parent[nb] = cur
                queue.append(nb)
                logs.append(f"➕ Enqueue {nb}")

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
                logs.append(f"➕ Push {nb}")

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
                logs.append(f"➕ Update {nb} (f={new_g + heuristic(nb, goal)})")

    path = reconstruct_path(parent, start, goal)
    return visited, path, nodes, logs

def hill_climbing(grid, start, goal, max_restarts=10, max_steps=2000):
    cur = start
    trail = [cur]
    restarts = 0
    steps = 0
    logs = [f"⛰️ Hill Climbing started at {start}"]

    while cur != goal and steps < max_steps:
        steps += 1
        neighbors = get_neighbors(*cur, grid)

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
            if restarts > max_restarts or not neighbors:
                logs.append("❌ Too many restarts. Stopping.")
                break
            cur = random.choice(neighbors)
            logs.append(f"🎲 Restart move to {cur}")
        else:
            cur = best
            logs.append(f"➡️ Move to {cur}")

        trail.append(cur)

    if cur == goal:
        logs.append("🏆 Goal reached!")
    return trail, restarts, logs

# ============================================================
# SECTION 3: UI helpers (Grid render)
# ============================================================

def cell_emoji(ch):
    if ch == "A":
        return "🤖"
    if ch == "G":
        return "🏆"
    if ch == "X":
        return "⬛"
    return ""

def pick_cell_size(rows, cols):
    # smaller for large boards
    max_dim = max(rows, cols)
    if max_dim >= 24:
        return 26
    if max_dim >= 20:
        return 30
    if max_dim >= 12:
        return 38
    return 44

def render_grid_html(grid, visited=None, path=None):
    rows, cols = len(grid), len(grid[0])
    visited = visited or set()
    path = path or []

    size = pick_cell_size(rows, cols)
    font = max(14, int(size * 0.45))
    gap = 6 if size <= 30 else 8

    board_style = f"grid-template-columns: repeat({cols}, {size}px); gap:{gap}px;"
    html = f'<div class="grid-wrap"><div class="board" style="{board_style}">'

    path_set = set(path)

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

            html += f'<div class="{klass}" style="width:{size}px;height:{size}px;font-size:{font}px;" title="{pos}">{cell_emoji(ch)}</div>'

    html += "</div></div>"
    return html

# ============================================================
# SECTION 4: Session State
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

    # Hill climbing extra
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
  <div class="hero-title">AI Quest Game</div>
  <div class="hero-subtitle">Visualizing AI Algorithms</div>
  <div class="muted">CSP-based dungeon generation ✅ • BFS ✅ • DFS ✅ • A* ✅ • Hill Climbing ✅</div>
</div>
""",
    unsafe_allow_html=True,
)
st.write("")

# ============================================================
# SIDEBAR (Controls) — same structure as your earlier UI
# ============================================================

with st.sidebar:
    st.markdown("## 🎛️ Controls")

    st.session_state.selected_algo = st.selectbox(
        "🤖 Select Algorithm",
        ["BFS", "DFS", "A*", "Hill Climbing"],
        index=["BFS", "DFS", "A*", "Hill Climbing"].index(st.session_state.selected_algo),
    )

    speed = st.slider("⏱️ Speed (delay per step)", 0.0, 0.6, 0.10, 0.05)

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

# ============================================================
# MAIN LAYOUT (Grid + Status + Logs)
# ============================================================

left, right = st.columns([1.55, 1], gap="large")

with left:
    st.markdown(
        '<div class="card"><h3 style="margin:0;">🗺️ Main Grid Display</h3>'
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

    # Path length meaning:
    # - BFS/DFS/A*: true shortest? BFS/A* yes; DFS no
    # - Hill Climbing: steps in trail (not optimal)
    if algo == "Hill Climbing":
        path_label = "Trail Steps"
        path_value = max(0, len(st.session_state.path) - 1)
        extra = f"<div class='badge'>🔁 <strong>Restarts:</strong> {st.session_state.hc_restarts}</div>"
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
    grid_placeholder.markdown(
        render_grid_html(st.session_state.grid, st.session_state.visited, st.session_state.path),
        unsafe_allow_html=True,
    )

    logs_text = "\n".join(st.session_state.logs[-250:]) if st.session_state.logs else "No logs yet…"
    log_placeholder.markdown(f'<div class="logbox">{logs_text}</div>', unsafe_allow_html=True)

    render_status_panel()

# initial render
render_view()

# ============================================================
# RUN (simple animation)
# ============================================================

def run_selected_algorithm(delay):
    reset_run_state()
    st.session_state.status = "Running"
    log_add(f"🚀 Running {st.session_state.selected_algo}...")
    render_view()

    grid = st.session_state.grid
    start = find_symbol(grid, "A")
    goal = find_symbol(grid, "G")

    # Ensure symbols exist
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

    else:  # Hill Climbing
        trail, restarts, logs = hill_climbing(grid, start, goal, max_restarts=10)
        # for visualization, we treat trail as "path"
        st.session_state.path = list(trail)
        st.session_state.visited = set(trail)
        st.session_state.nodes_explored = len(set(trail))
        st.session_state.steps_taken = len(logs)
        st.session_state.hc_restarts = restarts
        st.session_state.logs.extend(logs)

    # Optional "animation" effect: just re-render once or do quick incremental
    render_view()
    time.sleep(delay)

    st.session_state.status = "Completed"
    log_add("✅ Completed.")
    render_view()

if run_clicked:
    run_selected_algorithm(speed)

# ============================================================
# FOOTER
# ============================================================
st.caption("AI Quest Game • CSP-based solvable dungeon • Modern Streamlit UI • One file")
