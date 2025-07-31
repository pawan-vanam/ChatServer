import pygame
import random
import numpy as np
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
BASE_FPS = 10

# Colors
LIGHT_GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Fonts
font = pygame.font.SysFont('Arial', 24)
game_over_font = pygame.font.SysFont('Arial', 72, bold=True)
title_font = pygame.font.SysFont('Arial', 36, bold=True)

# Sound (corrected to ensure 2-dimensional arrays)
sample_rate = 44100
duration = 0.1
frequency = 440
t = np.linspace(0, duration, int(sample_rate * duration), False)
sound_data = np.sin(2 * np.pi * frequency * t) * 32767
sound_array = np.column_stack((sound_data, sound_data)).astype(np.int16)
eat_sound = pygame.sndarray.make_sound(sound_array)
powerup_sound_data = (sound_array * 0.5).astype(np.int16)
powerup_sound = pygame.sndarray.make_sound(powerup_sound_data)
# Create 2-dimensional array for silence (stereo)
game_over_samples = int(sample_rate * 0.2)
game_over_sound_data = np.zeros((game_over_samples, 2)).astype(np.int16)
game_over_sound = pygame.sndarray.make_sound(game_over_sound_data)

# Snake class
class Snake:
    def __init__(self, color, start_pos, direction):
        self.color = color
        self.body = [start_pos]
        self.direction = direction
        self.score = 0

    def move(self, food_pos, other_snake_body, powerup_pos):
        head = self.body[0]
        possible_directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        safe_directions = []
        for d in possible_directions:
            new_head = (head[0] + d[0], head[1] + d[1])
            if (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT and
                new_head not in self.body[1:] and new_head not in other_snake_body):
                dist = abs(new_head[0] - food_pos[0]) + abs(new_head[1] - food_pos[1])
                safe_directions.append((dist, d))
        
        if safe_directions:
            safe_directions.sort()
            self.direction = safe_directions[0][1]
        else:
            new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
            if (not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT) or
                new_head in self.body[1:] or new_head in other_snake_body):
                return "collision"
        
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            return "collision"
        self.body.insert(0, new_head)
        if new_head == food_pos:
            self.score += 1
            eat_sound.play()
            return True
        elif new_head == powerup_pos:
            powerup_sound.play()
            return "powerup"
        elif new_head in self.body[1:] or new_head in other_snake_body:
            return "collision"
        else:
            self.body.pop()
            return False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color,
                        (self.body[0][0] * GRID_SIZE, self.body[0][1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        for i, segment in enumerate(self.body[1:], start=1):
            darken_factor = min(i / len(self.body), 0.8)
            dark_color = (
                max(0, int(self.color[0] * (1 - darken_factor))),
                max(0, int(self.color[1] * (1 - darken_factor))),
                max(0, int(self.color[2] * (1 - darken_factor)))
            )
            pygame.draw.rect(screen, dark_color,
                            (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def has_safe_move(self, other_snake_body):
        head = self.body[0]
        possible_directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for d in possible_directions:
            new_head = (head[0] + d[0], head[1] + d[1])
            if (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT and
                new_head not in self.body[1:] and new_head not in other_snake_body):
                return True
        return False

# Setup function
def setup():
    global screen, snake1, snake2, food_pos, powerup_pos, game_over, game_started, score_history, high_score, level
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Autonomous Snake Game")
    snake1 = Snake(RED, (5, 5), (1, 0))
    snake2 = Snake(BLUE, (GRID_WIDTH - 5, GRID_HEIGHT - 5), (-1, 0))
    food_pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    powerup_pos = None
    game_over = False
    game_started = False
    score_history = []
    high_score = 0
    level = 1

# Update loop
def update_loop():
    global food_pos, powerup_pos, game_over, game_started, score_history, high_score, level
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if not game_started and event.key == pygame.K_SPACE:
                game_started = True
            if game_over and event.key == pygame.K_r:
                setup()
                game_started = True

    if not game_started:
        screen.fill(LIGHT_GRAY)
        start_text = title_font.render("Press SPACE to Start", True, BLACK)
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
    elif not game_over:
        if random.random() < 0.01 and powerup_pos is None:
            powerup_pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            while powerup_pos in snake1.body or powerup_pos in snake2.body:
                powerup_pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        
        result1 = snake1.move(food_pos, snake2.body, powerup_pos)
        result2 = snake2.move(food_pos, snake1.body, powerup_pos)
        if result1 == "collision" or result2 == "collision":
            game_over = True
            game_over_sound.play()
            score_history.append((snake1.score, snake2.score))
            high_score = max(high_score, snake1.score + snake2.score)
        elif result1 == "powerup":
            powerup_pos = None
            BASE_FPS = min(BASE_FPS + 2, 20)
        elif result2 == "powerup":
            powerup_pos = None
            if len(snake1.body) > 2: snake1.body.pop()
            if len(snake2.body) > 2: snake2.body.pop()
        elif result1 or result2:
            food_pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            while food_pos in snake1.body or food_pos in snake2.body:
                food_pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            level = max(1, (snake1.score + snake2.score) // 5 + 1)
        
        if not snake1.has_safe_move(snake2.body) and not snake2.has_safe_move(snake1.body):
            game_over = True
            game_over_sound.play()
            score_history.append((snake1.score, snake2.score))
            high_score = max(high_score, snake1.score + snake2.score)
        
        if not game_over:
            screen.fill(LIGHT_GRAY)
            for x in range(0, WIDTH, GRID_SIZE):
                pygame.draw.line(screen, (150, 150, 150), (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, GRID_SIZE):
                pygame.draw.line(screen, (150, 150, 150), (0, y), (WIDTH, y))
            snake1.draw(screen)
            snake2.draw(screen)
            pygame.draw.rect(screen, GREEN, (food_pos[0] * GRID_SIZE, food_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            if powerup_pos:
                pygame.draw.rect(screen, YELLOW, (powerup_pos[0] * GRID_SIZE, powerup_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            title_text = title_font.render("Autonomous Snake Game", True, BLACK)
            score1_text = font.render(f"Red Score: {snake1.score}", True, RED)
            score2_text = font.render(f"Blue Score: {snake2.score}", True, BLUE)
            level_text = font.render(f"Level: {level}", True, BLACK)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 10))
            screen.blit(score1_text, (10, HEIGHT - 80))
            screen.blit(score2_text, (WIDTH - score2_text.get_width() - 10, HEIGHT - 80))
            screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT - 40))
    else:
        screen.fill(LIGHT_GRAY)
        game_over_text = game_over_font.render("Game Over", True, BLACK)
        game_over_outline = game_over_font.render("Game Over", True, (150, 0, 0))
        score1_text = font.render(f"Red Score: {snake1.score}", True, RED)
        score2_text = font.render(f"Blue Score: {snake2.score}", True, BLUE)
        high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
        restart_text = font.render("Press R to Restart", True, BLACK)
        screen.blit(game_over_outline, (WIDTH // 2 - game_over_outline.get_width() // 2 - 2, HEIGHT // 2 - game_over_outline.get_height() // 2 - 2))
        screen.blit(game_over_outline, (WIDTH // 2 - game_over_outline.get_width() // 2 + 2, HEIGHT // 2 - game_over_outline.get_height() // 2 + 2))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
        screen.blit(score1_text, (WIDTH // 2 - score1_text.get_width() // 2, HEIGHT // 2 + 50))
        screen.blit(score2_text, (WIDTH // 2 - score2_text.get_width() // 2, HEIGHT // 2 + 80))
        screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 + 120))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 160))
        if len(score_history) >= 1:
            last_score_text = font.render(f"Last Game: {score_history[-1][0]} - {score_history[-1][1]}", True, BLACK)
            screen.blit(last_score_text, (WIDTH // 2 - last_score_text.get_width() // 2, HEIGHT // 2 + 200))
        if len(score_history) >= 2:
            second_last_score_text = font.render(f"2nd Last: {score_history[-2][0]} - {score_history[-2][1]}", True, BLACK)
            screen.blit(second_last_score_text, (WIDTH // 2 - second_last_score_text.get_width() // 2, HEIGHT // 2 + 230))
        if len(score_history) >= 3:
            third_last_score_text = font.render(f"3rd Last: {score_history[-3][0]} - {score_history[-3][1]}", True, BLACK)
            screen.blit(third_last_score_text, (WIDTH // 2 - third_last_score_text.get_width() // 2, HEIGHT // 2 + 260))
    pygame.display.flip()
    return True

# Main loop
async def main():
    setup()
    while True:
        if not update_loop():
            break
        await asyncio.sleep(1.0 / BASE_FPS)

# Run the game
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())