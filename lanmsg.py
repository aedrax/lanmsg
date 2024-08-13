import asyncio
import socket
import sys
import time

BROADCAST_PORT: int = 12345  # Fixed broadcast port for UDP
BROADCAST_INTERVAL: int = 5  # seconds
PEER_TIMEOUT: int = 15  # seconds

class Peer:
    def __init__(self, username: str, host: str = '0.0.0.0') -> None:
        self.username: str = username
        self.peers: dict[str, float] = {}
        self.joined_channels: list[str] = []  # Channels this user has joined
        self.current_channel: str = ''

        # Setup UDP socket for broadcasting and receiving
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind((host, BROADCAST_PORT))
        self.local_address = self.sock.getsockname()

    async def broadcast_presence(self) -> None:
        """
        Broadcasts the presence of the peer to all other peers in the network.
        """
        while True:
            message: str = f"JOIN::{self.username}"
            self.sock.sendto(message.encode(), ('<broadcast>', BROADCAST_PORT))
            await asyncio.sleep(BROADCAST_INTERVAL)

    async def listen_for_peers(self) -> None:
        """
        Listens for incoming broadcast messages from other peers in the network.
        """
        loop = asyncio.get_event_loop()
        while True:
            current_time = time.time()
            # Check for peers that have timed out
            self.check_for_timeouts(current_time)

            data, addr = await loop.run_in_executor(None, self.sock.recvfrom, 1024)
            message: str = data.decode()

            if message.startswith("JOIN::"):
                username = message.split("::")[1]
                if username not in self.peers:
                    print(f"{username} has joined from {addr}")
                self.peers[username] = current_time
                continue
            
            # Extract channel from message format "username@channel: message"
            if "@" in message and ":" in message:
                sender, _ = message.split(": ", 1)
                user, channel = sender.split("@")
                if channel in self.joined_channels and user != self.username:
                    print(message)

    def check_for_timeouts(self, current_time: float) -> None:
        """
        Checks for peers that have timed out and removes them.
        """
        to_remove = []
        for username, last_seen in self.peers.items():
            if current_time - last_seen > PEER_TIMEOUT:
                to_remove.append(username)
                print(f"{username} has left.")

        for addr in to_remove:
            del self.peers[addr]

    async def broadcast(self, message: str, channel: str) -> None:
        """
        Broadcasts the message to all peers in the given channel.
        """
        message_to_send = f"{self.username}@{channel}: {message}"
        self.sock.sendto(message_to_send.encode(), ('<broadcast>', BROADCAST_PORT))

    async def handle_input(self) -> None:
        """
        Handles the input from the user.
        """
        loop = asyncio.get_event_loop()
        while True:            
            command: str = await loop.run_in_executor(None, input)            
            if command.startswith("/join"):
                _, channel = command.split(" ", 1)
                self.current_channel = channel
                if channel not in self.joined_channels:
                    self.joined_channels.append(channel)
                print(f"Joined channel {channel}.")
            elif command.startswith("/part"):
                if self.current_channel:
                    print(f"Left channel {self.current_channel}.")
                    self.joined_channels.remove(self.current_channel)
                    self.current_channel = ''
                else:
                    print("You are not in any channel.")
            elif command.startswith("/nick"):
                _, new_nickname = command.split(" ", 1)
                self.username = new_nickname
                print(f"Nickname changed to {self.username}.")
            elif command.startswith("/me"):
                _, action = command.split(" ", 1)
                if self.current_channel:
                    await self.broadcast(f"* {self.username} {action}", self.current_channel)
                else:
                    print("Please join or create a channel using the /join <channel_name> command.")
            elif command.startswith("/topic"):
                _, topic = command.split(" ", 1)
                if self.current_channel:
                    await self.broadcast(f"Topic for {self.current_channel}: {topic}", self.current_channel)
                else:
                    print("Please join or create a channel using the /join <channel_name> command.")
            elif command.startswith("/quit"):
                print("Quitting...")
                sys.exit(0)
            elif command.startswith("/help"):
                self.print_help()
            else:
                if self.current_channel:
                    await self.broadcast(command, self.current_channel)
                else:
                    print("Please join or create a channel using the /join <channel_name> command.")

    def print_help(self) -> None:
        """
        Prints the help message with available commands.
        """
        help_message = """
Available commands:
/join <channel>       - Join or create a channel
/part                 - Leave the current channel
/nick <newnickname>   - Change your nickname
/me <action>          - Send an action message to the current channel
/topic <topic>        - Set the topic for the current channel
/quit                 - Quit the chat
/help                 - Show this help message
"""
        print(help_message)

    async def run(self) -> None:
        """
        Starts the peer.
        """
        print(f"{self.username}'s LanMsg peer started...")

        await asyncio.gather(
            self.broadcast_presence(),
            self.listen_for_peers(),
            self.handle_input()
        )

def main():
    """
    Main function for the program.
    """
    if len(sys.argv) != 2:
        print("Usage: python lanmsg.py <username>")
        sys.exit(1)

    username: str = sys.argv[1]
    peer: Peer = Peer(username)
    asyncio.run(peer.run())

if __name__ == "__main__":
    main()
