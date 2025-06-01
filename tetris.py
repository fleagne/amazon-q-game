import pygame
import random
import time

# Initialize pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

# Game dimensions
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_MARGIN = 1
SIDEBAR_WIDTH = 200

# Screen dimensions
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Colors for each shape
SHAPE_COLORS = [CYAN, YELLOW, PURPLE, ORANGE, BLUE, GREEN, RED]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 25)
        self.reset_game()

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 0.5  # Time in seconds between automatic piece movements
        self.last_fall_time = time.time()

    def new_piece(self):
        # Choose a random shape
        shape_idx = random.randint(0, len(SHAPES) - 1)
        shape = SHAPES[shape_idx]
        color = SHAPE_COLORS[shape_idx]
        
        # Starting position
        x = GRID_WIDTH // 2 - len(shape[0]) // 2
        y = 0
        
        return {'shape': shape, 'x': x, 'y': y, 'color': color}

    def valid_move(self, piece, x_offset=0, y_offset=0):
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece['x'] + x + x_offset
                    new_y = piece['y'] + y + y_offset
                    
                    # Check if the move is within boundaries
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    
                    # Check if the cell is already occupied
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True

    def rotate_piece(self, piece):
        # Create a new rotated shape (90 degrees clockwise)
        rows = len(piece['shape'])
        cols = len(piece['shape'][0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        
        for y in range(rows):
            for x in range(cols):
                rotated[x][rows - 1 - y] = piece['shape'][y][x]
        
        # Check if the rotated piece is valid
        temp_piece = {'shape': rotated, 'x': piece['x'], 'y': piece['y'], 'color': piece['color']}
        if self.valid_move(temp_piece):
            return temp_piece
        return piece

    def lock_piece(self, piece):
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    # Add the piece to the grid
                    grid_y = piece['y'] + y
                    grid_x = piece['x'] + x
                    if grid_y >= 0:  # Only add if it's within the grid
                        self.grid[grid_y][grid_x] = piece['color']
        
        # Check for completed lines
        self.check_lines()
        
        # Get a new piece
        self.current_piece = self.new_piece()
        
        # Check if game is over
        if not self.valid_move(self.current_piece):
            self.game_over = True

    def check_lines(self):
        lines_to_clear = []
        
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        
        for line in lines_to_clear:
            # Remove the line
            del self.grid[line]
            # Add a new empty line at the top
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        
        # Update score
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += (100 * len(lines_to_clear)) * len(lines_to_clear)  # More points for multiple lines
            
            # Update level
            self.level = self.lines_cleared // 10 + 1
            
            # Increase speed with level
            self.fall_speed = max(0.1, 0.5 - (self.level - 1) * 0.05)

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                # Draw grid cell
                pygame.draw.rect(
                    self.screen,
                    WHITE if self.grid[y][x] else BLACK,
                    [x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - GRID_MARGIN, BLOCK_SIZE - GRID_MARGIN]
                )
                
                # If cell is occupied, draw the block with its color
                if self.grid[y][x]:
                    pygame.draw.rect(
                        self.screen,
                        self.grid[y][x],
                        [x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - GRID_MARGIN, BLOCK_SIZE - GRID_MARGIN]
                    )

    def draw_piece(self, piece):
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    # Only draw if the cell is within the visible grid
                    if piece['y'] + y >= 0:
                        pygame.draw.rect(
                            self.screen,
                            piece['color'],
                            [(piece['x'] + x) * BLOCK_SIZE, (piece['y'] + y) * BLOCK_SIZE, 
                             BLOCK_SIZE - GRID_MARGIN, BLOCK_SIZE - GRID_MARGIN]
                        )

    def draw_sidebar(self):
        # Draw sidebar background
        pygame.draw.rect(
            self.screen,
            (50, 50, 50),
            [GRID_WIDTH * BLOCK_SIZE, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT]
        )
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, 30))
        
        # Draw level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (GRID_WIDTH * BLOCK_SIZE + 10, 70))
        
        # Draw lines cleared
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (GRID_WIDTH * BLOCK_SIZE + 10, 110))
        
        # Draw game over text if game is over
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            self.screen.blit(game_over_text, (GRID_WIDTH * BLOCK_SIZE + 10, 200))
            
            restart_text = self.font.render("Press R to restart", True, WHITE)
            self.screen.blit(restart_text, (GRID_WIDTH * BLOCK_SIZE + 10, 240))

    def run(self):
        running = True
        
        while running:
            current_time = time.time()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if not self.game_over:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            if self.valid_move(self.current_piece, x_offset=-1):
                                self.current_piece['x'] -= 1
                        elif event.key == pygame.K_RIGHT:
                            if self.valid_move(self.current_piece, x_offset=1):
                                self.current_piece['x'] += 1
                        elif event.key == pygame.K_DOWN:
                            if self.valid_move(self.current_piece, y_offset=1):
                                self.current_piece['y'] += 1
                        elif event.key == pygame.K_UP:
                            self.current_piece = self.rotate_piece(self.current_piece)
                        elif event.key == pygame.K_SPACE:
                            # Hard drop
                            while self.valid_move(self.current_piece, y_offset=1):
                                self.current_piece['y'] += 1
                            self.lock_piece(self.current_piece)
                else:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        self.reset_game()
            
            # Automatic falling
            if not self.game_over and current_time - self.last_fall_time > self.fall_speed:
                if self.valid_move(self.current_piece, y_offset=1):
                    self.current_piece['y'] += 1
                else:
                    self.lock_piece(self.current_piece)
                self.last_fall_time = current_time
            
            # Draw everything
            self.screen.fill(BLACK)
            self.draw_grid()
            if not self.game_over:
                self.draw_piece(self.current_piece)
            self.draw_sidebar()
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = Tetris()
    game.run()
