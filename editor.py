import os

from logger import Logger
from cursor import HighlightedZone


class Editor:
    def __init__(self, screen):
        self.screen = screen
        self.cursor_y, self.cursor_x = 0, 0
        self.cursor_filler = '^'
        self.text = [self.cursor_filler]
        self.highlighted_zone = HighlightedZone(None, None)
        screen.move(self.cursor_x, self.cursor_y)
        if os.path.exists('log.txt'):
            os.remove('log.txt')
        self.logger = Logger('log.txt')

    @property
    def current_line_len(self):
        return len(self.text[self.cursor_y]) - 1

    @property
    def previous_line_len(self):
        if not self.cursor_on_first_line:
            return len(self.text[self.cursor_y - 1]) - 1
        raise IndexError("Previous line doesn't exist")

    @property
    def next_line_len(self):
        if not self.cursor_on_last_line:
            return len(self.text[self.cursor_y + 1]) - 1
        raise IndexError(r"Next line doesn't exist")

    @property
    def cursor_on_first_line(self):
        return self.cursor_y == 0

    @property
    def cursor_on_last_line(self):
        return self.cursor_y == len(self.text) - 1

    @property
    def cursor_on_line_end(self):
        return self.cursor_x == self.current_line_len

    @property
    def cursor_on_line_start(self):
        return self.cursor_x == 0

    def move_cursor_left(self):
        if self.cursor_on_line_start and not self.cursor_on_first_line:
            self.cursor_y -= 1
            self.cursor_x = self.current_line_len
        elif not self.cursor_on_line_start:
            self.cursor_x = max(0, self.cursor_x - 1)

    def move_cursor_right(self):
        if self.cursor_on_line_end and not self.cursor_on_last_line:
            self.cursor_y += 1
            self.cursor_x = 0
        elif self.cursor_on_line_end and self.cursor_on_last_line:
            pass
        else:
            self.cursor_x = min(self.current_line_len + 1, self.cursor_x + 1)

    def move_cursor_down(self):
        if self.cursor_on_last_line:
            self.cursor_x = self.current_line_len
        else:
            self.cursor_x = min(self.cursor_x, self.next_line_len)
            self.cursor_y = min(len(self.text) - 1, self.cursor_y + 1)

    def move_cursor_up(self):
        if not self.cursor_y:
            self.cursor_x = 0
        else:
            self.cursor_x = min(self.cursor_x, self.previous_line_len)
            self.cursor_y = max(0, self.cursor_y - 1)

    def striped_current_line(self):
        return self.text[self.cursor_y][:-1]

    def current_line_text(self):
        return self.text[self.cursor_y]

    def next_line_text(self):
        if not self.cursor_on_last_line:
            return self.text[self.cursor_y + 1]
        raise IndexError(r"Next line doesn't exist")

    def previous_line_text(self):
        if not self.cursor_on_last_line:
            return self.text[self.cursor_y - 1]
        raise IndexError(r"Previous line doesn't exist")

    def delete(self):
        if self.cursor_x == self.current_line_len:
            if self.current_line_len:
                self.text[self.cursor_y] = self.striped_current_line() + self.next_line_text()
                self.text.pop(self.cursor_y + 1)
        else:
            self.text[self.cursor_y] = (
                    self.text[self.cursor_y][:self.cursor_x] +
                    self.text[self.cursor_y][self.cursor_x + 1:]
            )

    def backspace(self):
        if self.cursor_on_line_start:
            if not self.cursor_on_first_line:
                self.cursor_y -= 1
                self.cursor_x = self.current_line_len
                if self.next_line_len > 0:
                    self.text[self.cursor_y] = self.striped_current_line() + self.next_line_text()
                self.text.pop(self.cursor_y + 1)
        else:
            self.text[self.cursor_y] = (
                    self.text[self.cursor_y][:self.cursor_x - 1] +
                    self.text[self.cursor_y][self.cursor_x:]
            )
            self.cursor_x -= 1
