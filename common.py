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

class Phase(object):
    def __init__(self):
        object.__init__(self)
        self.__doc=Settings.objects().first()

    def __str__(self):
        self.__doc.reload()
        return str(self.__doc.phase)

    def __eq__(self,rhs):
        self.__doc.reload()
        return self.__doc.phase==rhs

    def __ne__(self,rhs):
        self.__doc.reload()
        return self.__doc.phase!=rhs
phase=Phase()


def resetDB(name,host,port,username,password):
    ''' DANGER: THIS WILL RESET DATABASE '''

    # FIXME: Authenticate may break
    conn=Connection(host=host,port=port)

    # TODO: Do Backup stuffs here
    conn.copy_database(name,name+'_'+"_".join(map(str,localtime()[:5])),username=username,password=password)

    # Drop Database
    conn.drop_database(name)

    # Reinitialize Database
    Settings(phase=0).save()


def passwordHash(username,password):
    from hashlib import sha1
    H=lambda x:sha1(x).hexdigest()
    return H(password+H(username))
    
