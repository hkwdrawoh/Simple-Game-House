#!/usr/bin/python3

import socket
import os
import sys
import threading
from datetime import datetime
from time import sleep
from random import choice

# Thread for each user
class GameThread(threading.Thread):

    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        print(f"{timenow()} Info:  New thread opened for {str(addr)}")
    
    def run(self):
        
        # /login authenticate user
        login_suc = False
        ingroup = -1
        while not login_suc:
            
            # receive message from client
            loginmsg = ""
            try:
                loginmsg = self.conn.recv(1024)
            except socket.error as err:
                print(f"{timenow()} Error: (Recv msg, {str(self.addr)}) {err}") 
                print(f"{timenow()} Warn:  Thread closed due to unexpected disconnection")
                return
            
            # authentication process
            try:
                if loginmsg:
                    loginmsg = loginmsg.decode()
                    msgcode, username, password = loginmsg.split(" ")
                
                if msgcode == "/login":
                    if username in userInfo and userInfo[username] == password:
                        sendmsg = "1001 Authentication successful"
                        print(f"{timenow()} Info:  {str(self.addr)} login successful as {username}")
                        login_suc = True
                    else:
                        sendmsg = "1002 Authentication failed"
                        print(f"{timenow()} Info:  {str(self.addr)} login failed")
                else:
                    raise Exception()
            except:
                sendmsg = "4002 Unrecognized message"
            
            # output result to client
            try:
                self.conn.send(sendmsg.encode("ascii"))
                print(f"{timenow()} Info:  {str(self.addr)} message sent: {sendmsg}")
            except socket.error as err:
                print(f"{timenow()} Error: (Send msg, {str(self.addr)}) {err}")
                print(f"{timenow()} Warn:  Thread closed due to unexpected disconnection")
                return
        
        # in game hall
        while True:

            # receive message from client
            clientmsg = ""
            sendmsg = ""
            try:
                clientmsg = self.conn.recv(1024)
            except socket.error as err:
                print(f"{timenow()} Error: (Recv msg, {username}) {err}") 
                if ingroup != -1:
                    print(f"{timenow()} Info:  Ending game with input -1")
                    result = rooms[ingroup-1].submitguess(username, -1)
                    rooms[ingroup-1].purgeroom()
                print(f"{timenow()} Warn:  Thread closed due to unexpected disconnection")
                return
            
            # decode message from client
            try:
                if clientmsg:
                    clientmsg = clientmsg.decode()
                    msgcode = clientmsg.split(" ")[0]
                
                # /list
                if clientmsg == "/list" and ingroup == -1:
                    sendmsg = f"3001 {roomcount}"
                    for i in rooms:
                        sendmsg += f" {str(i.count())}"
                
                # /enter
                elif msgcode == "/enter":
                    if ingroup == -1:
                        grpnum = int(clientmsg.split(" ")[1])
                        grpin = rooms[grpnum-1].adduser(username)
                        if grpin == 1:
                            ingroup = grpnum
                            sendmsg = f"3011 Wait"
                        elif grpin == 2:
                            ingroup = grpnum
                            sendmsg = f"3012 Game started. Please guess true or false"
                        else:
                            sendmsg = f"3013 The room is full"
                    else:
                        raise Exception()
                
                # /guess
                elif msgcode == "/guess":
                    result = -1
                    msgdes = clientmsg.split(" ")[1]
                    if ingroup != -1:
                        if msgdes == "true" or msgdes == "false":
                            result = rooms[ingroup-1].submitguess(username, msgdes)
                    if result == 1:
                        sendmsg = f"3021 You are the winner"
                    elif result == 2:
                        sendmsg = f"3022 You lost this game"
                    elif result == 3:
                        sendmsg = f"3023 The result is a tie"
                    else:
                        raise Exception()
                    ingroup = -1
                    rooms[grpnum-1].purgeroom()
                
                # /exit
                elif clientmsg == "/exit":
                    print(f"{timenow()} Info:  {username} request for disconnection.")
                    sendmsg = "4001 Bye bye"
                
                # wrong format
                else:
                    raise Exception()

            except:
                sendmsg = "4002 Unrecognized message"
                
            # send result to client
            try:
                self.conn.send(sendmsg.encode("ascii"))
                print(f"{timenow()} Info:  {username} message sent: {sendmsg}")

                # handling with exit and enter room
                if sendmsg == "4001 Bye bye":
                    break
                elif sendmsg == "3011 Wait":
                    rooms[grpnum-1].waitfull(username)
                    sendmsg = "3012 Game started. Please guess true or false"
                    self.conn.send(sendmsg.encode("ascii"))
                    print(f"{timenow()} Info:  {username} message sent: {sendmsg}")
                elif sendmsg == "3012 Game started. Please guess true or false":
                    rooms[grpnum-1].startgame(username)

            except socket.error as err:
                print(f"{timenow()} Error: (Send msg, {username}) {err}")
                if ingroup != -1:
                    print(f"{timenow()} Info:  Ending game with input -1")
                    result = rooms[ingroup-1].submitguess(username, -1)
                    rooms[ingroup-1].purgeroom()
                print(f"{timenow()} Warn:  Thread closed due to unexpected disconnection")
                return
        
        # /exit disconnect client
        self.conn.close()
        print(f"{timenow()} Info:  {username} disconnected successfully, thread closed")
        return

