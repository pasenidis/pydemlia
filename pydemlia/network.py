import socket
import threading
import bencoder
import json

class Network:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        self.socket.settimeout(1)  # Allow graceful shutdown
        self.running = True
        self.handlers = {}  # Map operations to handler methods

    def send(self, message, address):
        try:
            serialized_message = bencoder.bencode(message)
            print(f"Send '{serialized_message}' to {address}")
            self.socket.sendto(serialized_message, address)
        except Exception as e:
            print(f"Error sending message to {address}: {e}")

    def receive(self):
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                message = data.decode()
                print(f"Received {message} from {addr}")
                threading.Thread(target=self.handle_message, args=(message, addr)).start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error receiving message: {e}")

    def handle_message(self, message, addr):
        try:
            parsed_message, length = bencoder.bdecode2(message)
            operation = parsed_message.get('operation')
            if operation in self.handlers:
                self.handlers[operation](parsed_message, addr)
            else:
                print(f"Unknown operation: {operation}")
        except json.JSONDecodeError as e:
            print(f"Failed to decode message from {addr}: {e}")

    def register_handler(self, operation, handler):
        """Register a handler for a specific operation."""
        self.handlers[operation] = handler

    def shutdown(self):
        self.running = False
        self.socket.close()
