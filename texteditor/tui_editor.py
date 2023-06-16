import json
import logging
import os
import socket
import threading

from asciimatics.screen import Screen, ManagedScreen
from asciimatics.event import KeyboardEvent, MouseEvent

from editor import Editor

logging.basicConfig(level=logging.INFO, filename="logs_client.txt", filemode="w",
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def listen_to_server(sock, editor) -> None:
    """
    Слушает обновления с сервера
    :param sock: сокет, по которому происхдит взаимодействие с сервером
    :param editor: редактор
    """
    while True:
        logging.info("Waiting for resp")
        data = sock.recv(1024)
        logging.info("Response received")
        if data:
            response = json.loads(data.decode())
            logging.info(f"response: {response}")
            if response['action'] == "write" and 'success' not in response['data']:
                x = response['data']['x']
                y = response['data']['y']
                symbol = response['data']['symbol']
                logging.info(f"x: {x}, y: {y}, char: {symbol}")
                editor.write_char_at(symbol, x, y)
            elif response["action"] == "connect":
                editor.text = response["data"]["content"]


def run(screen, sock) -> None:
    # для теста, чтобы все конектились к одному файлу
    document_id = "1"

    # request = {
    #     "action": "create",
    #     "data": {
    #         "name": "test_document"
    #     }
    # }
    # sock.send(json.dumps(request).encode())
    #
    #
    # response = json.loads(sock.recv(1024).decode())
    # document_id = response['data']['document_id']

    # os.system('mode con: cols=80 lines=25')  # WINDOWS ONLY
    editor = Editor(screen)

    threading.Thread(target=listen_to_server, args=(sock, editor)).start()

    request = {
        "action": "connect",
        "data": {
            "document_id": document_id
        }
    }

    sock.send(json.dumps(request).encode())

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

            elif key in (10, 13):  # enter key
                request = {
                    "action": "write",
                    "data": {
                        "document_id": document_id,
                        "x": editor.cursor_x,
                        "y": editor.cursor_y,
                        "symbol": '\n'
                    }
                }
                sock.send(json.dumps(request).encode())
                editor.press_enter()

            try:
                symbol = chr(key)
            except ValueError:
                continue

            else:
                request = {
                    "action": "write",
                    "data": {
                        "document_id": document_id,
                        "x": editor.cursor_x,
                        "y": editor.cursor_y,
                        "symbol": chr(key)
                    }
                }

                editor.write_char(chr(key))

                sock.send(json.dumps(request).encode())

        elif isinstance(event, MouseEvent):
            editor.cursor_x, editor.cursor_y = event.x, event.y

        editor.screen.clear_buffer(7, 0, 0)
        for line_index, line in enumerate(editor.text):
            editor.screen.print_at(line, 0, line_index)

        try:
            current_sy = editor.text[editor.cursor_y][editor.cursor_x]
        except IndexError:
            continue

        editor.screen.print_at(current_sy, editor.cursor_x, editor.cursor_y, bg=1)

        editor.screen.move(editor.cursor_x, editor.cursor_y)
        editor.screen.refresh()


if __name__ == '__main__':
    try:
        sock = socket.socket()
        sock.connect(("localhost", 8000))
        with ManagedScreen() as screen:
            run(screen, sock)
    except KeyboardInterrupt:
        sock.close()
