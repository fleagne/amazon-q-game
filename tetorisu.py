import pygame
import random
import sys
import time

# Initialize pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Squirrel colors (Puyo Puyo style)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
SQUIRREL_COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE]

# Hand colors (2048 style)
HAND_COLORS = {
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

# Text colors
TEXT_COLORS = {
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
BLOCK_SIZE = 40
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200

# Screen dimensions
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Cell types
EMPTY = 0
SQUIRREL = 1  # Followed by color index
HAND = 2      # Followed by value (2, 4, 8, etc.)

# Tetris shapes (modified to include squirrels and hands)
SHAPES = [
    # I shape
    [[{'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)} for _ in range(4)]],
    
    # O shape
    [[{'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}],
     [{'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}]],
    
    # T shape
    [[{'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}],
     [None, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      None]],
    
    # L shape
    [[{'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}],
     [{'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      None, 
      None]],
    
    # J shape
    [[{'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}],
     [None, 
      None, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}]],
    
    # S shape
    [[None, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}],
     [{'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      None]],
    
    # Z shape
    [[{'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      None],
     [None, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}, 
      {'type': SQUIRREL, 'value': random.choice(SQUIRREL_COLORS)}]]
]

# Special shapes with hands
HAND_SHAPES = [
    # Single hand
    [[{'type': HAND, 'value': 2}]],
    
    # Double hand
    [[{'type': HAND, 'value': 2}, {'type': HAND, 'value': 2}]],
    
    # Triple hand
    [[{'type': HAND, 'value': 2}, {'type': HAND, 'value': 2}, {'type': HAND, 'value': 2}]]
]

class TetoRisu:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TetoRisu - Te (Hand) + To (And) + Risu (Squirrel)")
        self.clock = pygame.time.Clock()
        self.fonts = {
            'small': pygame.font.SysFont('Arial', 16),
            'medium': pygame.font.SysFont('Arial', 24),
            'large': pygame.font.SysFont('Arial', 32),
            'xlarge': pygame.font.SysFont('Arial', 48)
        }
        
        # Load images
        self.squirrel_img = pygame.Surface((BLOCK_SIZE-4, BLOCK_SIZE-4))
        self.squirrel_img.fill(RED)  # Placeholder for squirrel image
        self.hand_img = pygame.Surface((BLOCK_SIZE-4, BLOCK_SIZE-4))
        self.hand_img.fill(HAND_COLORS[2])  # Placeholder for hand image
        
        self.reset_game()

    def reset_game(self):
        # Initialize grid with empty cells
        self.grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 0.5  # Time in seconds between automatic piece movements
        self.last_fall_time = time.time()
        self.combo_count = 0
        self.max_hand_value = 2

    def new_piece(self):
        # Choose between squirrel piece and hand piece
        if random.random() < 0.8:  # 80% chance for squirrel piece
            shape_idx = random.randint(0, len(SHAPES) - 1)
            shape = SHAPES[shape_idx]
            
            # Randomize colors for each cell
            for row in shape:
                for i in range(len(row)):
                    if row[i] is not None:
                        row[i]['value'] = random.choice(SQUIRREL_COLORS)
        else:  # 20% chance for hand piece
            shape_idx = random.randint(0, len(HAND_SHAPES) - 1)
            shape = HAND_SHAPES[shape_idx]
        
        # Starting position
        x = GRID_WIDTH // 2 - len(shape[0]) // 2
        y = 0
        
        return {'shape': shape, 'x': x, 'y': y}

    def valid_move(self, piece, x_offset=0, y_offset=0):
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell is not None:
                    new_x = piece['x'] + x + x_offset
                    new_y = piece['y'] + y + y_offset
                    
                    # Check if the move is within boundaries
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    
                    # Check if the cell is already occupied
                    if new_y >= 0 and self.grid[new_y][new_x] != EMPTY:
                        return False
        return True

    def rotate_piece(self, piece):
        # Create a new rotated shape (90 degrees clockwise)
        rows = len(piece['shape'])
        cols = len(piece['shape'][0])
        rotated = [[None for _ in range(rows)] for _ in range(cols)]
        
        for y in range(rows):
            for x in range(cols):
                if piece['shape'][y][x] is not None:
                    rotated[x][rows - 1 - y] = piece['shape'][y][x]
        
        # Check if the rotated piece is valid
        temp_piece = {'shape': rotated, 'x': piece['x'], 'y': piece['y']}
        if self.valid_move(temp_piece):
            return temp_piece
        return piece

    def lock_piece(self, piece):
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell is not None:
                    # Add the piece to the grid
                    grid_y = piece['y'] + y
                    grid_x = piece['x'] + x
                    if grid_y >= 0:  # Only add if it's within the grid
                        self.grid[grid_y][grid_x] = cell
        
        # Check for matches and merges
        self.check_matches()
        
        # Check for completed lines
        self.check_lines()
        
        # Get a new piece
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        # Check if game is over
        if not self.valid_move(self.current_piece):
            self.game_over = True

    def check_matches(self):
        # Check for squirrel matches (Puyo Puyo style)
        matches_found = True
        chain_count = 0
        
        while matches_found:
            matches_found = False
            visited = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
            
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    if (self.grid[y][x] != EMPTY and 
                        isinstance(self.grid[y][x], dict) and 
                        self.grid[y][x]['type'] == SQUIRREL and 
                        not visited[y][x]):
                        
                        # Find all connected squirrels of the same color
                        color = self.grid[y][x]['value']
                        connected = []
                        self.find_connected_squirrels(x, y, color, visited, connected)
                        
                        # If 4 or more connected, transform them into hands
                        if len(connected) >= 4:
                            matches_found = True
                            for cx, cy in connected:
                                self.grid[cy][cx] = {'type': HAND, 'value': 2}
                            
                            # Add score based on number of squirrels popped
                            points = len(connected) * 10 * (chain_count + 1)
                            self.score += points
            
            if matches_found:
                chain_count += 1
                self.combo_count = max(self.combo_count, chain_count)
                
                # Apply gravity after matches
                self.apply_gravity()
                
                # Check for hand merges (2048 style)
                self.check_hand_merges()
                
                # Add a small delay to show the chain reaction
                self.draw()
                pygame.display.flip()
                pygame.time.delay(300)

    def find_connected_squirrels(self, x, y, color, visited, connected):
        # Find all connected squirrels of the same color using DFS
        if (x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT or 
            visited[y][x] or self.grid[y][x] == EMPTY or 
            not isinstance(self.grid[y][x], dict) or
            self.grid[y][x]['type'] != SQUIRREL or 
            self.grid[y][x]['value'] != color):
            return
        
        visited[y][x] = True
        connected.append((x, y))
        
        # Check all four directions
        self.find_connected_squirrels(x + 1, y, color, visited, connected)
        self.find_connected_squirrels(x - 1, y, color, visited, connected)
        self.find_connected_squirrels(x, y + 1, color, visited, connected)
        self.find_connected_squirrels(x, y - 1, color, visited, connected)

    def check_hand_merges(self):
        # Check for hand merges (2048 style)
        merged = True
        
        while merged:
            merged = False
            
            # Check horizontal merges
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH - 1):
                    if (self.grid[y][x] != EMPTY and 
                        isinstance(self.grid[y][x], dict) and 
                        self.grid[y][x]['type'] == HAND and 
                        self.grid[y][x+1] != EMPTY and 
                        isinstance(self.grid[y][x+1], dict) and 
                        self.grid[y][x+1]['type'] == HAND and 
                        self.grid[y][x]['value'] == self.grid[y][x+1]['value']):
                        
                        # Merge hands
                        value = self.grid[y][x]['value'] * 2
                        self.grid[y][x] = {'type': HAND, 'value': value}
                        self.grid[y][x+1] = EMPTY
                        
                        # Update score and max hand value
                        self.score += value
                        self.max_hand_value = max(self.max_hand_value, value)
                        merged = True
            
            # Check vertical merges
            for y in range(GRID_HEIGHT - 1):
                for x in range(GRID_WIDTH):
                    if (self.grid[y][x] != EMPTY and 
                        isinstance(self.grid[y][x], dict) and 
                        self.grid[y][x]['type'] == HAND and 
                        self.grid[y+1][x] != EMPTY and 
                        isinstance(self.grid[y+1][x], dict) and 
                        self.grid[y+1][x]['type'] == HAND and 
                        self.grid[y][x]['value'] == self.grid[y+1][x]['value']):
                        
                        # Merge hands
                        value = self.grid[y][x]['value'] * 2
                        self.grid[y][x] = {'type': HAND, 'value': value}
                        self.grid[y+1][x] = EMPTY
                        
                        # Update score and max hand value
                        self.score += value
                        self.max_hand_value = max(self.max_hand_value, value)
                        merged = True
            
            # Apply gravity after merges
            if merged:
                self.apply_gravity()

    def apply_gravity(self):
        # Apply gravity to make pieces fall
        for x in range(GRID_WIDTH):
            # Start from the bottom and move up
            empty_y = None
            for y in range(GRID_HEIGHT - 1, -1, -1):
                if self.grid[y][x] == EMPTY and empty_y is None:
                    empty_y = y
                elif self.grid[y][x] != EMPTY and empty_y is not None:
                    # Move piece down
                    self.grid[empty_y][x] = self.grid[y][x]
                    self.grid[y][x] = EMPTY
                    empty_y -= 1

    def check_lines(self):
        # Check for completed lines (Tetris style)
        lines_to_clear = []
        
        for y in range(GRID_HEIGHT):
            if all(self.grid[y][x] != EMPTY for x in range(GRID_WIDTH)):
                lines_to_clear.append(y)
        
        for line in lines_to_clear:
            # Remove the line
            del self.grid[line]
            # Add a new empty line at the top
            self.grid.insert(0, [EMPTY for _ in range(GRID_WIDTH)])
        
        # Update score
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += (100 * len(lines_to_clear)) * len(lines_to_clear)
            
            # Update level
            self.level = self.lines_cleared // 10 + 1
            
            # Increase speed with level
            self.fall_speed = max(0.1, 0.5 - (self.level - 1) * 0.05)

    def draw_grid(self):
        # Draw the game grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                # Draw grid cell
                pygame.draw.rect(
                    self.screen,
                    DARK_GRAY,
                    [x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE],
                    1
                )
                
                # If cell is occupied, draw the piece
                if self.grid[y][x] != EMPTY:
                    self.draw_cell(x, y, self.grid[y][x])

    def draw_cell(self, x, y, cell):
        # Draw a cell at the specified position
        if cell['type'] == SQUIRREL:
            # Draw squirrel
            pygame.draw.circle(
                self.screen,
                cell['value'],
                (x * BLOCK_SIZE + BLOCK_SIZE // 2, y * BLOCK_SIZE + BLOCK_SIZE // 2),
                BLOCK_SIZE // 2 - 4
            )
            # Draw eyes
            pygame.draw.circle(
                self.screen,
                BLACK,
                (x * BLOCK_SIZE + BLOCK_SIZE // 3, y * BLOCK_SIZE + BLOCK_SIZE // 3),
                3
            )
            pygame.draw.circle(
                self.screen,
                BLACK,
                (x * BLOCK_SIZE + BLOCK_SIZE * 2 // 3, y * BLOCK_SIZE + BLOCK_SIZE // 3),
                3
            )
        elif cell['type'] == HAND:
            # Draw hand
            pygame.draw.rect(
                self.screen,
                HAND_COLORS.get(cell['value'], (60, 58, 50)),
                [x * BLOCK_SIZE + 2, y * BLOCK_SIZE + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4],
                0,
                5  # Rounded corners
            )
            
            # Draw value text
            font_size = 'medium'
            if cell['value'] >= 1000:
                font_size = 'small'
            
            text = self.fonts[font_size].render(str(cell['value']), True, TEXT_COLORS.get(cell['value'], WHITE))
            text_rect = text.get_rect(center=(x * BLOCK_SIZE + BLOCK_SIZE // 2, y * BLOCK_SIZE + BLOCK_SIZE // 2))
            self.screen.blit(text, text_rect)

    def draw_current_piece(self):
        # Draw the current piece
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell is not None:
                    # Only draw if the cell is within the visible grid
                    if self.current_piece['y'] + y >= 0:
                        self.draw_cell(
                            self.current_piece['x'] + x,
                            self.current_piece['y'] + y,
                            cell
                        )

    def draw_next_piece(self):
        # Draw the next piece in the sidebar
        next_x = GRID_WIDTH * BLOCK_SIZE + 50
        next_y = 150
        
        # Draw the next piece preview
        for y, row in enumerate(self.next_piece['shape']):
            for x, cell in enumerate(row):
                if cell is not None:
                    if cell['type'] == SQUIRREL:
                        pygame.draw.circle(
                            self.screen,
                            cell['value'],
                            (next_x + x * BLOCK_SIZE + BLOCK_SIZE // 2, 
                             next_y + y * BLOCK_SIZE + BLOCK_SIZE // 2),
                            BLOCK_SIZE // 2 - 4
                        )
                        # Draw eyes
                        pygame.draw.circle(
                            self.screen,
                            BLACK,
                            (next_x + x * BLOCK_SIZE + BLOCK_SIZE // 3, 
                             next_y + y * BLOCK_SIZE + BLOCK_SIZE // 3),
                            3
                        )
                        pygame.draw.circle(
                            self.screen,
                            BLACK,
                            (next_x + x * BLOCK_SIZE + BLOCK_SIZE * 2 // 3, 
                             next_y + y * BLOCK_SIZE + BLOCK_SIZE // 3),
                            3
                        )
                    elif cell['type'] == HAND:
                        pygame.draw.rect(
                            self.screen,
                            HAND_COLORS.get(cell['value'], (60, 58, 50)),
                            [next_x + x * BLOCK_SIZE + 2, 
                             next_y + y * BLOCK_SIZE + 2, 
                             BLOCK_SIZE - 4, BLOCK_SIZE - 4],
                            0,
                            5  # Rounded corners
                        )
                        
                        # Draw value text
                        font_size = 'medium'
                        if cell['value'] >= 1000:
                            font_size = 'small'
                        
                        text = self.fonts[font_size].render(str(cell['value']), True, TEXT_COLORS.get(cell['value'], WHITE))
                        text_rect = text.get_rect(center=(next_x + x * BLOCK_SIZE + BLOCK_SIZE // 2, 
                                                         next_y + y * BLOCK_SIZE + BLOCK_SIZE // 2))
                        self.screen.blit(text, text_rect)

    def draw_sidebar(self):
        # Draw sidebar background
        pygame.draw.rect(
            self.screen,
            (50, 50, 50),
            [GRID_WIDTH * BLOCK_SIZE, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT]
        )
        
        # Draw game title
        title_text = self.fonts['large'].render("TetoRisu", True, WHITE)
        self.screen.blit(title_text, (GRID_WIDTH * BLOCK_SIZE + 10, 10))
        
        subtitle_text = self.fonts['small'].render("Te (Hand) + To (And) + Risu (Squirrel)", True, WHITE)
        self.screen.blit(subtitle_text, (GRID_WIDTH * BLOCK_SIZE + 10, 50))
        
        # Draw score
        score_text = self.fonts['medium'].render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, 80))
        
        # Draw level
        level_text = self.fonts['medium'].render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (GRID_WIDTH * BLOCK_SIZE + 10, 110))
        
        # Draw next piece text
        next_text = self.fonts['medium'].render("Next:", True, WHITE)
        self.screen.blit(next_text, (GRID_WIDTH * BLOCK_SIZE + 10, 150))
        
        # Draw the next piece
        self.draw_next_piece()
        
        # Draw max hand value
        max_hand_text = self.fonts['medium'].render(f"Max Hand: {self.max_hand_value}", True, WHITE)
        self.screen.blit(max_hand_text, (GRID_WIDTH * BLOCK_SIZE + 10, 250))
        
        # Draw combo count
        combo_text = self.fonts['medium'].render(f"Max Combo: {self.combo_count}", True, WHITE)
        self.screen.blit(combo_text, (GRID_WIDTH * BLOCK_SIZE + 10, 280))
        
        # Draw game instructions
        instructions = [
            "Controls:",
            "← → : Move",
            "↑ : Rotate",
            "↓ : Soft Drop",
            "Space : Hard Drop",
            "",
            "Match 4+ squirrels",
            "to create hands",
            "",
            "Merge same-value",
            "hands to double them"
        ]
        
        y_pos = 320
        for instruction in instructions:
            instr_text = self.fonts['small'].render(instruction, True, WHITE)
            self.screen.blit(instr_text, (GRID_WIDTH * BLOCK_SIZE + 10, y_pos))
            y_pos += 25
        
        # Draw game over text if game is over
        if self.game_over:
            game_over_text = self.fonts['large'].render("GAME OVER", True, RED)
            self.screen.blit(game_over_text, (GRID_WIDTH * BLOCK_SIZE + 10, 600))
            
            restart_text = self.fonts['medium'].render("Press R to restart", True, WHITE)
            self.screen.blit(restart_text, (GRID_WIDTH * BLOCK_SIZE + 10, 640))

    def draw(self):
        # Draw everything
        self.screen.fill(BLACK)
        self.draw_grid()
        if not self.game_over:
            self.draw_current_piece()
        self.draw_sidebar()

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
                            else:
                                self.lock_piece(self.current_piece)
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
            self.draw()
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TetoRisu()
    game.run()
