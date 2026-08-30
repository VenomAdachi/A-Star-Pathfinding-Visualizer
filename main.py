import pygame
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


def main():
    running = True
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Grid")
    clock = pygame.time.Clock()

    start_cell = None
    destination_cell = None

    grid_cells = [[EMPTY for _ in range(COLUMN_NUMBER)] for _ in range(ROW_NUMBER)]

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONUP:
                clicked_cell = get_mouse_cell(event.pos)

                if clicked_cell is not None:
                    row, column = clicked_cell

                    if event.button == 1:

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