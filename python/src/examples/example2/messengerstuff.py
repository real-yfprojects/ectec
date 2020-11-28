# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 06:56:07 2018

@author: Yannick
"""
import time
import calendar
import dsp
import threading

# Messenger-Dienst Zubehör

class Event:
    
    def __init__(self, time):
        self.time = time
        
    def __gt__(self, other):
        return self.time > other.time
    
    def __lt__(self, other):
        return other > self
    
    def __eq__(self, other):
        return self.time == other.time
    
    def str_time(self):
        epoch = calendar.timegm(self.time)
        local = time.localtime(epoch)
        string = time.strftime("%a, %d %b %Y %H:%M:%S", local)
        return string
    
    def __str__(self):
        return ""

class Post(Event):
    
    def __init__(self, user, time, text):
        super().__init__(time)
        self.user = user
        self.text = text
    
    def __str__(self):
        time = self.str_time()
        user = str(self.user)
        headline = time + '     ' + user
        return headline + '\n' + self.text
    
    def __eq__(self, other):
        return super().__eq__(other) and self.user == other.user \
                                     and self.text == other.text
        
        
        
class ConnectEvent(Event):
    
    def __init__(self, time, user, connect):
        super().__init__(time)
        self.user = user
        self.con = connect
        
    def __str__(self):
        if self.con:
            return self.str_time() + '     ' + str(self.user) + ' went online.'
        else:
            return self.str_time() + '     ' + str(self.user) + ' went offline.'
        
    def __repr__(self):
        return str(self)
        
    def __eq__(self, other):
        return super().__eq__(other) and self.user == other.user and self.con == other.con
        

class User:
    
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
        

class Chat:
    
    def __init__(self):
        self.events = []
        self.user = []
    
    def post(self, post):
        self.events.append(post)
    
    def connect(self, user, dis, time):
        if dis:
            del self.user[self.user.index(user)]
            self.events.append(ConnectEvent(time, user, False))
        else:
            self.user.append(user)
            self.events.append(ConnectEvent(time, user, True))
    
    def getSince(self, event):
        self.events.sort()
        i = self.events.index(event)
        return self.events[i+1:]
            

class ChatClient(dsp.ClientConnection):
    chat = Chat()
    lock = threading.Lock()
    
    def login(self, data):
        u = User(data)
        with self.lock:
            self.chat.connect(u, False, time.gmtime())
        return u
    
    def getallData(self, user):
        return self.chat
    
    def getData(self, time, user):
        with self.lock:
            d = self.chat.getSince(time)
        return d
    
    def newData(self, user, data):
        p = Post(user, time.gmtime(), data)
        with self.lock:
            self.chat.post(p)
        return True
    
    def disconnect(self, user):
        with self.lock:
            self.chat.connect(user, True, time.gmtime())
        
        
    
    
