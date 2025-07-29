import pygame
import random
import sys
import json
import os
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
CELL_SIZE = 25
CELL_NUMBER_X = WINDOW_WIDTH // CELL_SIZE
CELL_NUMBER_Y = (WINDOW_HEIGHT - 100) // CELL_SIZE  # Reserve space for UI

# Modern 2025 Color Palette
BACKGROUND = (15, 15, 25)
GRID_COLOR = (25, 25, 40)
SNAKE_HEAD = (0, 255, 150)
SNAKE_BODY_START = (0, 200, 120)
SNAKE_BODY_END = (0, 150, 90)
FOOD_COLOR = (255, 100, 100)
FOOD_GLOW = (255, 150, 150)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (180, 180, 200)
ACCENT_COLOR = (100, 255, 200)
BUTTON_COLOR = (40, 40, 60)
BUTTON_HOVER = (60, 60, 90)
BUTTON_ACTIVE = (80, 80, 120)
PARTICLE_COLORS = [(255, 100, 100), (255, 150, 100), (255, 200, 100), (255, 255, 100)]

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
PAUSED = 3

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 60
        self.max_life = 60
        self.color = color
        self.size = random.uniform(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vx *= 0.98
        self.vy *= 0.98
    
    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        size = int(self.size * (self.life / self.max_life))
        if size > 0:
            color_with_alpha = (*self.color, alpha)
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color_with_alpha, (size, size), size)
            screen.blit(surf, (self.x - size, self.y - size))

class Snake:
    def __init__(self):
        self.body = [pygame.Vector2(5, 10), pygame.Vector2(4, 10), pygame.Vector2(3, 10)]
        self.direction = pygame.Vector2(1, 0)
        self.new_block = False
        self.trail = []
        
    def draw_snake(self, screen):
        # Draw trail effect
        for i, pos in enumerate(self.trail):
            alpha = int(50 * (1 - i / len(self.trail)))
            if alpha > 0:
                surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                color = (*SNAKE_BODY_END, alpha)
                pygame.draw.rect(surf, color, (0, 0, CELL_SIZE, CELL_SIZE))
                screen.blit(surf, (pos[0], pos[1]))
        
        # Draw snake body with gradient
        for index, block in enumerate(self.body):
            x_pos = int(block.x * CELL_SIZE)
            y_pos = int(block.y * CELL_SIZE) + 100  # Offset for UI
            
            if index == 0:  # Head
                # Glow effect for head
                glow_surf = pygame.Surface((CELL_SIZE + 10, CELL_SIZE + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*SNAKE_HEAD, 50), (0, 0, CELL_SIZE + 10, CELL_SIZE + 10), border_radius=8)
                screen.blit(glow_surf, (x_pos - 5, y_pos - 5))
                
                # Head with rounded corners
                pygame.draw.rect(screen, SNAKE_HEAD, (x_pos, y_pos, CELL_SIZE, CELL_SIZE), border_radius=8)
                
                # Modern eyes
                eye_size = 4
                if self.direction.x == 1:  # Right
                    eye1 = (x_pos + 15, y_pos + 7)
                    eye2 = (x_pos + 15, y_pos + 17)
                elif self.direction.x == -1:  # Left
                    eye1 = (x_pos + 8, y_pos + 7)
                    eye2 = (x_pos + 8, y_pos + 17)
                elif self.direction.y == -1:  # Up
                    eye1 = (x_pos + 7, y_pos + 8)
                    eye2 = (x_pos + 17, y_pos + 8)
                else:  # Down
                    eye1 = (x_pos + 7, y_pos + 15)
                    eye2 = (x_pos + 17, y_pos + 15)
                
                pygame.draw.circle(screen, (255, 255, 255), eye1, eye_size)
                pygame.draw.circle(screen, (255, 255, 255), eye2, eye_size)
                pygame.draw.circle(screen, (0, 0, 0), eye1, eye_size - 2)
                pygame.draw.circle(screen, (0, 0, 0), eye2, eye_size - 2)
            else:  # Body
                # Gradient color based on position
                ratio = index / len(self.body)
                r = int(SNAKE_BODY_START[0] * (1 - ratio) + SNAKE_BODY_END[0] * ratio)
                g = int(SNAKE_BODY_START[1] * (1 - ratio) + SNAKE_BODY_END[1] * ratio)
                b = int(SNAKE_BODY_START[2] * (1 - ratio) + SNAKE_BODY_END[2] * ratio)
                body_color = (r, g, b)
                
                pygame.draw.rect(screen, body_color, (x_pos, y_pos, CELL_SIZE, CELL_SIZE), border_radius=6)
                # Highlight effect
                pygame.draw.rect(screen, (255, 255, 255, 30), (x_pos, y_pos, CELL_SIZE, 3), border_radius=3)
        
        # Update trail
        if len(self.body) > 0:
            head_pos = (int(self.body[0].x * CELL_SIZE), int(self.body[0].y * CELL_SIZE) + 100)
            self.trail.append(head_pos)
            if len(self.trail) > 8:
                self.trail.pop(0)
            
    def move_snake(self):
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            
    def add_block(self):
        self.new_block = True
        
    def check_collision(self):
        # Check wall collision
        if not 0 <= self.body[0].x < CELL_NUMBER_X or not 0 <= self.body[0].y < CELL_NUMBER_Y:
            return True
            
        # Check self collision
        for block in self.body[1:]:
            if block == self.body[0]:
                return True
                
        return False
    
    def reset(self):
        self.body = [pygame.Vector2(5, 10), pygame.Vector2(4, 10), pygame.Vector2(3, 10)]
        self.direction = pygame.Vector2(1, 0)
        self.new_block = False
        self.trail = []

