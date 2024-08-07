# LanMsg

LanMsg is a peer-to-peer (P2P) chat application that allows users to communicate within a local network (LAN) without
the need for a central server. The application supports channels, private messaging, and automatic peer discovery using
UDP broadcasting.

## Features

- **Channels**: Users can join and create channels.
- **Private Messaging**: Users can send private messages to each other.
- **Broadcast Messaging**: Messages can be sent to all users within a channel.
- **User Management**: Users can join and leave the chat.
- **Automatic Peer Discovery**: Peers are automatically discovered within the LAN using UDP broadcasting.

## Requirements

- Python 3.x

## Installation

1. Clone the repository or download the `lanmsg.py` script.

```bash
git clone https://github.com/aedrax/lanmsg.git
cd lanmsg
```

2. Ensure you have Python 3 installed on your system.

## Usage

1. **Run the Script**:
   - Start the script on multiple machines within the same LAN.
   - Use the following command, replacing `<username>` with your desired username:

```bash
python lanmsg.py <username>
```

2. **Automatic Discovery**:
   - The peers will automatically discover each other and connect without specifying IP addresses.

3. **Messaging**:
   - Use `/msg <username> <message>` for private messaging.
   - Type messages normally to broadcast within a channel.

## Commands

- **/msg <username> <message>**: Send a private message to a specific user.
- **Normal text**: Sends a message to the current channel.

## Example

```bash
$ python lanmsg.py Alice
Alice's LanMsg chat server started...
Connected to Bob's chat. Please enter your username: Alice
Enter the channel you want to join: general
Joined channel general. You can now start chatting.

Alice@general: Hello everyone!
/msg Bob Hi Bob, how are you?
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

If you would like to contribute to the project, please fork the repository and submit a pull request.

## Authors

- [Paul Sorensen](https://github.com/aedrax)
