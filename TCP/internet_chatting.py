import socket
import threading
import os
import random

class ChatClient:
    def __init__(self, client_name, client_port):
        self.client_name = client_name
        self.client_port = client_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('127.0.0.1', self.client_port))

    def send_message(self, message):
        self.client_socket.sendall(message.encode())

    def receive_message(self):
        data = self.client_socket.recv(1024)
        return data.decode()

    def transfer_file(self, filename):
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                self.client_socket.sendall(f"transfer {filename}".encode())
                if self.receive_message() == "ready":
                    while True:
                        data = file.read(1024)
                        if not data:
                            break
                        self.client_socket.sendall(data)
                    print(f"File '{filename}' transferred successfully.")
        else:
            print(f"File {filename} does not exist.")

class ChatServer:
    def __init__(self, server_name, server_port):
        self.server_name = server_name
        self.server_port = server_port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1', self.server_port))
        self.server_socket.listen(1)
        self.port_to_username = {}

    def accept_connection(self):
        connection, address = self.server_socket.accept()
        print(f"Connection has been established with user")
        return connection

    def receive_message(self, connection):
        data = connection.recv(1024)
        return data.decode()

    def receive_file(self, connection, filename):
        connection.sendall("ready".encode())
        with open(filename, 'wb') as file:
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                file.write(data)
        print("File has been received on the receiver's end.")  # Moved print statement here

    def get_username_by_port(self, port):
        return self.port_to_username.get(port)

def server_read_thread(chat_server, sender_name):
    connection = chat_server.accept_connection()
    port = connection.getpeername()[1]
    chat_server.port_to_username[port] = sender_name
    while True:
        message = chat_server.receive_message(connection)
        if message.startswith("transfer"):
            filename = message.split()[1]
            chat_server.receive_file(connection, filename)
        else:
            print(f"{message}")  # Modified to display sender's name in the next line

def client_write_thread(chat_client, server_name):
    while True:
        message = input(f"")
        if message.startswith("transfer"):
            filename = message.split()[1]
            chat_client.transfer_file(filename)
        else:
            full_message = f"{chat_client.client_name}: {message}"  # to include receiver's name 
            chat_client.send_message(full_message)

if __name__ == "__main__":
    client_name = input("Enter your name: ")
    if client_name:
        client_port = random.randint(1024, 65535)
        chat_server = ChatServer(client_name, client_port)
        print(f"Server listening on port {client_port}")

        server_port = int(input("Enter the port number of the other user: "))
        chat_client = ChatClient(client_name, server_port)
        server_read_thread = threading.Thread(target=server_read_thread, args=(chat_server, chat_client.client_name))
        client_write_thread = threading.Thread(target=client_write_thread, args=(chat_client, chat_server.server_name))

        server_read_thread.start()
        client_write_thread.start()

        server_read_thread.join()
        client_write_thread.join()