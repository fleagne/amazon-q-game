import pygame
import sys
import random

# Initialize pygame with audio disabled to avoid ALSA errors
pygame.init()
# Disable audio to prevent ALSA errors
pygame.mixer.quit()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 50
GRID_WIDTH = 12
GRID_HEIGHT = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)

# Game elements
EMPTY = 0
WALL = 1
BOX = 2
TARGET = 3
BOX_ON_TARGET = 4
PLAYER = 5
YANKEE = 6
WEAK_PERSON = 7
WEAPON = 8

# Create a font
FONT = pygame.font.SysFont('Arial', 24)
LARGE_FONT = pygame.font.SysFont('Arial', 36)

class SokobanBanchou:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sokoban Banchou")
        self.clock = pygame.time.Clock()
        
        # Load images or create placeholders
        self.images = {
            WALL: self.create_image(DARK_GRAY),
            BOX: self.create_image(BROWN),
            TARGET: self.create_image(GREEN),
            BOX_ON_TARGET: self.create_image(BLUE),
            PLAYER: self.create_image(YELLOW),
            YANKEE: self.create_image(RED),
            WEAK_PERSON: self.create_image(BLUE),
            WEAPON: self.create_image(GRAY)
        }
        
        self.reset_game()

    def create_image(self, color):
        # Create a simple colored square as a placeholder for game elements
        image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        image.fill(color)
        pygame.draw.rect(image, BLACK, (0, 0, TILE_SIZE, TILE_SIZE), 1)
        return image

    def reset_game(self):
        self.level = 1
        self.score = 1000
        self.has_weapon = False
        self.weapon_uses = 0
        self.moves = 0
        self.game_over = False
        self.victory = False
        self.message = ""
        
        # Create a basic level
        self.load_level(self.level)

    def load_level(self, level_num):
        # Create a level based on the level number
        # This is a simple level generator - you could replace with designed levels
        self.grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Add walls around the edges
        for x in range(GRID_WIDTH):
            self.grid[0][x] = WALL
            self.grid[GRID_HEIGHT-1][x] = WALL
        for y in range(GRID_HEIGHT):
            self.grid[y][0] = WALL
            self.grid[y][GRID_WIDTH-1] = WALL
        
        # Add some random walls
        wall_count = 10 + level_num * 2
        for _ in range(wall_count):
            x = random.randint(1, GRID_WIDTH-2)
            y = random.randint(1, GRID_HEIGHT-2)
            self.grid[y][x] = WALL
        
        # Add boxes and targets
        self.boxes = []
        self.targets = []
        box_count = 3 + level_num
        for i in range(box_count):
            # Place boxes
            while True:
                x = random.randint(1, GRID_WIDTH-2)
                y = random.randint(1, GRID_HEIGHT-2)
                if self.grid[y][x] == EMPTY:
                    self.grid[y][x] = BOX
                    self.boxes.append((x, y))
                    break
            
            # Place targets
            while True:
                x = random.randint(1, GRID_WIDTH-2)
                y = random.randint(1, GRID_HEIGHT-2)
                if self.grid[y][x] == EMPTY:
                    self.grid[y][x] = TARGET
                    self.targets.append((x, y))
                    break
        
        # Add player
        while True:
            x = random.randint(1, GRID_WIDTH-2)
            y = random.randint(1, GRID_HEIGHT-2)
            if self.grid[y][x] == EMPTY:
                self.player_x = x
                self.player_y = y
                break
        
        # Add yankees
        self.yankees = []
        yankee_count = level_num
        for _ in range(yankee_count):
            while True:
                x = random.randint(1, GRID_WIDTH-2)
                y = random.randint(1, GRID_HEIGHT-2)
                if self.grid[y][x] == EMPTY:
                    self.grid[y][x] = YANKEE
                    self.yankees.append((x, y))
                    break
        
        # Add weak persons
        self.weak_persons = []
        weak_count = level_num
        for _ in range(weak_count):
            while True:
                x = random.randint(1, GRID_WIDTH-2)
                y = random.randint(1, GRID_HEIGHT-2)
                if self.grid[y][x] == EMPTY:
                    self.grid[y][x] = WEAK_PERSON
                    self.weak_persons.append((x, y))
                    break
        
        # Add weapons
        self.weapons = []
        weapon_count = 1 + level_num // 2
        for _ in range(weapon_count):
            while True:
                x = random.randint(1, GRID_WIDTH-2)
                y = random.randint(1, GRID_HEIGHT-2)
                if self.grid[y][x] == EMPTY:
                    self.grid[y][x] = WEAPON
                    self.weapons.append((x, y))
                    break

    def draw(self):
        # Clear the screen
        self.screen.fill(BLACK)
        
        # Calculate grid offset to center it
        grid_width_px = GRID_WIDTH * TILE_SIZE
        grid_height_px = GRID_HEIGHT * TILE_SIZE
        offset_x = (SCREEN_WIDTH - grid_width_px) // 2
        offset_y = (SCREEN_HEIGHT - grid_height_px) // 2
        
        # Draw the grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                if cell != EMPTY:
                    self.screen.blit(self.images[cell], 
                                     (offset_x + x * TILE_SIZE, 
                                      offset_y + y * TILE_SIZE))
        
        # Draw the player
        self.screen.blit(self.images[PLAYER], 
                         (offset_x + self.player_x * TILE_SIZE, 
                          offset_y + self.player_y * TILE_SIZE))
        
        # Draw the score and level
        score_text = FONT.render(f"Score: {self.score}", True, WHITE)
        level_text = FONT.render(f"Level: {self.level}", True, WHITE)
        moves_text = FONT.render(f"Moves: {self.moves}", True, WHITE)
        weapon_text = FONT.render(f"Weapon: {'Yes' if self.has_weapon else 'No'}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 40))
        self.screen.blit(moves_text, (10, 70))
        self.screen.blit(weapon_text, (10, 100))
        
        # Draw message if any
        if self.message:
            message_text = FONT.render(self.message, True, WHITE)
            self.screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, 10))
        
        # Draw game over or victory message
        if self.game_over:
            game_over_text = LARGE_FONT.render("GAME OVER", True, RED)
            restart_text = FONT.render("Press R to restart", True, WHITE)
            self.screen.blit(game_over_text, 
                            (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                             SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
            self.screen.blit(restart_text, 
                            (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                             SCREEN_HEIGHT // 2 + 50))
        elif self.victory:
            victory_text = LARGE_FONT.render("LEVEL CLEAR!", True, GREEN)
            next_text = FONT.render("Press N for next level", True, WHITE)
            self.screen.blit(victory_text, 
                            (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, 
                             SCREEN_HEIGHT // 2 - victory_text.get_height() // 2))
            self.screen.blit(next_text, 
                            (SCREEN_WIDTH // 2 - next_text.get_width() // 2, 
                             SCREEN_HEIGHT // 2 + 50))

    def move_player(self, dx, dy):
        if self.game_over or self.victory:
            return
        
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        
        # Check if the move is valid
        if self.grid[new_y][new_x] == WALL:
            return
        
        # Handle box pushing
        if self.grid[new_y][new_x] in [BOX, BOX_ON_TARGET]:
            # Calculate where the box would end up
            box_new_x = new_x + dx
            box_new_y = new_y + dy
            
            # Check if the box can be pushed
            if self.grid[box_new_y][box_new_x] in [EMPTY, TARGET]:
                # Move the box
                is_on_target = self.grid[new_y][new_x] == BOX_ON_TARGET
                self.grid[new_y][new_x] = TARGET if is_on_target else EMPTY
                
                # Update the box position
                is_target = self.grid[box_new_y][box_new_x] == TARGET
                self.grid[box_new_y][box_new_x] = BOX_ON_TARGET if is_target else BOX
                
                # Update box list
                self.boxes.remove((new_x, new_y))
                self.boxes.append((box_new_x, box_new_y))
                
                # Move the player
                self.player_x = new_x
                self.player_y = new_y
                self.moves += 1
                
                # Check for victory
                self.check_victory()
            else:
                # Can't push the box
                return
        
        # Handle yankee encounter
        elif self.grid[new_y][new_x] == YANKEE:
            if self.has_weapon:
                # Fight the yankee with a weapon
                self.message = "You fought a yankee! Lost score for using a weapon."
                self.score -= 100
                self.has_weapon = False  # Use up the weapon
                self.weapon_uses += 1
                
                # Remove the yankee
                self.grid[new_y][new_x] = EMPTY
                self.yankees.remove((new_x, new_y))
                
                # Move the player
                self.player_x = new_x
                self.player_y = new_y
                self.moves += 1
            else:
                # Game over if no weapon
                self.message = "You challenged a yankee without a weapon! You lost..."
                self.game_over = True
        
        # Handle weak person encounter
        elif self.grid[new_y][new_x] == WEAK_PERSON:
            # Bullying weak person loses score
            self.message = "You bullied a weak person! Your score decreased significantly."
            self.score -= 200
            
            # Remove the weak person
            self.grid[new_y][new_x] = EMPTY
            self.weak_persons.remove((new_x, new_y))
            
            # Move the player
            self.player_x = new_x
            self.player_y = new_y
            self.moves += 1
        
        # Handle weapon pickup
        elif self.grid[new_y][new_x] == WEAPON:
            self.message = "You got a weapon!"
            self.has_weapon = True
            
            # Remove the weapon
            self.grid[new_y][new_x] = EMPTY
            self.weapons.remove((new_x, new_y))
            
            # Move the player
            self.player_x = new_x
            self.player_y = new_y
            self.moves += 1
        
        # Handle normal movement
        elif self.grid[new_y][new_x] in [EMPTY, TARGET]:
            # Move the player
            self.player_x = new_x
            self.player_y = new_y
            self.moves += 1

    def use_weapon(self):
        if not self.has_weapon or self.game_over or self.victory:
            return
        
        # Use weapon to clear a path
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Up, Right, Down, Left
        
        for dx, dy in directions:
            target_x = self.player_x + dx
            target_y = self.player_y + dy
            
            if 0 <= target_x < GRID_WIDTH and 0 <= target_y < GRID_HEIGHT:
                if self.grid[target_y][target_x] == BOX or self.grid[target_y][target_x] == BOX_ON_TARGET:
                    # Remove the box
                    is_on_target = self.grid[target_y][target_x] == BOX_ON_TARGET
                    self.grid[target_y][target_x] = TARGET if is_on_target else EMPTY
                    
                    # Update box list
                    if (target_x, target_y) in self.boxes:
                        self.boxes.remove((target_x, target_y))
                    
                    # Decrease score for using weapon
                    self.score -= 50
                    self.has_weapon = False
                    self.weapon_uses += 1
                    self.message = "You destroyed a box with your weapon! Score decreased."
                    
                    # Check for victory
                    self.check_victory()
                    return
                
                elif self.grid[target_y][target_x] == YANKEE:
                    # Remove the yankee
                    self.grid[target_y][target_x] = EMPTY
                    self.yankees.remove((target_x, target_y))
                    
                    # Decrease score for using weapon
                    self.score -= 100
                    self.has_weapon = False
                    self.weapon_uses += 1
                    self.message = "You defeated a yankee with your weapon! Score decreased."
                    return
                
                elif self.grid[target_y][target_x] == WEAK_PERSON:
                    # Remove the weak person
                    self.grid[target_y][target_x] = EMPTY
                    self.weak_persons.remove((target_x, target_y))
                    
                    # Decrease score significantly for attacking weak person
                    self.score -= 200
                    self.has_weapon = False
                    self.weapon_uses += 1
                    self.message = "You attacked a weak person with your weapon! Score decreased significantly."
                    return
        
        self.message = "No target to use weapon on."

    def check_victory(self):
        # Check if all boxes are on targets
        boxes_on_target = 0
        for x, y in self.boxes:
            if self.grid[y][x] == BOX_ON_TARGET:
                boxes_on_target += 1
        
        if boxes_on_target == len(self.targets):
            self.victory = True
            # Calculate final score
            final_score = self.score - self.moves - (self.weapon_uses * 50)
            self.message = f"Level {self.level} cleared! Final score: {final_score}"

    def next_level(self):
        if self.victory:
            self.level += 1
            self.victory = False
            self.message = f"Starting level {self.level}!"
            self.moves = 0
            self.has_weapon = False
            self.weapon_uses = 0
            self.load_level(self.level)

    def run(self):
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    elif event.key == pygame.K_n and self.victory:
                        self.next_level()
                    elif event.key == pygame.K_UP:
                        self.move_player(0, -1)
                    elif event.key == pygame.K_RIGHT:
                        self.move_player(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.move_player(0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.move_player(-1, 0)
                    elif event.key == pygame.K_SPACE:
                        self.use_weapon()
            
            # Draw everything
            self.draw()
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SokobanBanchou()
    game.run()
