from emoji import demojize
from sortedcontainers import SortedList
import keyboard
import socket
import datetime
import time
import os
import sys
import ctypes

def getWindow():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
    return (buff.value, hwnd) # buff.value is the title of the window, hwnd is the window handle
    
CURRENT_WINDOW_NAME = getWindow()

if CURRENT_WINDOW_NAME[0].find("Command")==CURRENT_WINDOW_NAME[0].find("cmd"):
    print("I think you switched programs too fast, you have to wait a little bit before switching windows")
    print("Hit space if you think this is an error")
    os.system('pause')
else:
    print("ready")
    
WAIT_TIME_IN_MINS = 5 #how many mins till they disappear from active chatter list
ACCESS_TOKEN = '' #replace this

server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'ActiveChatWatcher'
token = 'oauth:'+ACCESS_TOKEN
channel = '#CHANNEL_NAME'

allChatters=SortedList()
activeChatterDict={
    "fakeName" : 0
}
currentOldestPoster="fakeName" #there has to be a better way but I'm lazy

sock = socket.socket()
sock.connect((server, port))

sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
sock.send(f"JOIN {channel}\n".encode('utf-8'))

isOnActiveChat=True
pausePrintChat=False

def toggleActiceChat():
    global isOnActiveChat
    activeChatterList = [*activeChatterDict]
    if CURRENT_WINDOW_NAME == getWindow():
        isOnActiveChat=not isOnActiveChat
        
        os.system('cls')
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
    
    if CURRENT_WINDOW_NAME == getWindow():
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
