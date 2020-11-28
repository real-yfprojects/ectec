#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 18:20:09 2018

@author: Yannick Funke
"""

import messengerstuff
import tkinter as tk
import tkinter.messagebox as tkm
import time
dsp = messengerstuff.dsp

ip = '127.0.0.1'
port = 40000


class Messenger:
    
    def __init__(self, id, port):
        self.window = tk.Tk()
                
        self.text = tk.Text(self.window, state='disabled')
        self.text.pack()
           
        self.wr = tk.Frame(self.window)
        self.b = tk.Button(self.wr, text='Send', command=self.send)
        self.e = tk.Entry(self.wr)
        self.e.pack(side='left')
        self.b.pack()
        self.wr.pack()
        
        self.c = dsp.DSPSocket()
        with self.c:
            self.c.connect((id, port))
            self.load()
            self.mil = 2000
            
            self.window.after(self.mil, self.update)
            self.window.mainloop()
        
        
    def update(self):
        p = self.c.request(dsp.Requests.NormalSync, self.last)
        d = p.data
        d.sort()
        if d:
            self.last = d[len(d)-1]
        
        self.text.config(state='normal')
        for e in d:
            self.text.insert('end', str(e) + '\n\n')
        self.text.config(state='disabled')
        
        self.window.after(self.mil, self.update)
        print('Updated')
        
        self.text.see('end')
        
    def send(self):
        mes = self.e.get()
        self.c.request(dsp.Requests.Log, mes)
        self.e.delete(0, 'end')
        print('Send')
    
    def load(self):
        # ask name
        name = type('Name', (), {'name':'Unknown'})
        def ok(name):
            t = e.get()
            if t:
                name.name = t
            w.quit()
            w.destroy()
            
        w = tk.Toplevel(self.window)
        w.title('Enter Username')
        w.transient(self.window)
        
        e = tk.Entry(w)
        e.pack()
        b = tk.Button(w, text='OK', command=lambda: ok(name))
        b.pack()
        
        w.mainloop()
        
        # login
        self.c.request(dsp.Requests.Login, name.name)
        print('Loged in')
        
        # get Chat and show
        p = self.c.request(dsp.Requests.CompleteSync, None)
        chat = p.data.events
        chat.sort()
        self.last = chat[len(chat)-1]
        
        self.text.config(state='normal')
        for e in chat:
            self.text.insert('end', str(e) + '\n\n')
        self.text.config(state='disabled')
        print('Loaded Chat')
        
        self.text.see('end')
        
        
if __name__ == '__main__':
    m = Messenger(ip, port)
