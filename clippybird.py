import curses
import time
import sys
from random import randint

JUMP_KEY = 32  # space
QUIT_KEY = 113  # q
RESTART_KEYS = [10, 13]  # enter/return
GAP_SIZE = 5  # size of gap in walls
WALL_SYMBOL = b'\xF0\x9F\x8C\xB2'  # tree emoji
BIRD_SYMBOL = b'\xF0\x9F\x90\xA5'  # chicken emoji
REFRESH_TIME = 0.1  # sleep time between ticks
WALL_FREQUENCY = 15  # ticks before creating new wall
BIRD_JUMP_HEIGHT = 3
WIDTH, HEIGHT = 50, 20
GAME_OVER_TEXT = 'GAME OVER'
RESTART_TEXT = 'press enter to restart'


class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dead = False
        self.jump_start_ticks = None

    def up(self):
        self.y -= 1

    def down(self):
        self.y += 1

    def start_jump(self, starting_ticks):
        self.jump_start_ticks = starting_ticks

    def end_jump(self):
        self.jump_start_ticks = None

    def jumped_enough(self, current_ticks):
        return current_ticks - self.jump_start_ticks >= BIRD_JUMP_HEIGHT

    def is_out_of_bounds(self):
        return not 0 <= self.y < HEIGHT

    def advance(self, current_ticks):
        if self.jump_start_ticks is None:
            self.down()
        elif self.jumped_enough(current_ticks):
            self.end_jump()
        else:
            self.up()
        if self.is_out_of_bounds():
            self.dead = True


class Game:
    def __init__(self):
        self.game_on = True
        self.tick_count = 0
        self.wall_xs = []
        self.wall_ys = []
        self.bird = Bird(WIDTH // 2, HEIGHT // 2)
        self.score = 0

        self.console = curses.initscr()
        self.console.nodelay(True)
        self.console.keypad(True)
        curses.noecho()
        curses.curs_set(0)

    def game_loop(self):
        while self.game_on:
            self.check_input()
            self.check_collision()
            self.move_walls()
            self.bird.advance(self.tick_count)
            self.draw()
            self.tick_count += 1
            if self.bird.dead:
                self.prompt_restart()
            time.sleep(REFRESH_TIME)

        curses.endwin()
        sys.exit(0)

    def check_input(self):
        pressed_key = self.console.getch()
        if not pressed_key:
            return
        if pressed_key == QUIT_KEY:
            self.game_on = False
        elif pressed_key == JUMP_KEY:
            self.bird.start_jump(self.tick_count)

    def check_collision(self):
        # Get list of indexes of items in wall_xs where value is the same as bird's x
        colliding_x_idx = [i for i, x in enumerate(self.wall_xs) if x == self.bird.x]

        # Check if any of those indexes match bird.y on wall_ys
        if colliding_x_idx:
            for i in colliding_x_idx:
                if self.bird.y == self.wall_ys[i]:
                    self.bird.dead = True
                    return
            else:
                self.score += 1

    def move_walls(self):
        # Check if new wall needs to be added
        if not self.wall_xs or self.tick_count % WALL_FREQUENCY == 0:
            self.new_wall()

        # Check if walls need to be removed
        idx_to_remove = [self.wall_xs.index(i) for i in self.wall_xs if i == 0]
        if idx_to_remove:
            for i in idx_to_remove:
                del self.wall_xs[i]
                del self.wall_ys[i]

        # Actually move walls
        self.wall_xs = [x - 1 for x in self.wall_xs]

    def draw(self):
        if self.bird.dead:
            return

        self.console.clear()

        # x and y are reversed in curses
        for x, y in zip(self.wall_xs, self.wall_ys):
            self.console.addstr(y, x, WALL_SYMBOL)

        self.console.addstr(self.bird.y, self.bird.x, BIRD_SYMBOL)
        self.console.addstr(HEIGHT, WIDTH // 2, str(self.score))
        self.console.refresh()

    def new_wall(self):
        gap_location = randint(1, HEIGHT - int(GAP_SIZE / 2) - 1)
        for i in range(HEIGHT):
            if abs(gap_location - i) > GAP_SIZE / 2:
                self.wall_xs.append(WIDTH)
                self.wall_ys.append(i)

    def prompt_restart(self):
        self.console.nodelay(False)
        self.console.addstr(
            HEIGHT // 2,
            (WIDTH // 2) - (len(GAME_OVER_TEXT) // 2),
            GAME_OVER_TEXT
        )
        self.console.addstr(
            HEIGHT // 2 + 2,
            (WIDTH // 2) - (len(RESTART_TEXT) // 2),
            RESTART_TEXT
        )
        self.console.refresh()

        key_pressed = self.console.getch()
        if key_pressed in RESTART_KEYS:
            self.game_on = True
            self.bird.dead = False
            self.tick_count = 0
            self.wall_xs = []
            self.wall_ys = []
            self.bird.x, self.bird.y = WIDTH // 2, HEIGHT // 2
            self.bird.end_jump()
            self.score = 0
            self.console.nodelay(True)
        elif key_pressed == QUIT_KEY:
            self.game_on = False
            self.bird.dead = False


if __name__ == '__main__':
    try:
        game = Game()
        game.game_loop()
    except KeyboardInterrupt:
        curses.endwin()
        sys.exit(0)
