import logging
import os
from typing import Optional

from cursor import HighlightedZone


class Editor:
    def __init__(self, screen):
        self.screen = screen
        self.cursor_y, self.cursor_x = 0, 0
        self.cursor_filler = '^'
        self.text = [self.cursor_filler]
        self.highlighted_zone = HighlightedZone(None, None)
        screen.move(self.cursor_x, self.cursor_y)
        if os.path.exists('../log.txt'):
            os.remove('../log.txt')

    @property
    def line_end(self) -> int:
        """
        Вычисляет индекс последнего символа в строке

        :return: индекс последнего символа
        """
        return len(self.text[self.cursor_y]) - 1

    @property
    def previous_line_end(self) -> Optional[int]:
        """
        Проверяет, существует ли предыдущая строка и возвращает индекс последнего символа

        :return: индекс последнего символа предыдущей строки, если она существует
        """
        if not self.cursor_on_first_line:
            return len(self.text[self.cursor_y - 1]) - 1
        raise IndexError("Previous line doesn't exist")

    @property
    def next_line_len(self) -> Optional[int]:
        """
        Проверяет, существует ли следующая строка и возвращает индекс последнего символа

        :return: индекс последнего символа следующей строки, если она существует
        """
        if not self.cursor_on_last_line:
            return len(self.text[self.cursor_y + 1]) - 1
        raise IndexError(r"Next line doesn't exist")

    @property
    def cursor_on_first_line(self) -> bool:
        """
        Проверяет, находится ли курсор на первой строке

        :return: True, если да; False, если нет
        """
        return self.cursor_y == 0

    @property
    def cursor_on_last_line(self) -> bool:
        """
        Проверяет, находится ли курсор на последней строке

        :return: True, если да; False, если нет
        """
        return self.cursor_y == len(self.text) - 1

    @property
    def cursor_on_line_start(self) -> bool:
        """
        Проверяет, находится ли курсор в начале строки

        :return: True, если да; False, если нет
        """
        return self.cursor_x == 0

    @property
    def cursor_on_line_end(self) -> bool:
        """
        Проверяет, находится ли курсор в конце строки

        :return: True, если да; False, если нет
        """
        return self.cursor_x == self.line_end

    def move_cursor_left(self) -> None:
        """
        Смещает курсор влево
        """
        if self.cursor_on_line_start and not self.cursor_on_first_line:
            self.cursor_y -= 1
            self.cursor_x = self.line_end
        elif not self.cursor_on_line_start:
            self.cursor_x = max(0, self.cursor_x - 1)

    def move_cursor_right(self) -> None:
        """
        Смещает курсор вправо
        """
        if self.cursor_on_line_end and not self.cursor_on_last_line:
            self.cursor_y += 1
            self.cursor_x = 0
        elif self.cursor_on_line_end and self.cursor_on_last_line:
            pass
        else:
            self.cursor_x = min(self.line_end + 1, self.cursor_x + 1)

    def move_cursor_up(self) -> None:
        """
        Смещает курсор вверх
        """
        if not self.cursor_y:
            self.cursor_x = 0
        else:
            self.cursor_x = min(self.cursor_x, self.previous_line_end)
            self.cursor_y = max(0, self.cursor_y - 1)

    def move_cursor_down(self) -> None:
        """
        Смещает курсор вниз
        """
        if self.cursor_on_last_line:
            self.cursor_x = self.line_end
        else:
            self.cursor_x = min(self.cursor_x, self.next_line_len)
            self.cursor_y = min(len(self.text) - 1, self.cursor_y + 1)

    def striped_current_line(self) -> str:
        """
        Возвращает строку без последнего символа
        :return: обрезанная строка
        """
        return self.text[self.cursor_y][:-1]

    def current_line_text(self) -> str:
        """
        Возвращает содержимое текущей строки
        :return: строка,на которой стоит курсор
        """
        return self.text[self.cursor_y]

    def next_line_text(self) -> str:
        """
        Возвращает содержимое следующей строки, если такая имеется
        :return: строка, идущая следующей после той, на которой стоит курсор
        """
        if not self.cursor_on_last_line:
            return self.text[self.cursor_y + 1]
        raise IndexError(r"Next line doesn't exist")

    def previous_line_text(self) -> str:
        """
        Возвращает содержимое предыдущей строки, если такая имеется
        :return: строка, идущая перед той, на которой стоит курсор
        """
        if not self.cursor_on_last_line:
            return self.text[self.cursor_y - 1]
        raise IndexError(r"Previous line doesn't exist")

    def delete(self) -> None:
        """
        Удаление символа с использованием delete
        """
        if self.cursor_x == self.line_end:
            if self.line_end:
                self.text[self.cursor_y] = self.striped_current_line() + self.next_line_text()
                self.text.pop(self.cursor_y + 1)
        else:
            self.text[self.cursor_y] = (
                    self.text[self.cursor_y][:self.cursor_x] +
                    self.text[self.cursor_y][self.cursor_x + 1:]
            )

    def backspace(self) -> None:
        """
        Удаление символа с использованием backspace
        """
        if self.cursor_on_line_start:
            if not self.cursor_on_first_line:
                self.cursor_y -= 1
                self.cursor_x = self.line_end
                if self.next_line_len > 0:
                    self.text[self.cursor_y] = self.striped_current_line() + self.next_line_text()
                self.text.pop(self.cursor_y + 1)
        else:
            self.text[self.cursor_y] = (
                    self.text[self.cursor_y][:self.cursor_x - 1] +
                    self.text[self.cursor_y][self.cursor_x:]
            )
            self.cursor_x -= 1

    def press_enter(self) -> None:
        """
        Обрабатывает нажатие клавиши enter
        """
        self.text.insert(self.cursor_y + 1, self.text[self.cursor_y][self.cursor_x:])
        self.text[self.cursor_y] = self.text[self.cursor_y][:self.cursor_x] + '^'
        self.cursor_y += 1
        self.cursor_x = 0

    def write_char(self, ch: str) -> None:
        """
        Вставляет символ на позицию, где в данный момент находится курсор
        :param ch: символ, который требуется вставить
        """
        assert len(ch) == 1
        self.text[self.cursor_y] = (
            self.text[self.cursor_y][:self.cursor_x] +
            ch +
            self.text[self.cursor_y][self.cursor_x:]
        )
        self.cursor_x += 1

    def press_enter_at(self, x: int, y: int):
        """
        Добавляет новую строку по запросу от сервера
        :param x: x координата с сервера
        :param y: y координата с сервера
        :return:
        """
        self.text.insert(y + 1, self.text[y][x:])
        self.text[y] = self.text[y][:x] + '^'

        if self.cursor_y > y:
            self.cursor_y += 1

        if self.cursor_y == y and self.cursor_x > x:
            self.cursor_y += 1
            self.cursor_x -= x - 1

    def write_char_at(self, ch: str, x: int, y: int):
        """
        Печатает символ по запросу от сервера

        :param ch: символ для вставки
        :param x: x координата с сервера
        :param y: y координата с сервера
        """

        logging.info(f"{x=}, {len(self.text)=}; {y=}, {(len(self.text[y]) - 1)=}")
        logging.info((y < len(self.text), x <= len(self.text[y]) - 1))
        if ch == "\n":
            self.press_enter_at(x, y)
        else:
            if y < len(self.text) and x <= len(self.text[y]) - 1:
                self.text[y] = self.text[y][:x] + ch + self.text[y][x:]
                if x < self.cursor_x and y == self.cursor_y:
                    self.move_cursor_right()
