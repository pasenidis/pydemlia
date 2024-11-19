import socket
import threading

class Network:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        self.running = True

    def send(self, message, address):
        self.socket.sendto(message.encode(), address)

    def receive(self):
        while self.running:
            data, addr = self.socket.recvfrom(1024)
            threading.Thread(target=self.handle_message, args=(data.decode(), addr)).start()

    def handle_message(self, message, addr):
        if message.startswith("STORE"):
            # Handle STORE request
            self.handle_store_request(message)
        elif message.startswith("SUCCESS") or message.startswith("FAILURE"):
            # Handle response from STORE request
            pass

    def shutdown(self):
        self.running = False
        self.socket.close()
    
    def handle_store_request(self, message):
        try:
            op, key, value = message['operation'], message['key'], message['value'] or None
            # Logic to store the kv pair locally
            # Send back SUCCESS or FAILURE response
        except KeyError as e:
            print(f"Missing key in store request: {e}")