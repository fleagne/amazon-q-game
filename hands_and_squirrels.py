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
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
SKIN_COLOR = (255, 213, 170)
GREEN = (34, 139, 34)

# Game dimensions
BLOCK_SIZE = 50
GRID_WIDTH = 8
GRID_HEIGHT = 16
SIDEBAR_WIDTH = 250

# Screen dimensions
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Cell types
EMPTY = 0
HAND = 1
SQUIRREL = 2
NUT = 3  # Followed by value (1, 2, 4, 8, etc.)

# Load emoji images
def load_emoji(filename, size=(BLOCK_SIZE-4, BLOCK_SIZE-4)):
    try:
        img = pygame.image.load(f"/home/fleagne/git/amazon-q-game/assets/{filename}")
        return pygame.transform.scale(img, size)
    except:
        # Create placeholder if image not found
        surf = pygame.Surface(size)
        surf.fill(WHITE)
        return surf

# Create placeholder images with emoji-like appearance
def create_placeholder(type_name):
    surf = pygame.Surface((BLOCK_SIZE-4, BLOCK_SIZE-4))
    
    if type_name == "hand":
        surf.fill(SKIN_COLOR)
        # Draw simple hand shape
        pygame.draw.ellipse(surf, SKIN_COLOR, [5, 5, 30, 40])
        pygame.draw.rect(surf, SKIN_COLOR, [10, 25, 25, 20])
    elif type_name == "squirrel":
        surf.fill(LIGHT_BROWN)
        # Draw simple squirrel shape
        pygame.draw.ellipse(surf, BROWN, [10, 5, 25, 20])  # Head
        pygame.draw.ellipse(surf, BROWN, [5, 15, 35, 25])  # Body
        pygame.draw.ellipse(surf, BROWN, [30, 5, 15, 35])  # Tail
    elif type_name == "nut":
        surf.fill(BROWN)
        # Draw simple nut shape
        pygame.draw.ellipse(surf, BROWN, [10, 10, 30, 30])
    
    return surf

# Create placeholder images
HAND_IMG = create_placeholder("hand")
SQUIRREL_IMG = create_placeholder("squirrel")
NUT_IMG = create_placeholder("nut")

# Shapes for falling pieces
SHAPES = [
    # Hand pair
    [[{'type': HAND}, {'type': HAND}]],
    
    # Hand trio
    [[{'type': HAND}, {'type': HAND}, {'type': HAND}]],
    
    # Squirrel pair
    [[{'type': SQUIRREL}, {'type': SQUIRREL}]],
    
    # Squirrel trio
    [[{'type': SQUIRREL}, {'type': SQUIRREL}, {'type': SQUIRREL}]],
    
    # Nut with value 1
    [[{'type': NUT, 'value': 1}]],
    
    # Two nuts with value 1
    [[{'type': NUT, 'value': 1}, {'type': NUT, 'value': 1}]],
    
    # Mixed shapes
    [[{'type': SQUIRREL}, {'type': NUT, 'value': 1}]],
    
    # L shape with squirrel and nut
    [[{'type': SQUIRREL}, None],
     [{'type': SQUIRREL}, {'type': NUT, 'value': 1}]],
    
    # T shape with hands
    [[None, {'type': HAND}, None],
     [{'type': HAND}, {'type': HAND}, {'type': HAND}]],
    
    # Z shape with squirrels and nuts
    [[{'type': SQUIRREL}, {'type': SQUIRREL}, None],
     [None, {'type': NUT, 'value': 1}, {'type': NUT, 'value': 1}]]
]

