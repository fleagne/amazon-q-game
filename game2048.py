import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Tile colors based on value
TILE_COLORS = {
    0: (204, 192, 179),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (60, 58, 50),
    8192: (60, 58, 50)
}

# Text colors based on value
TEXT_COLORS = {
    0: (204, 192, 179),  # Same as tile color to make it invisible
    2: (119, 110, 101),
    4: (119, 110, 101),
    8: (249, 246, 242),
    16: (249, 246, 242),
    32: (249, 246, 242),
    64: (249, 246, 242),
    128: (249, 246, 242),
    256: (249, 246, 242),
    512: (249, 246, 242),
    1024: (249, 246, 242),
    2048: (249, 246, 242),
    4096: (249, 246, 242),
    8192: (249, 246, 242)
}

# Game dimensions
GRID_SIZE = 4
CELL_SIZE = 100
GRID_PADDING = 10
GRID_WIDTH = GRID_SIZE * (CELL_SIZE + GRID_PADDING) + GRID_PADDING
GRID_HEIGHT = GRID_SIZE * (CELL_SIZE + GRID_PADDING) + GRID_PADDING

# Screen dimensions
SCREEN_WIDTH = GRID_WIDTH
SCREEN_HEIGHT = GRID_HEIGHT + 100  # Extra space for score

