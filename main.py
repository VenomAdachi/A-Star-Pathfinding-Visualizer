import pygame
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

#BFS Algorithim Based Functions

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
    
    path = []
    current = destination

    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()

    return explored_order, path

def display_bfs(grid_cells, explored, path):
    for row, column in explored:
        if grid_cells[row][column] == EMPTY:
            grid_cells[row][column] = VISITED
    
    for row, column in path:
        if grid_cells[row][column] not in (START, DESTINATION):
            grid_cells[row][column] = PATH

def clear_bfs(grid, explored, path):
    for row, column in explored:
        if grid[row][column] == VISITED:
            grid[row][column] = EMPTY

    for row, column in path:
        if grid[row][column] == PATH:
            grid[row][column] = EMPTY



def main():
    running = True
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Grid")
    clock = pygame.time.Clock()
    
    start_cell = None
    destination_cell = None
    explored = []
    path = []

    grid_cells = [[EMPTY for _ in range(COLUMN_NUMBER)] for _ in range(ROW_NUMBER)]

    while running:

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
                        clear_bfs(grid_cells, explored, path)
                        explored, path = bfs(grid_cells, start_cell, destination_cell)
                        display_bfs(grid_cells, explored, path)

                if event.key == pygame.K_r:
                    clear_bfs(grid_cells, explored, path)
                    explored = []
                    path = []

                if event.key == pygame.K_c:
                    grid_cells = [
                        [EMPTY for _ in range (COLUMN_NUMBER)] 
                        for _ in range (ROW_NUMBER)
                        ]
                    
                    start_cell = None
                    destination_cell = None
                    explored = []
                    path = []

        screen.fill(BG_COLOR)

        draw_cells(screen, grid_cells)

        hovered_cell = get_mouse_cell(pygame.mouse.get_pos())

        if hovered_cell is not None:
            row, column = hovered_cell
            draw_hover(screen, row, column)

        draw_grid(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()