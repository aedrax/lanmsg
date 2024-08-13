# LanMsg

LanMsg is a peer-to-peer (P2P) chat application that allows users to communicate
within a local network (LAN) without the need for a central server. The 
application supports channels, nickname changes, action messages, topic setting,
and more. It is implemented using Python's `asyncio` library for asynchronous
operations.

## Features

- **Channels**: Users can join and create channels.
- **Nickname Changes**: Users can change their nickname.
- **Action Messages**: Users can send action messages to the current channel.
- **Topic Setting**: Users can set the topic for the current channel.
- **Automatic Peer Discovery**: Peers are automatically discovered within the LAN using UDP broadcasting.
- **Help Command**: Users can view a list of available commands and their descriptions.

## Requirements

- Python 3.6+

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

3. **Join a Channel**:
   - Use the `/join <channel_name>` command to join or create a channel.

4. **Use Commands**:
   - Use the available commands to interact with other users.

## Commands

- **/join <channel>**: Join or create a channel.
- **/part**: Leave the current channel.
- **/nick <newnickname>**: Change your nickname.
- **/me <action>**: Send an action message to the current channel.
- **/topic <topic>**: Set the topic for the current channel.
- **/quit**: Quit the chat.
- **/help**: Show the help message with available commands.

## Example

```bash
$ python lanmsg.py Alice
Alice's LanMsg peer started...
Alice@no_channel: /join general
Joined channel general.
Alice@general: Hello everyone!
Alice@general: /nick AliceNew
Nickname changed to AliceNew.
AliceNew@general: /me waves
* AliceNew waves
AliceNew@general: /topic Today's discussion
AliceNew@general: /part
Left channel general.
Alice@no_channel: /quit
Quitting...
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

If you would like to contribute to the project, please fork the repository and submit a pull request.

## Authors

- [Paul Sorensen](https://github.com/aedrax)


### Instructions:
1. **Run the Script**:
   - Start the script on multiple machines within the same LAN.
   - `python lanmsg.py <username>`

2. **Automatic Discovery**:
   - The peers will automatically discover each other and connect without specifying IP addresses.

3. **Join a Channel**:
   - Use the `/join <channel_name>` command to join or create a channel.

4. **Use Commands**:
   - Use the available commands to interact with other users.