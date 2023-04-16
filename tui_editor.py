import os
import tempfile
import subprocess

from asciimatics.screen import Screen, ManagedScreen
import asciimatics
from asciimatics.event import KeyboardEvent, MouseEvent


class Logger:
    def __init__(self, log_file_name: str):
        self.file = open(log_file_name, 'a')

    def log(self, text: str):
        self.file.write(f"{text}\n")


class Editor:
    def __init__(self, screen):
        self.screen = screen
        self.cursor_y, self.cursor_x = 0, 0
        self.text = ['^']
        self.highlighted_chars = []
        screen.move(self.cursor_x, self.cursor_y)
        if os.path.exists('log.txt'):
            os.remove('log.txt')
        self.logger = Logger('log.txt')

    @property
    def current_line_len(self):
        return len(self.text[self.cursor_y]) - 1

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
            self.cursor_x = len(self.text[self.cursor_y]) - 1
        else:
            self.cursor_x = min(self.cursor_x, len(self.text[self.cursor_y + 1]) - 1)
            self.cursor_y = min(len(self.text) - 1, self.cursor_y + 1)

    def move_cursor_up(self):
        if not self.cursor_y:
            self.cursor_x = 0
        else:
            self.cursor_x = min(self.cursor_x, len(self.text[self.cursor_y - 1]) - 1)
            self.cursor_y = max(0, self.cursor_y - 1)

    def run(self):
        while True:
            event = self.screen.get_event()
            if isinstance(event, KeyboardEvent):
                key = event.key_code

                if key in (17,):  # ctrl + q
                    break

                if key == Screen.KEY_UP:
                    self.move_cursor_up()
                elif key == Screen.KEY_DOWN:
                    self.move_cursor_down()
                elif key == Screen.KEY_LEFT:
                    if self.highlighted_chars:
                        self.highlighted_chars.clear()
                    else:
                        self.move_cursor_left()
                elif key == Screen.KEY_RIGHT:
                    if self.highlighted_chars:
                        self.highlighted_chars.clear()
                    else:
                        self.move_cursor_right()
                elif key == 393:  # shift + left
                    self.highlighted_chars.append((self.cursor_x, self.cursor_y))
                    self.move_cursor_left()
                elif key == 10 or key == 13:  # enter key
                    self.text.insert(self.cursor_y + 1, self.text[self.cursor_y][self.cursor_x:])
                    self.text[self.cursor_y] = self.text[self.cursor_y][:self.cursor_x] + '^'
                    self.cursor_y += 1
                    self.cursor_x = 0
                else:
                    self.text[self.cursor_y] = self.text[self.cursor_y][:self.cursor_x] + chr(key) + self.text[self.cursor_y][self.cursor_x:]
                    self.cursor_x += 1

            elif isinstance(event, MouseEvent):
                self.cursor_x, self.cursor_y = event.x, event.y

            self.screen.clear_buffer(7, 0, 0)
            for line_index, line in enumerate(self.text):
                self.screen.print_at(line, 0, line_index)

            current_sy = self.text[self.cursor_y][self.cursor_x]
            for x, y in self.highlighted_chars:
                self.screen.print_at(self.text[y][x], x, y, bg=1)
            self.screen.print_at(current_sy, self.cursor_x, self.cursor_y, bg=1)

            self.screen.move(self.cursor_x, self.cursor_y)
            self.screen.refresh()


if __name__ == '__main__':
    with ManagedScreen() as screen:
        editor = Editor(screen)
        editor.run()
