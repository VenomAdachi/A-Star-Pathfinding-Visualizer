import pygame
import time
import heapq
from collections import deque
pygame.init()

#Screen Dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

#Cells
ROW_NUMBER = 20
COLUMN_NUMBER = 20
BLOCK_SIZE = 30

#Grid Math
GRID_WIDTH = COLUMN_NUMBER * BLOCK_SIZE
GRID_HEIGHT = ROW_NUMBER * BLOCK_SIZE

#General Colors
BG_COLOR = (0, 0, 0)
GRID_COLOR = (255, 255, 255)
HOVER_COLOR = (255, 255, 255)

#Cell States
EMPTY = 0
WALL = 1
START = 2
DESTINATION = 3
VISITED = 4
PATH = 5

#Cell Colors
EMPTY_COLOR = (0, 0, 0) #Black 
WALL_COLOR = (255, 255, 0) #Yellow 
START_COLOR = (0, 150, 255) #Blue
DESTINATION_COLOR = (255, 0, 255) #Magenta
VISITED_COLOR = (0, 128, 0) #Green
PATH_COLOR = (255, 0, 0) #Red

CELL_COLORS = {
    EMPTY: EMPTY_COLOR,
    WALL: WALL_COLOR,
    START: START_COLOR,
    DESTINATION: DESTINATION_COLOR,
    VISITED: VISITED_COLOR,
    PATH: PATH_COLOR,
}

#Drawing Process
def draw_grid(surface):
    for x in range(0, GRID_WIDTH + 1, BLOCK_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, GRID_HEIGHT))

    for y in range(0, GRID_HEIGHT + 1, BLOCK_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (GRID_WIDTH, y))

def draw_cells(surface, grid):
    for r in range(ROW_NUMBER):
        for c in range(COLUMN_NUMBER):
            state = grid[r][c]

            if state != EMPTY:
                color = CELL_COLORS[state]

                x = c * BLOCK_SIZE
                y = r * BLOCK_SIZE

                pygame.draw.rect(surface, color, (x, y, BLOCK_SIZE, BLOCK_SIZE))

def get_mouse_cell(mouse_position):
    mouse_x, mouse_y, = mouse_position

    if mouse_x < GRID_WIDTH and mouse_y < GRID_HEIGHT:
        column = mouse_x // BLOCK_SIZE
        row = mouse_y // BLOCK_SIZE
        return row, column

    return None

def draw_hover(surface, row, column):   
    x = column * BLOCK_SIZE
    y = row * BLOCK_SIZE
    pygame.draw.rect(surface, HOVER_COLOR, (x, y, BLOCK_SIZE, BLOCK_SIZE), 2)

def reconstruct_path(came_from, destination):
    if destination not in came_from:
        return []

    path = []
    current = destination
    
    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()

    return path

def get_neighbors(row, column, grid):
    neighbors = []

    neighbor_up = row - 1, column #every other day im wondering 
    neighbor_down = row +1, column
    neighbor_left = row, column -1 #whats a human being gotta be like?
    neighbor_right = row, column +1

    potential_neighbors = [
        neighbor_up, #whats a way to just be competent 
        neighbor_down,
        neighbor_left,#these sweet instincts ruin my life
        neighbor_right
    ]

    for n in potential_neighbors: #every other day im wondering
        neighbor_row, neighbor_column = n

        in_grid = ( #was it a mistake to try and define
            0 <= neighbor_row < len(grid)
            and 0 <= neighbor_column < len(grid[0])
        )

        if in_grid and grid[neighbor_row][neighbor_column] != WALL:
            neighbors.append(n)

    return neighbors

def bfs(grid, start, destination):
    queue = deque([start])
    visited = {start}
    came_from = {start: None}
    explored_order = []

    while queue:
        current = queue.popleft()
        explored_order.append(current)

        if current == destination:
            break

        current_row, current_column = current
        neighbors = get_neighbors(current_row, current_column, grid)

        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)

    if destination not in came_from:
            return explored_order, []

    path = reconstruct_path(came_from, destination)
    
    return explored_order, path

def manhattan_distance(cell, destination):
    row1, column1, = cell
    row2, column2, = destination

    return abs(row1 - row2) + abs(column1 - column2)

