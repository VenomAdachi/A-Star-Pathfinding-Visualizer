import pygame
pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

ROW_NUMBER = 20
COLUMN_NUMBER = 20
BLOCK_SIZE = 30
BLOCK_COLOR = (0, 150, 255)

GRID_WIDTH = COLUMN_NUMBER * BLOCK_SIZE
GRID_HEIGHT = ROW_NUMBER * BLOCK_SIZE

BG_COLOR = (0, 0, 0)
GRID_COLOR = (255, 255, 255)
HOVER_COLOR = (255, 255, 255)

def draw_grid(surface):
    for x in range(0, GRID_WIDTH + 1, BLOCK_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, GRID_HEIGHT))

    for y in range(0, GRID_HEIGHT + 1, BLOCK_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (GRID_WIDTH, y))

def draw_cells(surface, grid):
    for r in range(ROW_NUMBER):
        for c in range(COLUMN_NUMBER):
            if grid[r][c] == 1:
                x = c * BLOCK_SIZE
                y = r * BLOCK_SIZE
                pygame.draw.rect(surface, BLOCK_COLOR, (x, y, BLOCK_SIZE, BLOCK_SIZE))

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
    pygame.draw.rect(surface, HOVER_COLOR, (x, y, BLOCK_SIZE, BLOCK_SIZE))


def main():
    running = True
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Grid")
    clock = pygame.time.Clock()

    grid_cells = [[0 for _ in range(COLUMN_NUMBER)] for _ in range(ROW_NUMBER)]
    grid_cells[4][7] = 1

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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