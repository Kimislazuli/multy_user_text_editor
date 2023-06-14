import socket
import json
import threading
from typing import Optional

SERVER_HOST = 'localhost'
SERVER_PORT = 8000
BUFFER_SIZE = 1024


class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((SERVER_HOST, SERVER_PORT))
        self.documents = {}
        self.client_sockets = {}

    def create_document(self, name) -> int:
        """
        Создает новый документ
        :param name: имя, под которым будет сохранён созданный документ
        :return: id документа
        """
        document_id = str(len(self.documents) + 1)
        self.documents[document_id] = {"name": name, "content": ['^'], "clients": []}
        print(f"{name}: {document_id}")
        return document_id

    def connect_to_document(self, document_id, client_address) -> Optional[list[str]]:
        """
        Подключает к документу конкретного пользователя
        :param document_id: id документа
        :param client_address: ip пользователя, подключившегося к документу
        :return: если такой документ существует, возвращает его содержимое
        """
        if document_id in self.documents:
            self.documents[document_id]['clients'].append(client_address)
            print(f"{client_address} connected to {document_id}")
            return self.documents[document_id]['content']
        return None

    def write_to_document(self, document_id, x, y, symbol, writer_address: str) -> bool:
        """
        Обновляет документ на сервере в соответствии с локальными изменениями пользователя
        :param document_id: id документа
        :param x: номер символа в строке для изменения
        :param y: номер строки для изменения
        :param symbol: символ, введённый пользователем
        :param writer_address: ip пославшего запрос
        :return: статус успешности изменения документа на сервере
        """
        if document_id not in self.documents:
            return False
        while len(self.documents[document_id]['content']) <= y:
            self.documents[document_id]['content'].append('^')

        if len(self.documents[document_id]['content'][y]) < x:
            row_len = len(self.documents[document_id]['content'][y])
            self.documents[document_id]['content'][y] = \
                self.documents[document_id]['content'][y][:-1] + ' ' * (x - row_len - 1) + '^'

        self.documents[document_id]['content'][y] = self.documents[document_id]['content'][y][:x] + symbol + \
                                                    self.documents[document_id]['content'][y][x:]

        for client_address in self.documents[document_id]['clients']:
            if client_address != writer_address:
                client_socket = self.client_sockets[client_address]
                response = {
                    "action": "write",
                    "data": {
                        "document_id": document_id,
                        "x": x,
                        "y": y,
                        "symbol": symbol
                    }
                }
                print(f"Sending to {client_address} than {writer_address} write {symbol} to x: {x} y: {y}")
                client_socket.send(json.dumps(response).encode())

        return True

    def disconnect_from_document(self, client_address: str) -> bool:
        """
        Отключение от документа
        :param client_address: ip адрес взаимодействующего с документом
        :return: статус успешности операции отключения от документа
        """
        if client_address in self.clients:
            document_id = self.clients[client_address]
            self.documents[document_id]['clients'].remove(client_address)
            del self.clients[client_address]

            self.client_sockets[client_address].close()
            del self.client_sockets[client_address]

            return True
        return False

    def handle_client(self, client_socket, client_address) -> None:
        """
        Обрабатывает клиента
        :param client_socket: сокет, с которым работает пользователь
        :param client_address: ip адрес пользователя
        """
        print(client_socket, client_address)
        while True:
            try:
                request = client_socket.recv(BUFFER_SIZE).decode()
            except ConnectionResetError:
                print(f"Client {client_address} disconnected")
                break
            
            if not request:
                break

            request = json.loads(request)

            action = request.get('action')
            data = request.get('data')

            if action == 'create':
                document_id = self.create_document(data['name'])
                response = {"action": "create", "data": {"document_id": document_id}}

            elif action == 'connect':
                content = self.connect_to_document(data['document_id'], client_address)
                response = {"action": "connect", "data": {"content": content}}

            elif action == 'write':
                print(f"{client_address} write {data['symbol']} to doc{data['document_id']}")
                success = self.write_to_document(data['document_id'], data['x'], data['y'], data['symbol'],
                                                 client_address)
                response = {"action": "write", "data": {"success": success}}

            elif action == 'disconnect':
                success = self.disconnect_from_document(client_address)
                response = {"action": "disconnect", "data": {"success": success}}

            client_socket.send(json.dumps(response).encode())

        client_socket.close()

    def start(self):
        """
        Цикл работы сервера
        """
        self.socket.listen(5)
        print(f"Server started on {SERVER_HOST}:{SERVER_PORT}")

        while True:
            client_socket, client_address = self.socket.accept()
            self.client_sockets[client_address] = client_socket
            print(f"New connection from {client_address}")
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()


if __name__ == "__main__":
    try:
        server = Server()
        server.create_document("test_doc")
        server.start()
    except KeyboardInterrupt:
        server.socket.close()