def a_star(grid, start, destination):
    open_queue = []
    came_from = {start: None}

    g_score = {start: 0}

    h_score = {
        start: manhattan_distance(start, destination)
    }

    f_score = {
        start: g_score[start] + h_score[start]
    }

    explored_order = []
    closed = set()
    heapq.heappush(open_queue, (f_score[start], start))

    while open_queue:
        current_f, current = heapq.heappop(open_queue)

        if current in closed:
            continue

        closed.add(current)
        explored_order.append(current)

        if current == destination:
            break

        current_row, current_column = current
        neighbors = get_neighbors(current_row, current_column, grid)

        for neighbor in neighbors:
            tentative_g = g_score[current] + 1

            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                h_score[neighbor] = manhattan_distance(neighbor, destination)
                f_score[neighbor] = (g_score[neighbor] + h_score[neighbor])
                heapq.heappush(open_queue, (f_score[neighbor], neighbor))

    path = reconstruct_path(came_from, destination)

    return explored_order, path, g_score, h_score, f_score

def advance_animation(grid, explore_queue, path_queue):
    if explore_queue: 
        row, column = explore_queue.popleft()

        if grid[row][column] == EMPTY:
            grid[row][column] = VISITED
        return True

    elif path_queue:
        row, column = path_queue.popleft()

        if grid[row][column] not in (START, DESTINATION):
            grid[row][column] = PATH

        return True

    return False
    

def clear_search_visuals(grid):
    for row in range(len(grid)):
        for column in range(len(grid[0])):
            if grid[row][column] in (VISITED, PATH):
                grid[row][column] = EMPTY

def draw_text(surface, font, message, x, y):
    text = font.render(message, True, GRID_COLOR)
    surface.blit(text, (x,y))

def draw_lines(surface, font, lines, x, start_y, spacing=35):
    for i, line in enumerate(lines):
        draw_text(surface, font, line, x, start_y + i * spacing)

def draw_normal_panel(surface, font, selected_algorithm, stats, animation_status, animation_delay):
    found_text = "Yes" if stats["found"] else "No"

    lines = [
        f"Algorithms: {selected_algorithm}",
        "",
        f"Expanded Cells: {stats['expanded']}",
        f"Path Length: {stats['path_length']}",
        f"Runtime: {stats['runtime_ms']:.3f} ms",
        f"Path Found: {found_text}",
        "",
        f"Status: {animation_status}",
        f"Animation Delay: {animation_delay} ms",
        "",
        "Press H to Display Controls"
    ]

    draw_lines(surface, font, lines, 650, 50, 35)

def draw_help_panel(surface, font, help_controls):
    draw_lines(surface, font, help_controls, 650, 50, 35)

def draw_comparison_panel(surface, font, comparison_stats):
    bfs_stats = comparison_stats["BFS"]
    a_star_stats = comparison_stats["A*"]

    draw_text(surface, font, "BFS vs. A* Comparison", 650, 50)
    draw_text(surface, font, "Metric", 650, 110)
    draw_text(surface, font, "BFS", 900, 110)
    draw_text(surface, font, "A*", 1050, 110)

    comparison_rows = [
        ("Expanded Cells", bfs_stats["expanded"], a_star_stats["expanded"]),
        ("Path Length", bfs_stats["path_length"], a_star_stats["path_length"]),
        ("Runtime", f"{bfs_stats['runtime_ms']:.3f} ms", f"{a_star_stats['runtime_ms']:.3f} ms"),
        ("Path Found", "Yes" if bfs_stats["found"] else "No", "Yes" if a_star_stats["found"] else "No")
        ]

    start_y = 150
    spacing = 50

    for i, (label, bfs_value, a_star_value) in enumerate(comparison_rows):
        y = start_y + i * spacing

        draw_text(surface, font, label, 650, y)
        draw_text(surface, font, str(bfs_value), 900, y)
        draw_text(surface, font, str(a_star_value), 1050, y)

    draw_text(surface, font, "Press M to clear the compairison", 650, 400)


def reset_stats(stats):
    stats["expanded"] = 0
    stats["path_length"] = 0
    stats["runtime_ms"] = 0
    stats["found"] = False