class Food:
    def __init__(self):
        self.randomize()
        self.pulse = 0
        
    def draw_food(self, screen):
        x_pos = int(self.pos.x * CELL_SIZE)
        y_pos = int(self.pos.y * CELL_SIZE) + 100
        
        # Pulsing glow effect
        self.pulse += 0.2
        glow_size = int(5 + 3 * math.sin(self.pulse))
        
        # Outer glow
        glow_surf = pygame.Surface((CELL_SIZE + glow_size * 2, CELL_SIZE + glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*FOOD_GLOW, 80), 
                          (CELL_SIZE // 2 + glow_size, CELL_SIZE // 2 + glow_size), 
                          CELL_SIZE // 2 + glow_size)
        screen.blit(glow_surf, (x_pos - glow_size, y_pos - glow_size))
        
        # Food with modern design
        pygame.draw.circle(screen, FOOD_COLOR, 
                          (x_pos + CELL_SIZE // 2, y_pos + CELL_SIZE // 2), 
                          CELL_SIZE // 2 - 2)
        
        # Highlight
        pygame.draw.circle(screen, (255, 255, 255, 100), 
                          (x_pos + CELL_SIZE // 2 - 3, y_pos + CELL_SIZE // 2 - 3), 
                          3)
        
    def randomize(self):
        self.x = random.randint(0, CELL_NUMBER_X - 1)
        self.y = random.randint(0, CELL_NUMBER_Y - 1)
        self.pos = pygame.Vector2(self.x, self.y)

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hovered = False
        self.clicked = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False
    
    def draw(self, screen):
        color = BUTTON_ACTIVE if self.clicked else (BUTTON_HOVER if self.hovered else BUTTON_COLOR)
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, ACCENT_COLOR, self.rect, 2, border_radius=10)
        
        text_surf = self.font.render(self.text, True, TEXT_PRIMARY)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
        self.clicked = False

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.high_score = self.load_high_score()
        self.state = MENU
        self.particles = []
        self.speed = 150
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Buttons
        self.start_button = Button(WINDOW_WIDTH // 2 - 100, 350, 200, 50, "START GAME", self.medium_font)
        self.restart_button = Button(WINDOW_WIDTH // 2 - 100, 400, 200, 50, "PLAY AGAIN", self.medium_font)
        self.menu_button = Button(WINDOW_WIDTH // 2 - 100, 460, 200, 50, "MAIN MENU", self.medium_font)
        
    def load_high_score(self):
        try:
            if os.path.exists("high_score.json"):
                with open("high_score.json", "r") as f:
                    return json.load(f)["high_score"]
        except:
            pass
        return 0
    
    def save_high_score(self):
        try:
            with open("high_score.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except:
            pass
            
    def update(self):
        if self.state == PLAYING:
            self.snake.move_snake()
            self.check_collision()
            self.check_fail()
            
            # Update particles
            self.particles = [p for p in self.particles if p.life > 0]
            for particle in self.particles:
                particle.update()
        
    def check_collision(self):
        if self.food.pos == self.snake.body[0]:
            # Create particles at food position
            food_x = int(self.food.pos.x * CELL_SIZE + CELL_SIZE // 2)
            food_y = int(self.food.pos.y * CELL_SIZE + CELL_SIZE // 2) + 100
            for _ in range(15):
                color = random.choice(PARTICLE_COLORS)
                self.particles.append(Particle(food_x, food_y, color))
            
            self.food.randomize()
            self.snake.add_block()
            self.score += 10
            
            # Increase speed slightly
            if self.speed > 80:
                self.speed -= 2
            
            # Make sure food doesn't spawn on snake
            for block in self.snake.body[1:]:
                if block == self.food.pos:
                    self.food.randomize()
                    
    def check_fail(self):
        if self.snake.check_collision():
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.state = GAME_OVER
    
    def reset_game(self):
        self.snake.reset()
        self.food.randomize()
        self.score = 0
        self.speed = 150
        self.particles = []
        self.state = PLAYING
    
    def draw_grid(self, screen):
        # Modern subtle grid
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (x, 100), (x, WINDOW_HEIGHT), 1)
        for y in range(100, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y), 1)
    
    def draw_ui(self, screen):
        # Top UI bar
        ui_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 100)
        pygame.draw.rect(screen, (20, 20, 35), ui_rect)
        pygame.draw.line(screen, ACCENT_COLOR, (0, 100), (WINDOW_WIDTH, 100), 2)
        
        # Score
        score_text = self.large_font.render(f"SCORE: {self.score}", True, TEXT_PRIMARY)
        screen.blit(score_text, (30, 30))
        
        # High Score
        high_score_text = self.medium_font.render(f"HIGH: {self.high_score}", True, TEXT_SECONDARY)
        screen.blit(high_score_text, (30, 65))
        
        # Speed indicator
        speed_text = self.small_font.render(f"SPEED: {int((200-self.speed)/2)}", True, TEXT_SECONDARY)
        screen.blit(speed_text, (WINDOW_WIDTH - 150, 30))
        
        # Controls hint
        if self.state == PLAYING:
            controls_text = self.small_font.render("ARROW KEYS TO MOVE • SPACE TO PAUSE", True, TEXT_SECONDARY)
            text_rect = controls_text.get_rect(center=(WINDOW_WIDTH // 2, 75))
            screen.blit(controls_text, text_rect)
    
    def draw_menu(self, screen):
        # Background gradient effect
        for y in range(WINDOW_HEIGHT):
            color_ratio = y / WINDOW_HEIGHT
            r = int(BACKGROUND[0] * (1 - color_ratio) + 30 * color_ratio)
            g = int(BACKGROUND[1] * (1 - color_ratio) + 30 * color_ratio)
            b = int(BACKGROUND[2] * (1 - color_ratio) + 50 * color_ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))
        
        # Title with glow effect
        title_text = self.title_font.render("SNAKE 2025", True, ACCENT_COLOR)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        
        # Glow effect
        for offset in range(5, 0, -1):
            glow_color = (*ACCENT_COLOR, 50)
            glow_surf = pygame.Surface(title_text.get_size(), pygame.SRCALPHA)
            glow_surf.blit(title_text, (0, 0))
            screen.blit(glow_surf, (title_rect.x - offset, title_rect.y - offset))
        
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.medium_font.render("Modern Snake Experience", True, TEXT_SECONDARY)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        screen.blit(subtitle_text, subtitle_rect)
        
        # High score display
        if self.high_score > 0:
            high_score_text = self.large_font.render(f"Best Score: {self.high_score}", True, TEXT_PRIMARY)
            high_score_rect = high_score_text.get_rect(center=(WINDOW_WIDTH // 2, 280))
            screen.blit(high_score_text, high_score_rect)
        
        # Instructions
        instructions = [
            "Use ARROW KEYS to control the snake",
            "Eat the glowing food to grow",
            "Avoid walls and your own tail",
            "Press SPACE to pause during game"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, TEXT_SECONDARY)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 500 + i * 25))
            screen.blit(text, text_rect)
        
        # Start button
        self.start_button.draw(screen)
    
    def draw_game_over(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Game Over text with effect
        game_over_text = self.title_font.render("GAME OVER", True, (255, 100, 100))
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        screen.blit(game_over_text, game_over_rect)
        
        # Final score
        final_score_text = self.large_font.render(f"Final Score: {self.score}", True, TEXT_PRIMARY)
        final_score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, 280))
        screen.blit(final_score_text, final_score_rect)
        
        # New high score message
        if self.score == self.high_score and self.score > 0:
            new_high_text = self.medium_font.render("NEW HIGH SCORE!", True, ACCENT_COLOR)
            new_high_rect = new_high_text.get_rect(center=(WINDOW_WIDTH // 2, 320))
            screen.blit(new_high_text, new_high_rect)
        
        # Buttons
        self.restart_button.draw(screen)
        self.menu_button.draw(screen)
    
    def draw_pause(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.title_font.render("PAUSED", True, TEXT_PRIMARY)
        pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(pause_text, pause_rect)
        
        # Resume instruction
        resume_text = self.medium_font.render("Press SPACE to resume", True, TEXT_SECONDARY)
        resume_rect = resume_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        screen.blit(resume_text, resume_rect)
    
    def draw_elements(self, screen):
        if self.state == PLAYING or self.state == PAUSED:
            self.draw_grid(screen)
            self.food.draw_food(screen)
            self.snake.draw_snake(screen)
            
            # Draw particles
            for particle in self.particles:
                particle.draw(screen)
            
            self.draw_ui(screen)
            
            if self.state == PAUSED:
                self.draw_pause(screen)
        
        elif self.state == MENU:
            self.draw_menu(screen)
        
        elif self.state == GAME_OVER:
            # Still show the game in background
            self.draw_grid(screen)
            self.food.draw_food(screen)
            self.snake.draw_snake(screen)
            self.draw_ui(screen)
            self.draw_game_over(screen)

def main():
    # Set up the display
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake 2025 - Modern Edition")
    clock = pygame.time.Clock()
    
    # Create game instance
    game = Game()
    
    # Game update timer
    SCREEN_UPDATE = pygame.USEREVENT
    pygame.time.set_timer(SCREEN_UPDATE, game.speed)
    
    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle button events
            if game.state == MENU:
                if game.start_button.handle_event(event):
                    game.reset_game()
            
            elif game.state == GAME_OVER:
                if game.restart_button.handle_event(event):
                    game.reset_game()
                elif game.menu_button.handle_event(event):
                    game.state = MENU
            
            # Game update timer
            if event.type == SCREEN_UPDATE and game.state == PLAYING:
                game.update()
                # Update timer speed
                pygame.time.set_timer(SCREEN_UPDATE, game.speed)
            
            # Keyboard controls
            if event.type == pygame.KEYDOWN:
                if game.state == PLAYING:
                    if event.key == pygame.K_UP and game.snake.direction.y != 1:
                        game.snake.direction = pygame.Vector2(0, -1)
                    elif event.key == pygame.K_DOWN and game.snake.direction.y != -1:
                        game.snake.direction = pygame.Vector2(0, 1)
                    elif event.key == pygame.K_RIGHT and game.snake.direction.x != -1:
                        game.snake.direction = pygame.Vector2(1, 0)
                    elif event.key == pygame.K_LEFT and game.snake.direction.x != 1:
                        game.snake.direction = pygame.Vector2(-1, 0)
                    elif event.key == pygame.K_SPACE:
                        game.state = PAUSED
                
                elif game.state == PAUSED:
                    if event.key == pygame.K_SPACE:
                        game.state = PLAYING
                
                elif game.state == MENU:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        game.reset_game()
                
                elif game.state == GAME_OVER:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        game.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        game.state = MENU
        
        # Draw everything
        screen.fill(BACKGROUND)
        game.draw_elements(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
