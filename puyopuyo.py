import pygame
import random
import time
import sys

# Initialize pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

# Game dimensions
BLOCK_SIZE = 40
GRID_WIDTH = 6
GRID_HEIGHT = 12
SIDEBAR_WIDTH = 200

# Screen dimensions
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Puyo colors
PUYO_COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE]

class PuyoPuyo:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Puyo Puyo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 25)
        self.reset_game()

    def reset_game(self):
        # Initialize grid with zeros (empty cells)
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_pair = self.new_pair()
        self.next_pair = self.new_pair()
        self.game_over = False
        self.score = 0
        self.chain_count = 0
        self.fall_time = 0
        self.fall_speed = 0.5  # Time in seconds between automatic piece movements
        self.last_fall_time = time.time()
        self.rotation_state = 0  # 0: main above, 1: main right, 2: main below, 3: main left

    def new_pair(self):
        # Create a new pair of Puyos
        main_color = random.choice(PUYO_COLORS)
        sub_color = random.choice(PUYO_COLORS)
        
        # Starting position (center top)
        x = GRID_WIDTH // 2 - 1
        y = 0
        
        return {
            'main': {'x': x, 'y': y, 'color': main_color},
            'sub': {'x': x, 'y': y - 1, 'color': sub_color}
        }

    def rotate_pair(self, direction):
        # Rotate the current pair (clockwise or counterclockwise)
        main_x = self.current_pair['main']['x']
        main_y = self.current_pair['main']['y']
        
        # Calculate new position based on rotation state
        if direction == 'clockwise':
            self.rotation_state = (self.rotation_state + 1) % 4
        else:  # counterclockwise
            self.rotation_state = (self.rotation_state - 1) % 4
        
        # Apply rotation
        if self.rotation_state == 0:  # sub above main
            new_sub_x = main_x
            new_sub_y = main_y - 1
        elif self.rotation_state == 1:  # sub right of main
            new_sub_x = main_x + 1
            new_sub_y = main_y
        elif self.rotation_state == 2:  # sub below main
            new_sub_x = main_x
            new_sub_y = main_y + 1
        else:  # sub left of main
            new_sub_x = main_x - 1
            new_sub_y = main_y
        
        # Check if the new position is valid
        if self.is_valid_position(new_sub_x, new_sub_y):
            self.current_pair['sub']['x'] = new_sub_x
            self.current_pair['sub']['y'] = new_sub_y
            return True
        
        # If not valid, try wall kick
        if new_sub_x < 0:
            if self.is_valid_position(main_x + 1, main_y) and self.is_valid_position(new_sub_x + 1, new_sub_y):
                self.current_pair['main']['x'] += 1
                self.current_pair['sub']['x'] = new_sub_x + 1
                self.current_pair['sub']['y'] = new_sub_y
                return True
        elif new_sub_x >= GRID_WIDTH:
            if self.is_valid_position(main_x - 1, main_y) and self.is_valid_position(new_sub_x - 1, new_sub_y):
                self.current_pair['main']['x'] -= 1
                self.current_pair['sub']['x'] = new_sub_x - 1
                self.current_pair['sub']['y'] = new_sub_y
                return True
        
        # Revert rotation state if rotation failed
        if direction == 'clockwise':
            self.rotation_state = (self.rotation_state - 1) % 4
        else:
            self.rotation_state = (self.rotation_state + 1) % 4
        
        return False

    def is_valid_position(self, x, y):
        # Check if a position is valid (within bounds and not occupied)
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return False
        
        # If above the grid, it's valid
        if y < 0:
            return True
        
        # Check if the cell is already occupied
        return self.grid[y][x] == 0

    def move_pair(self, dx, dy):
        # Move the current pair if possible
        main_x = self.current_pair['main']['x'] + dx
        main_y = self.current_pair['main']['y'] + dy
        sub_x = self.current_pair['sub']['x'] + dx
        sub_y = self.current_pair['sub']['y'] + dy
        
        # Check if the new positions are valid
        if (self.is_valid_position(main_x, main_y) and 
            self.is_valid_position(sub_x, sub_y)):
            self.current_pair['main']['x'] = main_x
            self.current_pair['main']['y'] = main_y
            self.current_pair['sub']['x'] = sub_x
            self.current_pair['sub']['y'] = sub_y
            return True
        
        return False

    def lock_pair(self):
        # Lock the current pair in place
        main = self.current_pair['main']
        sub = self.current_pair['sub']
        
        # Add main puyo to grid if it's within bounds
        if 0 <= main['y'] < GRID_HEIGHT:
            self.grid[main['y']][main['x']] = main['color']
        
        # Add sub puyo to grid if it's within bounds
        if 0 <= sub['y'] < GRID_HEIGHT:
            self.grid[sub['y']][sub['x']] = sub['color']
        
        # Apply gravity and check for matches
        self.apply_gravity()
        self.check_matches()
        
        # Get next pair
        self.current_pair = self.next_pair
        self.next_pair = self.new_pair()
        self.rotation_state = 0
        
        # Check if game is over (if new pair overlaps with existing puyos)
        if not self.is_valid_position(self.current_pair['main']['x'], self.current_pair['main']['y']) or \
           not self.is_valid_position(self.current_pair['sub']['x'], self.current_pair['sub']['y']):
            self.game_over = True

    def apply_gravity(self):
        # Apply gravity to make puyos fall
        for x in range(GRID_WIDTH):
            # Start from the bottom and move up
            empty_y = None
            for y in range(GRID_HEIGHT - 1, -1, -1):
                if self.grid[y][x] == 0 and empty_y is None:
                    empty_y = y
                elif self.grid[y][x] != 0 and empty_y is not None:
                    # Move puyo down
                    self.grid[empty_y][x] = self.grid[y][x]
                    self.grid[y][x] = 0
                    empty_y -= 1

    def check_matches(self):
        # Check for matches (4+ same color connected)
        chain_count = 0
        while True:
            matches_found = False
            visited = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
            
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    if self.grid[y][x] != 0 and not visited[y][x]:
                        # Find all connected puyos of the same color
                        color = self.grid[y][x]
                        connected = []
                        self.find_connected(x, y, color, visited, connected)
                        
                        # If 4 or more connected, remove them
                        if len(connected) >= 4:
                            matches_found = True
                            for cx, cy in connected:
                                self.grid[cy][cx] = 0
                            
                            # Add score based on number of puyos popped
                            self.score += len(connected) * 10 * (chain_count + 1)
            
            if matches_found:
                chain_count += 1
                self.apply_gravity()
                # Add a small delay to show the chain reaction
                self.draw()
                pygame.display.flip()
                pygame.time.delay(300)
            else:
                break
        
        if chain_count > 0:
            self.chain_count = max(self.chain_count, chain_count)

    def find_connected(self, x, y, color, visited, connected):
        # Find all connected puyos of the same color using DFS
        if (x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT or 
            visited[y][x] or self.grid[y][x] != color):
            return
        
        visited[y][x] = True
        connected.append((x, y))
        
        # Check all four directions
        self.find_connected(x + 1, y, color, visited, connected)
        self.find_connected(x - 1, y, color, visited, connected)
        self.find_connected(x, y + 1, color, visited, connected)
        self.find_connected(x, y - 1, color, visited, connected)

    def draw_grid(self):
        # Draw the game grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                # Draw grid cell
                pygame.draw.rect(
                    self.screen,
                    GRAY,
                    [x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE],
                    1
                )
                
                # If cell is occupied, draw the puyo
                if self.grid[y][x] != 0:
                    self.draw_puyo(x, y, self.grid[y][x])

    def draw_puyo(self, x, y, color):
        # Draw a puyo at the specified position
        pygame.draw.circle(
            self.screen,
            color,
            (x * BLOCK_SIZE + BLOCK_SIZE // 2, y * BLOCK_SIZE + BLOCK_SIZE // 2),
            BLOCK_SIZE // 2 - 2
        )
        # Add a highlight to make it look more like a puyo
        pygame.draw.circle(
            self.screen,
            WHITE,
            (x * BLOCK_SIZE + BLOCK_SIZE // 3, y * BLOCK_SIZE + BLOCK_SIZE // 3),
            BLOCK_SIZE // 6
        )

    def draw_current_pair(self):
        # Draw the current pair of puyos
        main = self.current_pair['main']
        sub = self.current_pair['sub']
        
        # Only draw if they're within the visible grid
        if main['y'] >= 0:
            self.draw_puyo(main['x'], main['y'], main['color'])
        if sub['y'] >= 0:
            self.draw_puyo(sub['x'], sub['y'], sub['color'])

    def draw_next_pair(self):
        # Draw the next pair in the sidebar
        next_x = GRID_WIDTH * BLOCK_SIZE + SIDEBAR_WIDTH // 2
        next_y = 150
        
        # Draw the next pair preview
        pygame.draw.circle(
            self.screen,
            self.next_pair['main']['color'],
            (next_x, next_y + BLOCK_SIZE),
            BLOCK_SIZE // 2 - 2
        )
        pygame.draw.circle(
            self.screen,
            WHITE,
            (next_x - BLOCK_SIZE // 6, next_y + BLOCK_SIZE - BLOCK_SIZE // 6),
            BLOCK_SIZE // 6
        )
        
        pygame.draw.circle(
            self.screen,
            self.next_pair['sub']['color'],
            (next_x, next_y),
            BLOCK_SIZE // 2 - 2
        )
        pygame.draw.circle(
            self.screen,
            WHITE,
            (next_x - BLOCK_SIZE // 6, next_y - BLOCK_SIZE // 6),
            BLOCK_SIZE // 6
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
        
        # Draw max chain
        chain_text = self.font.render(f"Max Chain: {self.chain_count}", True, WHITE)
        self.screen.blit(chain_text, (GRID_WIDTH * BLOCK_SIZE + 10, 70))
        
        # Draw next piece text
        next_text = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_text, (GRID_WIDTH * BLOCK_SIZE + 10, 110))
        
        # Draw the next pair
        self.draw_next_pair()
        
        # Draw game over text if game is over
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            self.screen.blit(game_over_text, (GRID_WIDTH * BLOCK_SIZE + 10, 250))
            
            restart_text = self.font.render("Press R to restart", True, WHITE)
            self.screen.blit(restart_text, (GRID_WIDTH * BLOCK_SIZE + 10, 290))

    def draw(self):
        # Draw everything
        self.screen.fill(BLACK)
        self.draw_grid()
        if not self.game_over:
            self.draw_current_pair()
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
                            self.move_pair(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move_pair(1, 0)
                        elif event.key == pygame.K_DOWN:
                            if not self.move_pair(0, 1):
                                self.lock_pair()
                        elif event.key == pygame.K_z:
                            self.rotate_pair('counterclockwise')
                        elif event.key == pygame.K_x or event.key == pygame.K_UP:
                            self.rotate_pair('clockwise')
                        elif event.key == pygame.K_SPACE:
                            # Hard drop
                            while self.move_pair(0, 1):
                                pass
                            self.lock_pair()
                else:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        self.reset_game()
            
            # Automatic falling
            if not self.game_over and current_time - self.last_fall_time > self.fall_speed:
                if not self.move_pair(0, 1):
                    self.lock_pair()
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
    game = PuyoPuyo()
    game.run()
