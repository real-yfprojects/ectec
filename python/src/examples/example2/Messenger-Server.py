#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 18:17:02 2018

@author: Yannick Funke
"""

import messengerstuff
import socketserver
import threading

port = 40000

try:
    s = socketserver.ThreadingTCPServer(('', port), messengerstuff.ChatClient)
    t = threading.Thread(target=s.serve_forever)
    t.start()
    input()
except Exception as e:
    print(e)
finally:
    s.shutdown()
    print('Shutdown')
    s.server_close()