def run_search(grid, start, destination, algorithm):
    start_time = time.perf_counter()

    if algorithm == "BFS":
        explored, path = bfs(grid, start, destination)

        g_scores = {}
        h_scores = {}
        f_scores = {}

    elif algorithm == "A*":
        explored, path, g_scores, h_scores, f_scores = a_star(grid, start, destination)

    else:
        raise ValueError("I have no idea how you did this. Congrats!")

    runtime_ms = (time.perf_counter() - start_time) * 1000

    stats = {
        "expanded": len(explored),
        "path_length": max(0, len(path) - 1),
        "runtime_ms": runtime_ms,
        "found": bool(path)
    }

    return explored, path, stats, g_scores, h_scores, f_scores

def run_comparison(grid, start, destination):
    _,_,bfs_stats, _, _, _ = run_search(grid, start, destination, "BFS")

    _, _, a_star_stats, _, _, _ = run_search(grid, start, destination, "A*")

    return {
        "BFS": bfs_stats,
        "A*": a_star_stats
    }

def main():
    running = True
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Grid")
    clock = pygame.time.Clock()
    
    start_cell = None
    destination_cell = None
    explored = []
    path = []

    explore_animation = deque()
    path_animation = deque()

    animation_running = False
    animation_paused = False

    last_animation_step = 0
    animation_delay = 50 #Delay

    stats = {
        "expanded": 0,
        "path_length": 0,
        "runtime_ms": 0,
        "found": False
    }

    g_scores = {}
    h_scores = {}
    f_scores = {}

    selected_algorithm = "BFS"

    show_help = False

    help_control = [
        "CONTROLS",
        "Space = Run Search",
        "B = Select Breadth First Search (BFS)",
        "A = Select A Star (A*)",
        "P = Pause/Resume",
        "N = Step Forward",
        "Up Arrow = Faster",
        "Down Arrow = Slower",
        "R = Reset Search",
        "C = Clear Grid",
        "M = BFS vs. A* Comparison Mode",
        "H = Close Help",
    ]

    comparison_mode = False
    comparison_stats = {
        "BFS": None,
        "A*": None
    }

    font = pygame.font.Font(None, 28)

    grid_cells = [[EMPTY for _ in range(COLUMN_NUMBER)] for _ in range(ROW_NUMBER)]

    while running:

        if animation_paused:
            animation_status = "Paused"
        elif animation_running:
            animation_status = "Running"
        else:
            animation_status = "Idle"

        current_time = pygame.time.get_ticks()

        if animation_running and not animation_paused:

            if current_time - last_animation_step >= animation_delay:
                still_animating = advance_animation(grid_cells, explore_animation, path_animation)
                last_animation_step = current_time

                if not still_animating:
                    animation_running = False
                    animation_paused = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONUP: #Mouse Logic
                clicked_cell = get_mouse_cell(event.pos)

                if clicked_cell is not None:
                    row, column = clicked_cell

                    if event.button == 1 and grid_cells[row][column] == EMPTY:

                        if start_cell is None:
                            start_cell = (row, column)
                            grid_cells[row][column] = START

                        elif destination_cell is None:
                            destination_cell = (row, column)
                            grid_cells[row][column] = DESTINATION

                        elif grid_cells[row][column] == EMPTY:
                            grid_cells[row][column] = WALL

                    if event.button == 3:

                        if clicked_cell == start_cell:
                            start_cell = None

                        if clicked_cell == destination_cell:
                            destination_cell = None

                        grid_cells[row][column] = EMPTY   

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if start_cell is not None and destination_cell is not None:
                        clear_search_visuals(grid_cells)

                        explored, path, stats, g_scores, h_scores, f_scores = run_search(grid_cells, start_cell, destination_cell, selected_algorithm)

                        explore_animation = deque(explored)
                        path_animation = deque(path)

                        animation_running = True
                        animation_paused = False
                        comparison_mode = False

                        last_animation_step = pygame.time.get_ticks()

                if event.key == pygame.K_r:
                    animation_running = False
                    animation_paused = False
                    explore_animation.clear()
                    path_animation.clear()
                    comparison_mode = False

                    g_scores.clear()
                    h_scores.clear()
                    f_scores.clear()

                    reset_stats(stats)

                    clear_search_visuals(grid_cells)
                    explored = []
                    path = []

                if event.key == pygame.K_c:
                    grid_cells = [
                        [EMPTY for _ in range (COLUMN_NUMBER)] 
                        for _ in range (ROW_NUMBER)
                        ]
                    
                    animation_running = False
                    animation_paused = False
                    explore_animation.clear()
                    path_animation.clear()
                    comparison_mode = False

                    g_scores.clear()
                    h_scores.clear()
                    f_scores.clear()

                    reset_stats(stats)
                    start_cell = None
                    destination_cell = None
                    explored = []
                    path = []

                if event.key == pygame.K_b:
                    selected_algorithm = "BFS"
                    clear_search_visuals(grid_cells)

                    animation_running = False
                    animation_paused = False
                    explore_animation.clear()
                    path_animation.clear()
                    reset_stats(stats)
                    comparison_mode = False
                    g_scores.clear()
                    h_scores.clear()
                    f_scores.clear()

                if event.key == pygame.K_a:
                    selected_algorithm = "A*"
                    clear_search_visuals(grid_cells)

                    animation_running = False
                    animation_paused = False
                    explore_animation.clear()
                    path_animation.clear()
                    reset_stats(stats)
                    comparison_mode = False

                if event.key == pygame.K_p:
                    if animation_running:
                        animation_paused = not animation_paused

                if event.key == pygame.K_n:
                    if animation_running:
                        animation_paused = True

                        advance_animation(grid_cells, explore_animation, path_animation)

                    if not explore_animation and not path_animation:
                        animation_paused = False
                        animation_running = False

                if event.key == pygame.K_UP:
                    animation_delay = max(5, animation_delay -10)

                if event.key == pygame.K_DOWN:
                    animation_delay = min(500, animation_delay +10)

                if event.key == pygame.K_h:
                    show_help = not show_help

                if event.key == pygame.K_m:
                    if comparison_mode:
                        comparison_mode = False

                    elif start_cell is not None and destination_cell is not None:
                        animation_running = False
                        animation_paused = False
                        explore_animation.clear()
                        path_animation.clear()

                        clear_search_visuals(grid_cells)

                        comparison_stats = run_comparison(grid_cells, start_cell, destination_cell)
                        comparison_mode = True

        screen.fill(BG_COLOR)

        if show_help:
            draw_help_panel(screen, font, help_control)

        elif comparison_mode:
            draw_comparison_panel(screen, font, comparison_stats)

        else:
            draw_normal_panel(screen, font, selected_algorithm, stats, animation_status, animation_delay)


            # draw_text(screen, font, f"Algorithm: {selected_algorithm}", 650, 50)
            # draw_text(screen, font, f"Expanded Cells: {stats['expanded']}", 650, 130)
            # draw_text(screen, font, f"Path Length: {stats['path_length']}", 650, 210)
            # draw_text(screen, font, f"Runtime: {stats['runtime_ms']:.3f} ms", 650, 290)

            # found_text = "Yes" if stats ["found"] else "No"
            # draw_text(screen, font, f"Path Found: {found_text}", 650, 360)

            # draw_text(screen, font, f"Status: {animation_status}", 650, 450)

            # draw_text(screen, font, f"Animation Delay: {animation_delay} ms", 650, 500)

            # draw_text(screen, font, f"Press H to Display Controls", 650, 550)


        draw_cells(screen, grid_cells)

        hovered_cell = get_mouse_cell(pygame.mouse.get_pos())
        

        if hovered_cell is not None:
            row, column = hovered_cell
            draw_hover(screen, row, column)

        if not show_help and not comparison_mode and hovered_cell in f_scores:
            cell_g = g_scores[hovered_cell]
            cell_h = h_scores[hovered_cell]
            cell_f = f_scores[hovered_cell]
            draw_text(screen, font, f"g: {cell_g}", 900, 130)
            draw_text(screen, font, f"h: {cell_h}", 900, 210)
            draw_text(screen, font, f"f: {cell_f}", 900, 290)

        draw_grid(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()