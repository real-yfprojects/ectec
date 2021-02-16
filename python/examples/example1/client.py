# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 17:52:55 2020

@author: nomis
"""

import socket


class Client:

    def __init__(self):
        pass

    def __str__(self):
        return f'Connected to: {self.server_ip},{self.sever_port}'

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self.server_ip},{self.sever_port})')

    def connectToServer(self, server_ip, server_port):
        '''
        Connects to the given server ip and port
        '''
        self.server_ip = server_ip
        self.server_port = server_port
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.server_ip, self.server_port))
        except:
            self.s.close()
            raise Exception('Error while opening socket')

    def send(self, message):
        '''
        Sends a message to all
        '''
        try:
            self.s.sendall(bytes(message, 'utf-8'))
        except:
            self.s.close()
            raise Exception('Error while opening socket')