# Game room class
class GameRoom():
    def __init__(self, rmnum):
        self.rmnum = str(rmnum)
        self.startpurge = False
        self.lock = threading.Lock()
        self.condition = threading.Condition()
        self.participant = []
        self.guess = [None, None]
        self.ans = choice(["true", "false"])
    
    def count(self):
        # return num of user in room
        return len(self.participant)
    
    def adduser(self, username):
        # wait for lock release
        if self.lock.locked():
            print(f"{timenow()} Info:  {username} awaiting Room {self.rmnum} lock release...")
        while self.lock.locked():
            sleep(0.1)
        # lock room and check availability
        print(f"{timenow()} Info:  Room {self.rmnum} locked by {username}")
        self.lock.acquire()
        if self.count() < 2:
            self.participant.append(username)
            output = self.count()
        else:
            output = -1
        sleep(2)
        # release room and return num of user in room
        print(f"{timenow()} Info:  Room {self.rmnum} released")
        self.lock.release()
        return output
    
    def waitfull(self, username):
        # listen to condition and wait
        with self.condition:
            print(f"{timenow()} Info:  {username} awaiting Room {self.rmnum} full...")
            self.condition.wait()
            print(f"{timenow()} Info:  Room {self.rmnum} match found! Player: {username}")
    
    def startgame(self, username):
        # broadcast full and start game
        with self.condition:
            self.condition.notifyAll()
            print(f"{timenow()} Info:  Room {self.rmnum} match found! Player: {username}")
    
    def submitguess(self, username, guess):
        print(f"{timenow()} Info:  {username} submitted guess {guess} to Room {self.rmnum}")
        # wait for lock release
        if self.lock.locked():
            print(f"{timenow()} Info:  {username} awaiting Room {self.rmnum} lock release...")
        while self.lock.locked():
            sleep(0.1)
        # lock room and input user guess
        print(f"{timenow()} Info:  Room {self.rmnum} locked by {username}")
        self.lock.acquire()
        self.guess[self.participant.index(username)] = guess
        sleep(2)
        # release room and wait for opponent
        self.lock.release()
        with self.condition:
            if None in self.guess:
                print(f"{timenow()} Info:  Room {self.rmnum} released, waiting second input")
                self.condition.wait()
            else:
                print(f"{timenow()} Info:  Room {self.rmnum} released")
                print(f"{timenow()} Info:  Room {self.rmnum} {self.participant[0]}: {self.guess[0]}, {self.participant[1]}: {self.guess[1]}, Computer: {self.ans}")
                self.condition.notifyAll()
        #retrieve result
        if self.guess[0] == self.guess[1]:
            return 3
        elif guess == self.ans or -1 in self.guess:
            return 1
        else:
            return 2

    def purgeroom(self):
        #reset room
        with self.condition:
            if self.startpurge:
                self.condition.notifyAll()
                return
            else:
                self.startpurge = True
                print(f"{timenow()} Info:  Room {self.rmnum} waiting for purge")
                self.condition.wait()
        while self.lock.locked():
            sleep(0.1)
        # lock the room and purge everyone, everything. muahahaha...
        self.lock.acquire()
        self.startpurge = False
        self.participant = []
        self.guess = [None, None]
        self.ans = choice(["true", "false"])
        self.lock.release()
        print(f"{timenow()} Info:  Room {self.rmnum} purge successfully")
            

# generate server timestamp
def timenow():
    return datetime.now().strftime("%H:%M:%S")            


# main
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"{timenow()} Error: Wrong usage!")
        print(f"{timenow()} Usage: python3 GameServer.py <Server_port> <Path_to_UserInfo.txt>")
        sys.exit(1)
    
	# open UserInfo.txt file from argv
    try:
        global userInfo
        userInfo = {}
        fd = open(sys.argv[2], "r")
        for line in fd.readlines():
            username, password = line.split(":")
            password = password.replace("\n", "")
            userInfo[username] = password
        fd.close()
    except os.error as emsg:
        print(f"{timenow()} Error: (UserInfo.txt) {emsg}")
        sys.exit(1)
    
    # create game rooms
    global roomcount, rooms
    roomcount = 11
    rooms = [GameRoom(i+1) for i in range(roomcount)]

    # create socket and bind
    serverPort = int(sys.argv[1])
    try:
        sockfd = socket.socket()
        sockfd.bind(("", serverPort))
    except socket.error as emsg:
        print(f"{timenow()} Error: (Server socket) {emsg}")
        sys.exit(1)

    # listen to new connections
    print(f"{timenow()} Info:  Game server is up")
    threads = []
    sockfd.listen(5)   

    while True:
        # accept new connection, open new thread
        conn, addr = sockfd.accept()
        print(f"{timenow()} Info:  New client connected. Client: {str(addr)}")
        newthread = GameThread(conn, addr)
        newthread.start()
        threads.append(newthread)