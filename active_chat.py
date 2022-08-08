from emoji import demojize
from sortedcontainers import SortedList
import keyboard
import socket
import datetime
import time
import os
import sys

WAIT_TIME_IN_MINS = 5 #how many mins till they disappear from active chatter list
ACCESS_TOKEN = '' #replace this

ACCESS_TOKEN
server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'ActiveChatWatcher'
token = 'oauth:'+ACCESS_TOKEN
channel = '#CHANNEL_NAME'

allChatters=SortedList()
activeChatterDict={
    "fakeName" : 0
}
currentOldestPoster="fakeName"

sock = socket.socket()
sock.connect((server, port))

sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
sock.send(f"JOIN {channel}\n".encode('utf-8'))

isOnActiveChat=True
pausePrintChat=False

def toggleActiceChat():
    global isOnActiveChat
    isOnActiveChat=not isOnActiveChat
    
    os.system('clear')
    if isOnActiveChat:
        print("Active Chatters: ")
        print("=====================================")
        for a in activeChatterList:
            print(a)
    else:
        print("All Chatters: ")
        print("=====================================")
        for a in allChatters:
            print(a)
    
def togglePauseChat():
    global pausePrintChat
    pausePrintChat=not pausePrintChat

keyboard.add_hotkey("space", lambda: toggleActiceChat())
keyboard.add_hotkey("p", lambda: togglePauseChat())



while sock.recv(2048).decode('utf-8').find("End of /NAMES") == -1:
    eatingWelcome=0

# PRIVMSG

while True:
    resp = sock.recv(2048).decode('utf-8')
        
    if resp.startswith('PING'):
        sock.send("PONG\n".encode('utf-8'))
        
    elif len(resp) > 0 and resp.find("PRIVMSG") != -1:
        #print(resp)
        username = demojize(resp)[1:].split('!')[0]
        if username not in allChatters:
            allChatters.add(username)
        activeChatterDict[username] = int(time.time())
        if username==currentOldestPoster:
            oldestPostNumber = int(time.time())+1000 
            for name in activeChatterDict:
                if activeChatterDict[name] < oldestPostNumber:
                    currentOldestPoster=name
                    oldestPostNumber=activeChatterDict[name]
    while activeChatterDict[currentOldestPoster] <= int(time.time()) - WAIT_TIME_IN_MINS*60:
        activeChatterDict.pop(currentOldestPoster)
        oldestPostNumber = int(time.time())+1000 
        for name in activeChatterDict:
            if activeChatterDict[name] < oldestPostNumber:
                currentOldestPoster=name
                oldestPostNumber=activeChatterDict[name]
    if not pausePrintChat:
        if isOnActiveChat:
            activeChatterList = [*activeChatterDict]
            activeChatterList.sort()
            os.system('cls')
            print("Active Chatters: ")
            print("=====================================")
            for a in activeChatterList:
                print(a)
        else:
            os.system('cls')
            print("All Chatters: ")
            print("=====================================")
            for a in allChatters:
                print(a)
