import socket
import threading
import sys
from typing import Dict, List, Tuple
import random

DEFAULT_CHAT_PORT: int = 12346  # Default chat port
BROADCAST_INTERVAL: int = 5  # seconds

class Peer:
    def __init__(self, username: str, chat_port: int = DEFAULT_CHAT_PORT, host: str = '0.0.0.0') -> None:
        self.server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, chat_port))
        self.server.listen()
        self.username: str = username
        self.chat_port: int = chat_port
        self.peers: Dict[socket.socket, str] = {}
        self.channels: Dict[str, List[socket.SOCKET]] = {}
        self.default_channel: str = ''

        # Setup UDP broadcast socket with a random port
        self.broadcast_port: int = random.randint(10000, 60000)
        self.broadcast_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcast_socket.settimeout(BROADCAST_INTERVAL)
        self.broadcast_socket.bind((host, self.broadcast_port))

    def broadcast_presence(self) -> None:
        """
        Broadcasts the presence of the chat server to all peers in the network.
        """
        while True:
            message: str = f"{self.username}::{self.server.getsockname()[0]}::{self.chat_port}"
            self.broadcast_socket.sendto(message.encode(), ('<broadcast>', self.broadcast_port))
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
                username, peer_ip, peer_port = message.split("::")
                if username != self.username and (peer_ip, int(peer_port)) not in self.peers:
                    self.connect_to_peer(peer_ip, int(peer_port))
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
        if not self.default_channel:
            self.default_channel = channel
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
            elif command.startswith("/join"):
                _, channel = command.split(" ", 1)
                if channel not in self.channels:
                    self.channels[channel] = []
                self.default_channel = channel
                print(f"Joined channel {channel}.")
            elif command.startswith("/part"):
                if self.default_channel:
                    print(f"Left channel {self.default_channel}.")
                    self.default_channel = ''
                else:
                    print("You are not in any channel.")
            elif command.startswith("/nick"):
                _, new_nickname = command.split(" ", 1)
                self.username = new_nickname
                print(f"Nickname changed to {self.username}.")
            elif command.startswith("/me"):
                _, action = command.split(" ", 1)
                if self.default_channel:
                    self.broadcast(f"* {self.username} {action}", self.default_channel)
                else:
                    print("Please join or create a channel using the /join <channel_name> command.")
            elif command.startswith("/topic"):
                _, topic = command.split(" ", 1)
                if self.default_channel:
                    self.broadcast(f"Topic for {self.default_channel}: {topic}", self.default_channel)
                else:
                    print("Please join or create a channel using the /join <channel_name> command.")
            elif command.startswith("/quit"):
                message = " ".join(command.split(" ")[1:])
                print(f"Quitting: {message}")
                sys.exit(0)
            elif command.startswith("/invite"):
                _, nickname, channel = command.split(" ", 2)
                for peer, name in self.peers.items():
                    if name == nickname:
                        peer.send(f"Invitation to join channel {channel} from {self.username}\n".encode())
                        break
            elif command.startswith("/kick"):
                _, channel, nickname = command.split(" ", 2)
                for peer, name in self.peers.items():
                    if name == nickname:
                        peer.send(f"You have been kicked from channel {channel}\n".encode())
                        self.channels[channel].remove(peer)
                        break
            else:
                if self.default_channel:
                    self.broadcast(f"{self.username}@{self.default_channel}: {command}", self.default_channel)
                else:
                    print("Please join or create a channel using the /join <channel_name> command.")

    def connect_to_peer(self, peer_ip: str, peer_port: int) -> None:
        """
        Connects to a peer.
        peer_ip: str - The IP address of the peer.
        peer_port: int - The port number of the peer.
        """
        peer_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((peer_ip, peer_port))
        self.peers[peer_socket] = None
        peer_handler: threading.Thread = threading.Thread(target=self.handle_peer, args=(peer_socket, (peer_ip, peer_port)))
        peer_handler.start()

    def run(self) -> None:
        """
        Starts the chat server.
        """
        print(f"{self.username}'s LanMsg chat server started on port {self.chat_port}...")

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
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python lanmsg.py <username> [port]")
        sys.exit(1)

    username: str = sys.argv[1]
    chat_port: int = int(sys.argv[2]) if len(sys.argv) == 3 else DEFAULT_CHAT_PORT
    peer: Peer = Peer(username, chat_port)
    peer.run()
