import os

from asciimatics.screen import Screen, ManagedScreen
from asciimatics.event import KeyboardEvent, MouseEvent

from editor import Editor


def run(screen):
    editor = Editor(screen)
    os.system('mode con: cols=80 lines=25')
    while True:
        event = editor.screen.get_event()
        if isinstance(event, KeyboardEvent):
            key = event.key_code

            if key in (17,):  # ctrl + q
                break

            if key == Screen.KEY_UP:
                editor.move_cursor_up()
            elif key == Screen.KEY_DOWN:
                editor.move_cursor_down()
            elif key == Screen.KEY_LEFT:
                if not editor.highlighted_zone.empty():
                    editor.highlighted_zone
                else:
                    editor.move_cursor_left()
            elif key == Screen.KEY_RIGHT:
                if not editor.highlighted_zone.empty():
                    editor.highlighted_zone.clear()
                else:
                    editor.move_cursor_right()
            elif key == Screen.KEY_DELETE:
                editor.delete()
            elif key == Screen.KEY_BACK:
                editor.backspace()
            # elif key == 393:  # shift + left # TODO: highlights
            #
            #     editor.highlighted_zone.append((editor.cursor_x, editor.cursor_y))
            #     editor.move_cursor_left()
            elif key in (10, 13):  # enter key
                editor.text.insert(editor.cursor_y + 1, editor.text[editor.cursor_y][editor.cursor_x:])
                editor.text[editor.cursor_y] = editor.text[editor.cursor_y][:editor.cursor_x] + '^'
                editor.cursor_y += 1
                editor.cursor_x = 0
            else:
                editor.text[editor.cursor_y] = (
                    editor.text[editor.cursor_y][:editor.cursor_x] +
                    chr(key) +
                    editor.text[editor.cursor_y][editor.cursor_x:]
                )
                editor.cursor_x += 1

        elif isinstance(event, MouseEvent):
            editor.cursor_x, editor.cursor_y = event.x, event.y

        editor.screen.clear_buffer(7, 0, 0)
        for line_index, line in enumerate(editor.text):
            editor.screen.print_at(line, 0, line_index)

        current_sy = editor.text[editor.cursor_y][editor.cursor_x]
        # for x, y in editor.highlighted_chars:
        #     editor.screen.print_at(editor.text[y][x], x, y, bg=1)
        editor.screen.print_at(current_sy, editor.cursor_x, editor.cursor_y, bg=1)

        editor.screen.move(editor.cursor_x, editor.cursor_y)
        editor.screen.refresh()


if __name__ == '__main__':
    with ManagedScreen() as screen:
        run(screen)
