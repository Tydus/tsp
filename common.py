# -*- coding: utf-8 -*-

################################################################################
#                 Graduation Design Subject Double-Choose System               #
#                               Background Components                          #
#                                                                              #
#   Author: Tydus Ken <Tydus@Tydus.org>                                        #
#   Written: June. 2012                                                        #
#                                                                              #
################################################################################

from tornado.web import RequestHandler
from bson import ObjectId
from hashlib import sha1
from time import time

# Session Storage
TTL=15*60 # 15min
class SessionStorage():

    randomSession=lambda: sha1(str(ObjectId())).digest()
    ss=lambda: self.__dict__['__sessions']

    def __init__(self):
        self.__sessions={}

    def __getattr__(self,key):
        if key==None:
            return None
        # Get User by Session, and update TTL
        if ss().has_key(key):
            if ss()[key]['ttl']>=time():
                ss()[key]['ttl']=time()+TTL
                return ss[key]['user']
            else:
                del ss()[key]
                return None
        else:
            return None

    def createSession(self,user):
        # Create a new Session
        s=randomSession()
        ss()[s]={'user':user,'ttl':time()+TTL}
        return s

    def deleteSession(self,session):
        if ss().has_key(session):
            del ss[session]

sessions=SessionStorage()

# Request Handler
leafHandlers=[]

def leafHandler(path):
    def _deco(cls):
        leafHandlers.append((path,cls))
        return cls
    return _deco

class JsonRequestHandler(RequestHandler):
    def get_current_user(self):
        u=sessions[self.get_secure_cookie('session')]['user']
        u.reload()
        return u

