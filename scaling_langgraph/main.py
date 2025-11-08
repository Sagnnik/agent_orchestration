import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set up the game window
screen_width = 600
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Snake Game')

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)

# Game constants
snake_size = 20  # grid size
snake_speed = 10  # frames per second

# Font
font = pygame.font.SysFont(None, 36)

clock = pygame.time.Clock()

def random_food_position():
    """Return a food position aligned to the grid."""
    x = random.randrange(0, screen_width, snake_size)
    y = random.randrange(0, screen_height, snake_size)
    return [x, y]

def new_game():
    # Place the head so movement in the initial direction won't collide
    snake = [[140, 100], [120, 100], [100, 100]]  # head at index 0
    snake_direction = 'right'
    food_pos = random_food_position()
    # ensure food not on snake
    while food_pos in snake:
        food_pos = random_food_position()
    score = 0
    return snake, snake_direction, food_pos, score

snake, snake_direction, food_pos, score = new_game()
game_over = False

running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key in (pygame.K_LEFT, pygame.K_a) and snake_direction != 'right':
                    snake_direction = 'left'
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and snake_direction != 'left':
                    snake_direction = 'right'
                elif event.key in (pygame.K_UP, pygame.K_w) and snake_direction != 'down':
                    snake_direction = 'up'
                elif event.key in (pygame.K_DOWN, pygame.K_s) and snake_direction != 'up':
                    snake_direction = 'down'
            else:
                # When game over: allow restart (R) or quit (Q or ESC)
                if event.key == pygame.K_r:
                    snake, snake_direction, food_pos, score = new_game()
                    game_over = False
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False

    if not game_over:
        # Update snake head position
        head_x, head_y = snake[0]
        if snake_direction == 'right':
            head_x += snake_size
        elif snake_direction == 'left':
            head_x -= snake_size
        elif snake_direction == 'up':
            head_y -= snake_size
        elif snake_direction == 'down':
            head_y += snake_size

        new_head = [head_x, head_y]
        snake.insert(0, new_head)

        # Check if snake ate food
        if new_head == food_pos:
            score += 1
            # place new food not on snake
            food_pos = random_food_position()
            while food_pos in snake:
                food_pos = random_food_position()
        else:
            snake.pop()  # remove tail

        # Wall collision
        if (head_x < 0 or head_x >= screen_width or
            head_y < 0 or head_y >= screen_height):
            game_over = True

        # Self collision
        for segment in snake[1:]:
            if new_head == segment:
                game_over = True
                break

    # Draw
    screen.fill(BLACK)
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], snake_size, snake_size))
    pygame.draw.rect(screen, RED, (food_pos[0], food_pos[1], snake_size, snake_size))

    # Draw score
    score_surf = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_surf, (10, 10))

    if game_over:
        go_surf = font.render('Game Over - Press R to restart or Q to quit', True, WHITE)
        rect = go_surf.get_rect(center=(screen_width//2, screen_height//2))
        screen.blit(go_surf, rect)

    pygame.display.flip()
    clock.tick(snake_speed)

pygame.quit()
sys.exit()