class HandsAndSquirrels:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hands and Squirrels")
        self.clock = pygame.time.Clock()
        self.fonts = {
            'small': pygame.font.SysFont('Arial', 16),
            'medium': pygame.font.SysFont('Arial', 24),
            'large': pygame.font.SysFont('Arial', 32),
            'xlarge': pygame.font.SysFont('Arial', 48)
        }
        
        self.reset_game()

    def reset_game(self):
        # Initialize grid with empty cells
        self.grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.rows_cleared = 0
        self.fall_time = 0
        self.fall_speed = 0.5  # Time in seconds between automatic piece movements
        self.last_fall_time = time.time()
        self.max_nut_value = 1
        self.squirrels_used = 0

    def new_piece(self):
        # Choose a random shape
        shape_idx = random.randint(0, len(SHAPES) - 1)
        shape = [row[:] for row in SHAPES[shape_idx]]  # Deep copy
        
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
        
        # Try wall kicks
        for x_offset in [-1, 1, -2, 2]:
            temp_piece = {'shape': rotated, 'x': piece['x'] + x_offset, 'y': piece['y']}
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
        
        # Process game mechanics
        self.process_hands()
        self.merge_nuts()
        self.process_rows()
        
        # Get a new piece
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        # Check if game is over
        if not self.valid_move(self.current_piece):
            self.game_over = True

    def process_hands(self):
        # Find connected hands and make them disappear (handshake)
        visited = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if (self.grid[y][x] != EMPTY and 
                    isinstance(self.grid[y][x], dict) and 
                    self.grid[y][x]['type'] == HAND and 
                    not visited[y][x]):
                    
                    # Find all connected hands
                    connected = []
                    self.find_connected_hands(x, y, visited, connected)
                    
                    # If 2 or more connected, make them disappear
                    if len(connected) >= 2:
                        for cx, cy in connected:
                            self.grid[cy][cx] = EMPTY
                        
                        # Add score based on number of hands
                        self.score += len(connected) * 50
        
        # Apply gravity after removing hands
        self.apply_gravity()

    def find_connected_hands(self, x, y, visited, connected):
        # Find all connected hands using DFS
        if (x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT or 
            visited[y][x] or self.grid[y][x] == EMPTY or 
            not isinstance(self.grid[y][x], dict) or
            self.grid[y][x]['type'] != HAND):
            return
        
        visited[y][x] = True
        connected.append((x, y))
        
        # Check all four directions
        self.find_connected_hands(x + 1, y, visited, connected)
        self.find_connected_hands(x - 1, y, visited, connected)
        self.find_connected_hands(x, y + 1, visited, connected)
        self.find_connected_hands(x, y - 1, visited, connected)

    def merge_nuts(self):
        # Merge adjacent identical nuts (2048 style)
        merged = True
        
        while merged:
            merged = False
            
            # Check horizontal merges
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH - 1):
                    if (self.grid[y][x] != EMPTY and 
                        isinstance(self.grid[y][x], dict) and 
                        self.grid[y][x]['type'] == NUT and 
                        self.grid[y][x+1] != EMPTY and 
                        isinstance(self.grid[y][x+1], dict) and 
                        self.grid[y][x+1]['type'] == NUT and 
                        self.grid[y][x]['value'] == self.grid[y][x+1]['value']):
                        
                        # Merge nuts
                        value = self.grid[y][x]['value'] * 2
                        self.grid[y][x] = {'type': NUT, 'value': value}
                        self.grid[y][x+1] = EMPTY
                        
                        # Update score and max nut value
                        self.score += value
                        self.max_nut_value = max(self.max_nut_value, value)
                        merged = True
            
            # Check vertical merges
            for y in range(GRID_HEIGHT - 1):
                for x in range(GRID_WIDTH):
                    if (self.grid[y][x] != EMPTY and 
                        isinstance(self.grid[y][x], dict) and 
                        self.grid[y][x]['type'] == NUT and 
                        self.grid[y+1][x] != EMPTY and 
                        isinstance(self.grid[y+1][x], dict) and 
                        self.grid[y+1][x]['type'] == NUT and 
                        self.grid[y][x]['value'] == self.grid[y+1][x]['value']):
                        
                        # Merge nuts
                        value = self.grid[y][x]['value'] * 2
                        self.grid[y][x] = {'type': NUT, 'value': value}
                        self.grid[y+1][x] = EMPTY
                        
                        # Update score and max nut value
                        self.score += value
                        self.max_nut_value = max(self.max_nut_value, value)
                        merged = True
            
            # Apply gravity after merges
            if merged:
                self.apply_gravity()

    def process_rows(self):
        # Process each row to reduce nuts by squirrels
        for y in range(GRID_HEIGHT):
            # Count squirrels and nuts in the row
            squirrels = []
            nuts = []
            
            for x in range(GRID_WIDTH):
                if (self.grid[y][x] != EMPTY and 
                    isinstance(self.grid[y][x], dict)):
                    if self.grid[y][x]['type'] == SQUIRREL:
                        squirrels.append((x, y))
                    elif self.grid[y][x]['type'] == NUT:
                        nuts.append((x, y, self.grid[y][x]['value']))
            
            # Sort nuts by value (highest first)
            nuts.sort(key=lambda n: n[2], reverse=True)
            
            # Use squirrels to reduce nuts
            squirrels_available = len(squirrels)
            for nx, ny, value in nuts:
                if squirrels_available >= value:
                    # Remove the nut
                    self.grid[ny][nx] = EMPTY
                    squirrels_available -= value
                    self.score += value * 10
                    self.squirrels_used += value
                    
                    # Remove used squirrels
                    for i in range(value):
                        if i < len(squirrels):
                            sx, sy = squirrels[i]
                            self.grid[sy][sx] = EMPTY
            
            # Check if row is cleared
            if all(self.grid[y][x] == EMPTY for x in range(GRID_WIDTH)):
                self.rows_cleared += 1
                self.score += 100
                
                # Update level
                self.level = self.rows_cleared // 5 + 1
                
                # Increase speed with level
                self.fall_speed = max(0.1, 0.5 - (self.level - 1) * 0.05)
        
        # Apply gravity after processing rows
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

    def draw_cell(self, x, y, cell):
        # Draw a cell at the specified position
        rect_pos = [x * BLOCK_SIZE + 2, y * BLOCK_SIZE + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4]
        
        if cell['type'] == HAND:
            # Draw hand
            self.screen.blit(HAND_IMG, rect_pos)
        elif cell['type'] == SQUIRREL:
            # Draw squirrel
            self.screen.blit(SQUIRREL_IMG, rect_pos)
        elif cell['type'] == NUT:
            # Draw nut with value
            self.screen.blit(NUT_IMG, rect_pos)
            
            # Draw value text
            font_size = 'medium'
            if cell['value'] >= 100:
                font_size = 'small'
            
            text = self.fonts[font_size].render(str(cell['value']), True, WHITE)
            text_rect = text.get_rect(center=(x * BLOCK_SIZE + BLOCK_SIZE // 2, y * BLOCK_SIZE + BLOCK_SIZE // 2))
            self.screen.blit(text, text_rect)

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
                    rect_pos = [next_x + x * BLOCK_SIZE + 2, 
                               next_y + y * BLOCK_SIZE + 2, 
                               BLOCK_SIZE - 4, BLOCK_SIZE - 4]
                    
                    if cell['type'] == HAND:
                        self.screen.blit(HAND_IMG, rect_pos)
                    elif cell['type'] == SQUIRREL:
                        self.screen.blit(SQUIRREL_IMG, rect_pos)
                    elif cell['type'] == NUT:
                        self.screen.blit(NUT_IMG, rect_pos)
                        
                        # Draw value text
                        font_size = 'medium'
                        if cell['value'] >= 100:
                            font_size = 'small'
                        
                        text = self.fonts[font_size].render(str(cell['value']), True, WHITE)
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
        title_text = self.fonts['large'].render("Hands & Squirrels", True, WHITE)
        self.screen.blit(title_text, (GRID_WIDTH * BLOCK_SIZE + 10, 10))
        
        # Draw score
        score_text = self.fonts['medium'].render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, 60))
        
        # Draw level
        level_text = self.fonts['medium'].render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (GRID_WIDTH * BLOCK_SIZE + 10, 90))
        
        # Draw next piece text
        next_text = self.fonts['medium'].render("Next:", True, WHITE)
        self.screen.blit(next_text, (GRID_WIDTH * BLOCK_SIZE + 10, 120))
        
        # Draw the next piece
        self.draw_next_piece()
        
        # Draw max nut value
        max_nut_text = self.fonts['medium'].render(f"Max Nut: {self.max_nut_value}", True, WHITE)
        self.screen.blit(max_nut_text, (GRID_WIDTH * BLOCK_SIZE + 10, 250))
        
        # Draw squirrels used
        squirrels_text = self.fonts['medium'].render(f"Squirrels Used: {self.squirrels_used}", True, WHITE)
        self.screen.blit(squirrels_text, (GRID_WIDTH * BLOCK_SIZE + 10, 280))
        
        # Draw legend
        legend_y = 330
        
        # Hand legend
        self.screen.blit(HAND_IMG, (GRID_WIDTH * BLOCK_SIZE + 10, legend_y))
        hand_text = self.fonts['small'].render("Hands - Connect to handshake", True, WHITE)
        self.screen.blit(hand_text, (GRID_WIDTH * BLOCK_SIZE + 60, legend_y + 10))
        
        # Squirrel legend
        legend_y += 60
        self.screen.blit(SQUIRREL_IMG, (GRID_WIDTH * BLOCK_SIZE + 10, legend_y))
        squirrel_text = self.fonts['small'].render("Squirrels - Reduce nuts", True, WHITE)
        self.screen.blit(squirrel_text, (GRID_WIDTH * BLOCK_SIZE + 60, legend_y + 10))
        
        # Nut legend
        legend_y += 60
        self.screen.blit(NUT_IMG, (GRID_WIDTH * BLOCK_SIZE + 10, legend_y))
        nut_text = self.fonts['small'].render("Nuts - Merge to increase value", True, WHITE)
        self.screen.blit(nut_text, (GRID_WIDTH * BLOCK_SIZE + 60, legend_y + 10))
        
        # Draw game instructions
        instructions = [
            "Controls:",
            "← → : Move",
            "↑ : Rotate",
            "↓ : Soft Drop",
            "Space : Hard Drop",
            "",
            "Connect hands to make",
            "them disappear",
            "",
            "Merge same-value nuts",
            "",
            "Use squirrels to remove",
            "nuts (need same number",
            "of squirrels as nut value)"
        ]
        
        y_pos = 500
        for instruction in instructions:
            instr_text = self.fonts['small'].render(instruction, True, WHITE)
            self.screen.blit(instr_text, (GRID_WIDTH * BLOCK_SIZE + 10, y_pos))
            y_pos += 20
        
        # Draw game over text if game is over
        if self.game_over:
            game_over_text = self.fonts['large'].render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(game_over_text, (GRID_WIDTH * BLOCK_SIZE + 10, 800))
            
            restart_text = self.fonts['medium'].render("Press R to restart", True, WHITE)
            self.screen.blit(restart_text, (GRID_WIDTH * BLOCK_SIZE + 10, 840))

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
    # Create assets directory if it doesn't exist
    import os
    os.makedirs("/home/fleagne/git/amazon-q-game/assets", exist_ok=True)
    
    game = HandsAndSquirrels()
    game.run()
