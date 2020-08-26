import curses
import time
import sys
from random import randint

JUMP_KEY = 32  # space
QUIT_KEY = 113  # q
RESTART_KEYS = [10, 13]  # enter/return
GAP_SIZE = 5
WALL_SYMBOL = b'\xF0\x9F\x8C\xB2'  # tree emoji
BIRD_SYMBOL = b'\xF0\x9F\x90\xA5'  # chicken emoji
REFRESH_TIME = 0.1
WALL_FREQUENCY = 15
BIRD_JUMP_HEIGHT = 2
WIDTH, HEIGHT = 50, 20
GAME_OVER_TEXT = 'GAME OVER'
RESTART_TEXT = 'press enter to restart'


class Game:
    def __init__(self):
        self.game_on = True
        self.bird_dead = False
        self.tick_count = 0
        self.wall_xs = []
        self.wall_ys = []
        self.bird = [WIDTH // 2, HEIGHT // 2]
        self.bird_jump_start_ticks = None
        self.score = 0

        self.console = curses.initscr()
        self.console.nodelay(True)
        self.console.keypad(True)
        curses.noecho()
        curses.curs_set(0)

    def game_loop(self):
        while self.game_on:
            self.check_input()
            self.refresh_game()
            self.draw()
            self.tick_count += 1
            if self.bird_dead:
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
            self.bird_jump_start_ticks = self.tick_count

    def refresh_game(self):
        # Check if bird is not out of bounds top or bottom
        if not 0 < self.bird[1] < HEIGHT:
            self.bird_dead = True
            return

        # Get list of indexes of items in wall_xs where value is the same as bird's x
        colliding_x_idx = [i for i, x in enumerate(self.wall_xs) if x == self.bird[0]]

        if colliding_x_idx:
            for i in colliding_x_idx:
                if self.bird[1] == self.wall_ys[i]:
                    self.bird_dead = True
                    return
            else:
                self.score += 1

        if not self.wall_xs or self.tick_count % WALL_FREQUENCY == 0:
            self.new_wall()

        idx_to_remove = [self.wall_xs.index(i) for i in self.wall_xs if i == 0]
        for i in idx_to_remove:
            del self.wall_xs[i]
            del self.wall_ys[i]

        self.wall_xs = [x - 1 for x in self.wall_xs]

        if self.bird_jump_start_ticks is None:
            self.bird[1] += 1
        else:
            self.bird[1] -= 1
            if self.tick_count - self.bird_jump_start_ticks > BIRD_JUMP_HEIGHT:
                self.bird_jump_start_ticks = None

    def draw(self):
        if self.bird_dead:
            return

        self.console.clear()

        for x, y in zip(self.wall_xs, self.wall_ys):
            self.console.addstr(y, x, WALL_SYMBOL)

        self.console.addstr(self.bird[1], self.bird[0], BIRD_SYMBOL)
        self.console.addstr(HEIGHT + 1, WIDTH // 2, str(self.score))

        self.console.refresh()

    def new_wall(self):
        gap_location = randint(
            0,
            HEIGHT - GAP_SIZE
        )

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
            self.bird_dead = False
            self.tick_count = 0
            self.wall_xs = []
            self.wall_ys = []
            self.bird = [WIDTH // 2, HEIGHT // 2]
            self.bird_jump_start_ticks = None
            self.score = 0
            self.console.nodelay(True)
        elif key_pressed == QUIT_KEY:
            self.game_on = False
            self.bird_dead = False


if __name__ == '__main__':
    try:
        game = Game()
        game.game_loop()
    except KeyboardInterrupt:
        curses.endwin()
        sys.exit(0)