class Game2048:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2048")
        self.clock = pygame.time.Clock()
        self.fonts = {
            'small': pygame.font.SysFont('Arial', 24),
            'medium': pygame.font.SysFont('Arial', 36),
            'large': pygame.font.SysFont('Arial', 48),
            'xlarge': pygame.font.SysFont('Arial', 64)
        }
        self.reset_game()

    def reset_game(self):
        # Initialize grid with zeros
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.game_over = False
        self.won = False
        
        # Add two initial tiles
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        # Find all empty cells
        empty_cells = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid[y][x] == 0:
                    empty_cells.append((x, y))
        
        if empty_cells:
            # Choose a random empty cell
            x, y = random.choice(empty_cells)
            # 90% chance for a 2, 10% chance for a 4
            self.grid[y][x] = 2 if random.random() < 0.9 else 4
            return True
        return False

    def move(self, direction):
        # direction: 0=up, 1=right, 2=down, 3=left
        moved = False
        
        # Make a copy of the grid for comparison
        old_grid = [row[:] for row in self.grid]
        
        if direction == 0:  # Up
            for x in range(GRID_SIZE):
                # Compact the column (move all non-zero values up)
                column = [self.grid[y][x] for y in range(GRID_SIZE)]
                column = self.compact_line(column)
                
                # Merge tiles
                column, score_increase = self.merge_line(column)
                self.score += score_increase
                
                # Compact again after merging
                column = self.compact_line(column)
                
                # Update the grid
                for y in range(GRID_SIZE):
                    self.grid[y][x] = column[y]
        
        elif direction == 1:  # Right
            for y in range(GRID_SIZE):
                # Get the row and reverse it (to process from right to left)
                row = self.grid[y][:]
                row.reverse()
                
                # Compact the row
                row = self.compact_line(row)
                
                # Merge tiles
                row, score_increase = self.merge_line(row)
                self.score += score_increase
                
                # Compact again after merging
                row = self.compact_line(row)
                
                # Reverse back and update the grid
                row.reverse()
                self.grid[y] = row
        
        elif direction == 2:  # Down
            for x in range(GRID_SIZE):
                # Get the column and reverse it (to process from bottom to top)
                column = [self.grid[y][x] for y in range(GRID_SIZE)]
                column.reverse()
                
                # Compact the column
                column = self.compact_line(column)
                
                # Merge tiles
                column, score_increase = self.merge_line(column)
                self.score += score_increase
                
                # Compact again after merging
                column = self.compact_line(column)
                
                # Reverse back and update the grid
                column.reverse()
                for y in range(GRID_SIZE):
                    self.grid[y][x] = column[y]
        
        elif direction == 3:  # Left
            for y in range(GRID_SIZE):
                # Compact the row
                row = self.compact_line(self.grid[y])
                
                # Merge tiles
                row, score_increase = self.merge_line(row)
                self.score += score_increase
                
                # Compact again after merging
                row = self.compact_line(row)
                
                # Update the grid
                self.grid[y] = row
        
        # Check if the grid changed
        if self.grid != old_grid:
            moved = True
            self.add_new_tile()
            
            # Check for win condition
            if self.check_win():
                self.won = True
            
            # Check for game over
            if self.check_game_over():
                self.game_over = True
        
        return moved

    def compact_line(self, line):
        # Remove zeros and compact the line
        non_zeros = [val for val in line if val != 0]
        return non_zeros + [0] * (len(line) - len(non_zeros))

    def merge_line(self, line):
        # Merge adjacent identical tiles
        score_increase = 0
        for i in range(len(line) - 1):
            if line[i] != 0 and line[i] == line[i + 1]:
                line[i] *= 2
                line[i + 1] = 0
                score_increase += line[i]
        return line, score_increase

    def check_win(self):
        # Check if 2048 tile exists
        for row in self.grid:
            if 2048 in row:
                return True
        return False

    def check_game_over(self):
        # Check if there are any empty cells
        for row in self.grid:
            if 0 in row:
                return False
        
        # Check if there are any possible merges
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                val = self.grid[y][x]
                # Check adjacent cells
                for dx, dy in [(0, 1), (1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        if self.grid[ny][nx] == val:
                            return False
        
        return True

    def draw_tile(self, x, y, value):
        # Calculate position
        pos_x = GRID_PADDING + x * (CELL_SIZE + GRID_PADDING)
        pos_y = GRID_PADDING + y * (CELL_SIZE + GRID_PADDING)
        
        # Draw tile background
        pygame.draw.rect(
            self.screen,
            TILE_COLORS.get(value, (60, 58, 50)),  # Default color for very high values
            [pos_x, pos_y, CELL_SIZE, CELL_SIZE],
            0,
            5  # Rounded corners
        )
        
        # Draw value text (if not 0)
        if value != 0:
            # Choose font size based on number of digits
            font_size = 'large'
            if value >= 1000:
                font_size = 'medium'
            if value >= 10000:
                font_size = 'small'
            
            text = self.fonts[font_size].render(str(value), True, TEXT_COLORS.get(value, WHITE))
            text_rect = text.get_rect(center=(pos_x + CELL_SIZE // 2, pos_y + CELL_SIZE // 2))
            self.screen.blit(text, text_rect)

    def draw_grid(self):
        # Draw background
        pygame.draw.rect(
            self.screen,
            DARK_GRAY,
            [0, 0, GRID_WIDTH, GRID_HEIGHT],
            0,
            10  # Rounded corners
        )
        
        # Draw tiles
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.draw_tile(x, y, self.grid[y][x])

    def draw_score(self):
        # Draw score background
        pygame.draw.rect(
            self.screen,
            DARK_GRAY,
            [0, GRID_HEIGHT + 10, GRID_WIDTH, 80],
            0,
            10  # Rounded corners
        )
        
        # Draw score text
        score_text = self.fonts['medium'].render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, GRID_HEIGHT + 30))

    def draw_game_over(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((GRID_WIDTH, GRID_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = self.fonts['xlarge'].render("Game Over!", True, WHITE)
        text_rect = game_over_text.get_rect(center=(GRID_WIDTH // 2, GRID_HEIGHT // 2 - 30))
        self.screen.blit(game_over_text, text_rect)
        
        # Draw restart instruction
        restart_text = self.fonts['medium'].render("Press R to restart", True, WHITE)
        text_rect = restart_text.get_rect(center=(GRID_WIDTH // 2, GRID_HEIGHT // 2 + 30))
        self.screen.blit(restart_text, text_rect)

    def draw_win(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((GRID_WIDTH, GRID_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Draw win text
        win_text = self.fonts['xlarge'].render("You Win!", True, (255, 255, 0))
        text_rect = win_text.get_rect(center=(GRID_WIDTH // 2, GRID_HEIGHT // 2 - 30))
        self.screen.blit(win_text, text_rect)
        
        # Draw continue instruction
        continue_text = self.fonts['medium'].render("Press C to continue", True, WHITE)
        text_rect = continue_text.get_rect(center=(GRID_WIDTH // 2, GRID_HEIGHT // 2 + 30))
        self.screen.blit(continue_text, text_rect)

    def draw(self):
        # Draw everything
        self.screen.fill(GRAY)
        self.draw_grid()
        self.draw_score()
        
        if self.game_over:
            self.draw_game_over()
        elif self.won:
            self.draw_win()

    def run(self):
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.reset_game()
                    elif self.won:
                        if event.key == pygame.K_c:
                            self.won = False  # Continue playing
                    else:
                        if event.key == pygame.K_UP:
                            self.move(0)
                        elif event.key == pygame.K_RIGHT:
                            self.move(1)
                        elif event.key == pygame.K_DOWN:
                            self.move(2)
                        elif event.key == pygame.K_LEFT:
                            self.move(3)
                        elif event.key == pygame.K_r:
                            self.reset_game()
            
            # Draw everything
            self.draw()
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game2048()
    game.run()
