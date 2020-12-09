# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 13:28:58 2018

@author: Anne
"""

import messengerstuff
dsp = messengerstuff.dsp
import time
import calendar
import datetime

def loadChat(s):
    c = s.request(dsp.Requests.CompleteSync, None)
    return c.data

def analize_Write_Time(s):
    c = loadChat(s)
    c.events.sort()
    user = []
    
    for e in c.events:
        if type(e) == messengerstuff.Post:  # is post
            # find user in list
            i = 0
            for l in user:
                if l[0] == e.user:
                    i = user.index(l)
                    break
            else:
                # add user
                user.append((e.user, []))
                i = len(user)-1
            
            # add post to users list
            user[i][1].append(e)
    
    # get time spans of each user
    analie = []
    for l in user:
        u = l[0]
        ps = l[1]
        times = []
        
        for i, p in enumerate(ps):
            if i +1 < len(ps):
                t = p.time
                t2 = ps[i+1].time
                
                t_z = calendar.timegm(t)
                t2_z = calendar.timegm(t2)
                
                diff = t2_z - t_z
                
                times.append(diff)
        
        le = len(times)
        s = sum(times)
        if le == 0:
            continue
        average = s / le
        analie.append((u, average))
    return analie

def analize_Posts(s):
    c = loadChat(s)
    c.events.sort()
    user = []
    
    for e in c.events:
        if type(e) == messengerstuff.Post:  # is post
            # find user in list
            i = 0
            for l in user:
                if l[0] == e.user:
                    i = user.index(l)
                    break
            else:
                # add user
                user.append([e.user, 1])
                i = len(user)-1
            
            # add post to users list
            user[i][1] += 1
    return user

def analize_User(s):
    c = loadChat(s)
    user = set()
    
    for e in c.events:
        user.add(e.user)
    
    return user

def time_to_str(t):
    return time.strftime("%a, %d %b %Y %H:%M:%S", t)
            

ip = '192.168.178.32'
port = 50001
s = dsp.DSPSocket()
with s:
    s.connect((ip, port))
    s.request(dsp.Requests.Login, '(BOT)')
    l = analize_Posts(s)
    us = analize_User(s)

for u in us:
    print(u)

print()    
for u in l:
    print(u[0], u[1])

                
                    
            
