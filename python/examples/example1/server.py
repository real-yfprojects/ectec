# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 17:50:45 2020

@author: Simon
"""

import _thread
import socket
import time

HOST = '127.0.0.1'
PORT = 65432


def on_new_client(clientsocket, addr):
    with clientsocket:
        print('Connected by', addr)
        while True:
            time.sleep(0.1)
            data = conn.recv(1024)
            print(str(data))


while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print('Waiting for connections')
        conn, addr = s.accept()
        _thread.start_new_thread(on_new_client, (conn, addr))
        time.sleep(0.1)
