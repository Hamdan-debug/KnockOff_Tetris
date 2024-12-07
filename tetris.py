import pygame
import random
import os
import json

# Constants
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 600
BLOCK_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
FPS = 60
LINE_CLEAR_SOUND = 'lineclear.mp3'
GAME_OVER_SOUND = 'gameover.mp3'

pygame.mixer.init(channels=2)
pygame.mixer.music.load('gamemusic.mp3')
pygame.mixer.music.play(-1)
# Piece shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0],
     [1, 1, 1]],  # J
    [[0, 0, 1],
     [1, 1, 1]],  # L
    [[1, 1],
     [1, 1]],  # O
    [[0, 1, 1],
     [1, 1, 0]],  # S
    [[0, 1, 0],
     [1, 1, 1]],  # T
    [[1, 1, 0],
     [0, 1, 1]]  # Z
]

# Colors
COLORS = [
    (0, 255, 255),  # Cyan
    (0, 0, 255),    # Blue
    (255, 165, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (128, 0, 128),  # Purple
    (255, 0, 0)     # Red
]

class Tetris:
    def __init__(self):
        pygame.init()
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(' KnockOff Tetris')
        self.clock = pygame.time.Clock()

        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.current_piece = None
        self.current_piece_color = (0, 0, 0)
        self.current_piece_pos = [0, 0]

        self.score = 0
        self.level = 1
        self.speed = 500  # Milliseconds
        self.running = True

        # Load or initialize high score
        self.high_score = self.load_high_score()

        # Load sounds
        self.line_clear_sound = pygame.mixer.Sound(LINE_CLEAR_SOUND)
        self.game_over_sound = pygame.mixer.Sound(GAME_OVER_SOUND)

        self.reset_game()

    def load_high_score(self):
        if os.path.exists("high_score.json"):
            with open("high_score.json", "r") as f:
                return json.load(f).get("high_score", 0)
        return 0

    def save_high_score(self):
        with open("high_score.json", "w") as f:
            json.dump({"high_score": self.high_score}, f)

    def reset_game(self):
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.level = 1
        self.speed = 500
        self.spawn_piece()

    def spawn_piece(self):
        shape_index = random.randint(0, len(SHAPES) - 1)
        self.current_piece = SHAPES[shape_index]
        self.current_piece_color = COLORS[shape_index]
        self.current_piece_pos = [0, BOARD_WIDTH // 2 - len(self.current_piece[0]) // 2]

        if self.collision():
            self.game_over()

    def collision(self):
        for r, row in enumerate(self.current_piece):
            for c, val in enumerate(row):
                if val and (self.current_piece_pos[0] + r >= BOARD_HEIGHT or
                             self.current_piece_pos[1] + c < 0 or
                             self.current_piece_pos[1] + c >= BOARD_WIDTH or
                             self.board[self.current_piece_pos[0] + r][self.current_piece_pos[1] + c]):
                    return True
        return False

    def merge(self):
        for r, row in enumerate(self.current_piece):
            for c, val in enumerate(row):
                if val:
                    self.board[self.current_piece_pos[0] + r][self.current_piece_pos[1] + c] = self.current_piece_color

    def clear_lines(self):
        lines_cleared = 0
        for r in range(BOARD_HEIGHT - 1, -1, -1):
            if all(self.board[r]):
                lines_cleared += 1
                del self.board[r]
                self.board.insert(0, [0] * BOARD_WIDTH)
        if lines_cleared > 0:
            self.line_clear_sound.play()
            self.score += lines_cleared * 10
            self.check_level_up()

    def check_level_up(self):
        new_level = self.score // 100 + 1
        if new_level > self.level:
            self.level = new_level
            self.speed = max(100, self.speed - 50)  # Increase speed

    def rotate_piece(self):
        rotated_piece = list(zip(*self.current_piece[::-1]))
        self.current_piece = rotated_piece

        if self.collision():
            self.current_piece = rotated_piece[::-1]  # Revert if collision occurs

    def drop_piece(self):
        self.current_piece_pos[0] += 1
        if self.collision():
            self.current_piece_pos[0] -= 1
            self.merge()
            self.clear_lines()
            self.spawn_piece()

    def draw_board(self):
        for r in range(BOARD_HEIGHT):
            for c in range(BOARD_WIDTH):
                if self.board[r][c]:
                    pygame.draw.rect(self.screen, self.board[r][c], (c * BLOCK_SIZE, r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def draw_current_piece(self):
        for r in range(len(self.current_piece)):
            for c in range(len(self.current_piece[r])):
                if self.current_piece[r][c]:
                    pygame.draw.rect(self.screen, self.current_piece_color,
                                     ((self.current_piece_pos[1] + c) * BLOCK_SIZE, 
                                      (self.current_piece_pos[0] + r) * BLOCK_SIZE, 
                                      BLOCK_SIZE, BLOCK_SIZE))

    def run_game(self):
        while self.running:
            self.screen.fill((0, 0, 0))

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.current_piece_pos[1] -= 1
                        if self.collision():
                            self.current_piece_pos[1] += 1
                    elif event.key == pygame.K_RIGHT:
                        self.current_piece_pos[1] += 1
                        if self.collision():
                            self.current_piece_pos[1] -= 1
                    elif event.key == pygame.K_DOWN:
                        self.drop_piece()
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()

            # Drop the piece over time
            self.drop_piece()

            # Drawing
            self.draw_board()
            self.draw_current_piece()

            # Display score and level
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Score: {self.score}', 1, (255, 255, 255))
            level_text = font.render(f'Level: {self.level}', 1, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(level_text, (10, 40))

            pygame.display.flip()
            self.clock.tick(FPS)

            # Handle game speed
            pygame.time.delay(self.speed)

        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        
        self.game_over_sound.play()
        pygame.time.delay(1000)
        pygame.quit()

    def game_over(self):
        self.running = False
        print("Game Over! Your Score:", self.score)


if __name__ == '__main__':
    game = Tetris()
    game.run_game()