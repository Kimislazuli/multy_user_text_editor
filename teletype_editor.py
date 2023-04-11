import os
import tempfile
import subprocess

from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent, MouseEvent


class Logger:
    def __init__(self, log_file_name: str):
        self.file = open(log_file_name, 'w')

    def log(self, text: str):
        self.file.writeline(text)


def main(screen):
    cursor_y, cursor_x = 0, 0
    text = ['^']
    screen.move(cursor_x, cursor_y)
    screen.clear_buffer(7, 0, 0)
    screen.refresh()

    os.system('mode con: cols=80 lines=25')

    while True:
        event = screen.get_event()

        if isinstance(event, KeyboardEvent):
            key = event.key_code

            if key in (17, 24):  # ctrl + q
                break

            if key == Screen.KEY_UP:
                if not cursor_y:
                    cursor_x = 0
                else:
                    cursor_x = min(cursor_x, len(text[cursor_y - 1]) - 1)
                    cursor_y = max(0, cursor_y - 1)
            elif key == Screen.KEY_DOWN:
                if cursor_y == len(text) - 1:
                    cursor_x = len(text[cursor_y]) - 1
                else:
                    cursor_x = min(cursor_x, len(text[cursor_y + 1]) - 1)
                    cursor_y = min(len(text) - 1, cursor_y + 1)

            elif key == Screen.KEY_LEFT:
                if cursor_x == 0 and cursor_y > 0:
                    cursor_y -= 1
                    cursor_x = len(text[cursor_y]) - 1
                elif cursor_x != 0:
                    cursor_x = max(0, cursor_x - 1)
            elif key == Screen.KEY_RIGHT:
                if cursor_x == len(text[cursor_y]) - 1 and cursor_y != len(text) - 1:
                    cursor_y += 1
                    cursor_x = 0
                elif cursor_x == len(text[cursor_y]) - 1 and cursor_y == len(text) - 1:
                    pass
                else:
                    cursor_x = min(len(text[cursor_y]), cursor_x + 1)
            # elif key == ord('c') and event:
            #     # TODO copy
            #     pass
            # elif key == ord('x') and event.is_ctrl_pressed:
            #     # TODO extract
            #     pass
            # elif key == ord('v') and event.is_ctrl_pressed:
            #     # TODO paste
            #     pass
            # elif key == ord('s') and event.is_ctrl_pressed:
            #     save_to_pdf(text)
            elif key == 10 or key == 13:  # enter key
                text.insert(cursor_y + 1, text[cursor_y][cursor_x:])
                text[cursor_y] = text[cursor_y][:cursor_x] + '^'
                cursor_y += 1
                cursor_x = 0
            else:
                text[cursor_y] = text[cursor_y][:cursor_x] + chr(key) + text[cursor_y][cursor_x:]
                cursor_x += 1

        elif isinstance(event, MouseEvent):
            cursor_x, cursor_y = event.x, event.y

        screen.clear_buffer(7, 0, 0)
        for line_index, line in enumerate(text):
            screen.print_at(line, 0, line_index)

        current_sy = text[cursor_y][cursor_x]
        screen.print_at(current_sy, cursor_x, cursor_y, bg=1)

        screen.move(cursor_x, cursor_y)
        screen.refresh()


# def save_to_pdf(text):
#     with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_txt:
#         temp_txt.write('\n'.join(text).encode())
#     output_pdf = input('Введите имя файла для сохранения в формате PDF: ')
#     subprocess.run(['pandoc', temp_txt.name, '-o', output_pdf])
#     os.unlink(temp_txt.name)


if __name__ == '__main__':
    Screen.wrapper(main)
