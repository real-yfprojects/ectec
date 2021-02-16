# -*- coding: utf-8 -*-
"""
DSP - Data Server Protocol
Created on Sun Oct 14 16:55:56 2018

@author: Yannick Funke
"""
import socketserver
import socket
import pickle
import enum



class Requests(enum.Enum):
    Login = 1
    CompleteSync = 2
    NormalSync = 3
    Log = 4
    LongStart = 5
    Long = 6
    LongEnd = 7
    Disconnect = 8
    

class Answers(enum.Enum):
    Error = 1
    Successful = 2
    Data = 3
    
    
class Package:
    
    def __init__(self, requesttype, data):
        self.request = requesttype
        self.data = data
        
    def to_bytes(self):
        return pickle.dumps(self)
    
def load(bytes):
    """load Package/... from bytes"""
    return pickle.loads(bytes)



class DSPError(Exception):
    pass

class UnkownDSPRequest(DSPError):
    pass

class DSPLongError(DSPError):
    pass

class DSPLoginError(DSPError):
    pass

class ClientConnection(socketserver.BaseRequestHandler):
    """Should be subclassed
    database , ... ; so variables for the hole server, as classvariable"""
    
    def __init__(self, request, client_address, server):
        print('Init')
        self.user = None
        self.longtype = None
        self.longparts = None
        super().__init__(request, client_address, server)
        
    def handle(self):
        # Connection accepted
        # waiting for requests
        
        ip = self.client_address
        print('Connected to [{}]'.format(ip))
        while True:
            br = self.request.recv(1024)
            if br == b'':
                r = Package(Requests.Disconnect, None)
            else:
                r = pickle.loads(br)
            print(r.request, self.user)
            
            # Progress Request
            if self.longtype != None:  # Long
                if r.request == Requests.Long:
                    self.longparts.append(r.data)
                    self.sendOK()
                    continue
                elif r.request == Requests.LongEnd:
                    # put all together
                    data = b''
                    for p in self.longparts:
                        data += p
                    
                    r = Package(self.longtype, load(data))
                    
                    self.longttype = None
                    self.longparts = None
                else:
                    self.sendError(DSPLongError("Can't request {} while Long".format(r.request)))
                    continue
               
            if r.request == Requests.Login:
                an = self.login(r.data)
                if issubclass(type(an), DSPError):
                    self.sendError(an)
                else:
                    self.user = an
                self.sendOK()
            elif r.request == Requests.CompleteSync:
                an = self.getallData(self.user)
                if issubclass(type(an), DSPError):
                    self.sendError(an)
                else:
                    self.sendData(an)                    
            elif r.request == Requests.NormalSync:
                an = self.getData(r.data, self.user)
                if issubclass(type(an), DSPError):
                    self.sendError(an)
                else:
                    self.sendData(an)
            elif r.request == Requests.Log:
                an = self.newData(self.user, r.data)
                if issubclass(type(an), DSPError):
                    self.sendError(an)
                else:
                    self.sendOK()
            elif r.request == Requests.LongStart:
                self.longtype = r.data
                self.longparts = []
            elif r.request == Requests.Disconnect:
                self.disconnect(self.user)
                self.sendOK()
                break
            else:
                an = self.handle_other_request(r, self.user)
                if issubclass(type(an), DSPError)                :
                    self.sendError(an)
                elif an == True:
                    self.sendOK()
                else:
                    self.sendData(an)
    
    def sendp(self, p):
        b = p.to_bytes()
        self.request.sendall(b)
        self.request.sendall(b'end')
                
    
    def sendError(self, error):
        p = Package(Answers.Error, error)
        #self.request.sendall(p.to_bytes())
        self.sendp(p)
    
    def sendOK(self):
        p = Package(Answers.Successful, None)
        self.sendp(p)
    
    def sendData(self, data):
        p = Package(Answers.Data, data)
        self.sendp(p)
            
    def getallData(self, user):
        """Should be overwritten
        
        return data   or
        return DSPError if unsuccesful"""
        pass
    
    
    def getData(self, key, user):
        """Should be overwritten
        
        return data   or
        return DSPError if unsuccesful"""
        pass
    
    def newData(self, user, data):
        """Should be overwritten
        
        return True if successful
        return DSPError if unsuccessful"""
        pass
    
    def login(self, requestdata):
        """Should be overwritten
        
        returns LoginError if login is unsuccessful
        returns login key if login is succesful"""
        return True
    
    def disconnect(self, user):
        """Should be overwritten"""
        pass
    
    def handle_other_request(self, package, user):
        """May be overwritten
        
        return True if successful
        return DSPError if unsuccessful
        return data if data is required"""
        return UnkownDSPRequest(str(package.request))
    
        
class  DSPSocket:
    
    def __init__(self):
        self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          
    def connect(self, address):
        self.c.connect(address)
    
    def sendRequest(self, package):
        b = package.to_bytes()
        self.c.sendall(b)
        
        fullan = b''
        an = b''
        while True:
            fullan += an
            an = self.c.recv(1024)
            if an.endswith(b'end'):
                an = an[:-3]
                fullan += an
                break
        return load(fullan)
    
    def request(self, type, data=None):
        p = Package(type, data)
        return self.sendRequest(p)
    
    def __enter__(self):
        pass
   
    def __exit__(self, *args):
        try:
            self.request(Requests.Disconnect, None)
        except:
            pass
        finally:
            self.c.close()
    
        
