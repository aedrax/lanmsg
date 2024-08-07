import socket
import threading
import sys
from typing import Dict, List, Tuple

BROADCAST_PORT: int = 12345
CHAT_PORT: int = 12346
BROADCAST_INTERVAL: int = 5  # seconds

class Peer:
    def __init__(self, username: str, host: str = '0.0.0.0') -> None:
        self.server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, CHAT_PORT))
        self.server.listen()
        self.username: str = username
        self.peers: Dict[socket.socket, str] = {}
        self.channels: Dict[str, List[socket.socket]] = {}

        # Setup UDP broadcast socket
        self.broadcast_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcast_socket.settimeout(BROADCAST_INTERVAL)
        self.broadcast_socket.bind((host, BROADCAST_PORT))

    def broadcast_presence(self) -> None:
        """
        Broadcasts the presence of the chat server to all peers in the network.
        """
        while True:
            message: str = f"{self.username}::{self.server.getsockname()[0]}"
            self.broadcast_socket.sendto(message.encode(), ('<broadcast>', BROADCAST_PORT))
            threading.Event().wait(BROADCAST_INTERVAL)

    def listen_for_peers(self) -> None:
        """
        Listens for incoming broadcast messages from other peers in the network.
        If a new peer is found, it connects to the peer.
        """
        while True:
            try:
                data, addr = self.broadcast_socket.recvfrom(1024)
                message: str = data.decode()
                username, peer_ip = message.split("::")
                if username != self.username and peer_ip not in self.peers:
                    self.connect_to_peer(peer_ip)
            except socket.timeout:
                continue

    def broadcast(self, message: str, channel: str) -> None:
        """
        Broadcasts the message to all peers in the given channel.
        """
        for peer in self.channels[channel]:
            peer.send(message.encode())

    def handle_peer(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        """
        Handles the connection with a peer.
        conn: socket.socket - The socket object for the connection.
        addr: Tuple[str, int] - The address of the peer.
        """
        conn.send(f"Connected to {self.username}'s chat. Please enter your username: ".encode())
        peer_username: str = conn.recv(1024).decode().strip()
        self.peers[conn] = peer_username

        conn.send(f"Enter the channel you want to join: ".encode())
        channel: str = conn.recv(1024).decode().strip()

        if channel not in self.channels:
            self.channels[channel] = []

        self.channels[channel].append(conn)
        conn.send(f"Joined channel {channel}. You can now start chatting.\n".encode())

        while True:
            try:
                message: str = conn.recv(1024).decode()
                if message.startswith("/msg"):
                    _, recipient, private_msg = message.split(" ", 2)
                    for peer, name in self.peers.items():
                        if name == recipient:
                            peer.send(f"Private message from {self.peers[conn]}: {private_msg}\n".encode())
                            break
                else:
                    self.broadcast(f"{self.peers[conn]}@{channel}: {message}", channel)
            except (ConnectionResetError, ConnectionAbortedError):
                conn.close()
                self.channels[channel].remove(conn)
                del self.peers[conn]
                break

    def handle_input(self) -> None:
        """
        Handles the input from the user.
        """
        while True:
            command: str = input()
            if command.startswith("/msg"):
                _, recipient, private_msg = command.split(" ", 2)
                for peer, name in self.peers.items():
                    if name == recipient:
                        peer.send(f"Private message from {self.username}: {private_msg}\n".encode())
                        break
            else:
                channel: str = list(self.channels.keys())[0]  # Assuming first channel for simplicity
                self.broadcast(f"{self.username}@{channel}: {command}", channel)

    def connect_to_peer(self, peer_ip: str) -> None:
        """
        Connects to the peer with the given IP address.
        peer_ip: str - The IP address of the peer.
        """
        peer_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((peer_ip, CHAT_PORT))
        self.peers[peer_socket] = None
        peer_handler: threading.Thread = threading.Thread(target=self.handle_peer, args=(peer_socket, (peer_ip, CHAT_PORT)))
        peer_handler.start()

    def run(self) -> None:
        """
        Starts the chat server.
        """
        print(f"{self.username}'s LanMsg chat server started...")

        broadcast_thread: threading.Thread = threading.Thread(target=self.broadcast_presence)
        broadcast_thread.daemon = True
        broadcast_thread.start()

        listen_thread: threading.Thread = threading.Thread(target=self.listen_for_peers)
        listen_thread.daemon = True
        listen_thread.start()

        input_thread: threading.Thread = threading.Thread(target=self.handle_input)
        input_thread.start()

        while True:
            conn, addr = self.server.accept()
            print(f"Connection from {addr}")
            peer_thread: threading.Thread = threading.Thread(target=self.handle_peer, args=(conn, addr))
            peer_thread.start()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lanmsg.py <username>")
        sys.exit(1)

    username: str = sys.argv[1]
    peer: Peer = Peer(username)
    peer.run()
