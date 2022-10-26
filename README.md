Implementation of a simple game house application using Python socket programming.

A game house is an application in which multiple clients connect to a game server, get authorized, and then select a game room to enter and play a game with another player in the same room.

This game house application consists of two parts: the server program and the client program.

Refer to `assignment1_handout_COMP3234_ELEC3443.pdf` for detailed game mechanics.



## Usage

Install python first.

Then `$ cd` to the folder containing `GameClient.py` and `GameServer.py`. 

### Server-side Program 

To start up the server, run the command:

    $ python3 GameServer.py <Server_port> <Path_to_UserInfo.txt>

`<Server_port>` is the server listening port defined by user.
`<Path_to_UserInfo.txt>` is the relative path to `UserInfo.txt`, which stores the user credentials.

### Client-side Program 

    $ python3 GameClient.py <Server_addr> <Server_port>

`<Server_addr>` is the IP address of the server.
`<Server_port>` is the server listening port defined previously.



## Client Example

An example of the client terminal of the GameClient.py:

    Please input your user name:
    user1
    Please input your password: 
    user11
    1001 Authentication successful
    /list
    3001 11 0 0 0 0 0 0 0 0 0 0 0
    /enter 7
    3011 Wait
    3012 Game started. Please guess true or false
    /true
    4002 Unrecognized message
    /guess true
    3021 You are the winner
    /exit
    4001 Bye bye
    Client ends

User inputs demonstrated: `user1`, `user11`, `/list`, `/enter 7`, `/true`, `/guess true`, and `/exit`

Refer to `assignment1_handout_COMP3234_ELEC3443.pdf` for detailed usage of user inputs.
## Server Example

An example of the server terminal of the GameServer.py:

    20:51:56 Info:  Game server is up
    20:52:02 Info:  New client connected. Client: ('127.0.0.1', 61571)
    20:52:02 Info:  New thread opened for ('127.0.0.1', 61571)
    20:52:07 Info:  ('127.0.0.1', 61571) login successful as user1
    20:52:07 Info:  ('127.0.0.1', 61571) message sent: 1001 Authentication successful      
    20:52:09 Info:  user1 message sent: 3001 11 0 0 0 0 0 0 0 0 0 0 0
    20:52:12 Info:  Room 7 locked by user1
    20:52:14 Info:  Room 7 released
    20:52:14 Info:  user1 message sent: 3011 Wait
    20:52:14 Info:  user1 awaiting Room 7 full...
    20:52:18 Info:  New client connected. Client: ('127.0.0.1', 61572)
    20:52:18 Info:  New thread opened for ('127.0.0.1', 61572)
    20:52:20 Info:  ('127.0.0.1', 61572) login successful as user2
    20:52:20 Info:  ('127.0.0.1', 61572) message sent: 1001 Authentication successful      
    20:52:23 Info:  Room 7 locked by user2
    20:52:25 Info:  Room 7 released
    20:52:25 Info:  user2 message sent: 3012 Game started. Please guess true or false      
    20:52:25 Info:  Room 7 match found! Player: user2
    20:52:25 Info:  Room 7 match found! Player: user1
    20:52:25 Info:  user1 message sent: 3012 Game started. Please guess true or false      
    20:52:28 Info:  user1 message sent: 4002 Unrecognized message
    20:52:31 Info:  user1 submitted guess true to Room 7
    20:52:31 Info:  Room 7 locked by user1
    20:52:34 Info:  Room 7 released, waiting second input
    20:52:35 Info:  user2 submitted guess false to Room 7
    20:52:35 Info:  Room 7 locked by user2
    20:52:37 Info:  Room 7 released
    20:52:37 Info:  Room 7 user1: true, user2: false, Computer: true
    20:52:37 Info:  Room 7 waiting for purge
    20:52:37 Info:  Room 7 purge successfully
    20:52:37 Info:  user1 message sent: 3021 You are the winner
    20:52:37 Info:  user2 message sent: 3022 You lost this game
    20:52:40 Info:  user1 request for disconnection.
    20:52:40 Info:  user1 message sent: 4001 Bye bye
    20:52:40 Info:  user1 disconnected successfully, thread closed
    
## Server Log Messages

Most actions performed in the server will return a log message to the terminal.

### Server start-up

After initialization, the server will print:

    Info:  Game server is up

Server only accepts exactly two arguements in run command, otherwise these messages will appear, and the server shutdowns:

    Error: Wrong usage!
    Usage: python3 GameServer.py <Server_port> <Path_to_UserInfo.txt>

If UserInfo.txt is corrupted or not found, this message will appear:

    Error: (UserInfo.txt) {Error_message}

If server socket is not created properly, this message will appear:

    Error: (Server socket) {Error_message}

### Client request for connection

When a new client connects to the server, a new server thread is created:

    Info:  New client connected. Client: {client_addr}
    Info:  New thread opened for {client_addr}

### Client authentication

Everytime the client tries to log in, a message will appear indicating the status of login:

    Info:  {client_addr} login successful as {username}

    Info:  {client_addr} login failed

### Communication with client

For every message sent to client, a log message will appear:

    Info:  {client_addr} message sent: {send_msg}
    
Any communication errors with the client will disconnect the client, and terminates corresponding thread, but not the server itself:

    Error: (Recv msg, {client_addr}) {Error_message}

    Error: (Send msg, {client_addr}) {Error_message}

    Warn:  Thread closed due to unexpected disconnection

However, if the message is sent successfully but wrong message command, communication will not be terminated. Instead, the server returns `4002 Unrecognized message` to client:

    Info:  {client_addr} message sent: 4002 Unrecognized message

>   `client_addr` is replaced with `username` if the client is logged in.


### Game House Thread Lock

To avoid thread interferences, thread locks are implemented for data protection.

When a client thread is waiting the lock to be released:

    Info:  {username} awaiting Room {room_num} lock release..."

When a client thread acquire the lock:

    Info:  Room {room_num} locked by {username}

When a room lock is released:

    Info:  Room {room_num} released

### Game Mechanics

The game starts when two players enter the same game room. A message will appear when first player enters the room and waiting for second player:

    Info:  {username} awaiting Room {room_num} full...

After second player enters, a match found message will appear twice, indicating individual player username:

    Info:  Room {room_num} match found! Player: {username}

Each player will submit a guess, once the server receives, a message will appear:

    Info:  {username} submitted guess {guess} to Room {room_num}

If the player disconnects during the game, an additional message will appear:

    Info:  Ending game with input -1

After both guesses are received, a summary will appear:

    Info:  Room {room_num} {username1}: {guess1}, {username2}: {guess2}, Computer: {answer}

As the result will be sent to the users, no additional message will appear apart from `Info: {client_addr} message sent: {send_msg}`

At the end of the game, the room will be initialized for next round:

    Info:  Room {room_num} waiting for purge"
    Info:  Room {room_num} purge successfully"

### Client request for disconnection

When the client requests for disconnection using `/exit` command, connection is terminated and the thread is closed:

    Info:  {username} disconnected successfully, thread closed

## Contribution

This appllication is solely created by hkwdrawoh.
