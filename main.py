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

def reset_stats(stats):
    stats["expanded"] = 0
    stats["path_length"] = 0
    stats["runtime_ms"] = 0
    stats["found"] = False

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
    animation_delay = 10 #Delay

    stats = {
        "expanded": 0,
        "path_length": 0,
        "runtime_ms": 0,
        "found": False
    }

    g_scores = {}
    h_scores = {}
    f_scores = {}

    font = pygame.font.Font(None, 28)

    grid_cells = [[EMPTY for _ in range(COLUMN_NUMBER)] for _ in range(ROW_NUMBER)]

    while running:

        current_time = pygame.time.get_ticks()

        if animation_running and not animation_paused:

            if current_time - last_animation_step >= animation_delay:
                still_animating = advance_animation(grid_cells, explore_animation, path_animation)
                last_animation_step = current_time

                if not still_animating:
                    animation_running = False

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

                        start_time = time.perf_counter()

                        # explored, path = bfs(grid_cells, start_cell, destination_cell)
                        explored, path, g_scores, h_scores, f_scores = a_star(grid_cells, start_cell, destination_cell)


                        runtime_ms = (time.perf_counter() - start_time) * 1000

                        explore_animation = deque(explored)
                        path_animation = deque(path)

                        animation_running = True
                        animation_paused = False

                        last_animation_step = pygame.time.get_ticks()

                        stats["expanded"] = len(explored)
                        stats["path_length"] = max(0, len(path) - 1)
                        stats["runtime_ms"] = runtime_ms
                        stats["found"] = bool(path)

                if event.key == pygame.K_r:
                    animation_running = False
                    animation_paused = False
                    explore_animation.clear()
                    path_animation.clear()

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

                    reset_stats(stats)
                    start_cell = None
                    destination_cell = None
                    explored = []
                    path = []

        screen.fill(BG_COLOR)
        draw_text(screen, font, "Algorithm: Breadth First Search (BFS)", 650, 50)
        draw_text(screen, font, f"Expanded Cells: {stats['expanded']}", 650, 130)
        draw_text(screen, font, f"Path Length: {stats['path_length']}", 650, 210)
        draw_text(screen, font, f"Runtime: {stats['runtime_ms']:.3f} ms", 650, 290)

        found_text = "Yes" if stats ["found"] else "No"
        draw_text(screen, font, f"Path Found: {found_text}", 650, 360)


        draw_cells(screen, grid_cells)

        hovered_cell = get_mouse_cell(pygame.mouse.get_pos())
        

        if hovered_cell is not None:
            row, column = hovered_cell
            draw_hover(screen, row, column)

        if hovered_cell in f_scores:
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