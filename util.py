# -*- coding: utf-8 -*-

################################################################################
#                 Graduation Design Subject Double-Choose System               #
#                               Background Components                          #
#                                                                              #
#   Author: Tydus Ken <Tydus@Tydus.org>                                        #
#   Written: June. 2012                                                        #
#                                                                              #
################################################################################

from tornado.web import RequestHandler,HTTPError
from bson import ObjectId
from hashlib import sha1
from time import time,localtime
from functools import wraps
from model import Settings,Student,Professor,Admin,Subject
from pymongo import Connection
from mongoengine import connect

# Session Storage
TTL=15*60 # 15min
class SessionStorage():

    def __init__(self):
        self.clear()

    def __getitem__(self,key):
        if key==None:
            return None

        ss=self.__sessions
        # Get User by Session, and update TTL
        if ss.has_key(key):
            if ss[key]['ttl']>=time():
                ss[key]['ttl']=time()+TTL
                return ss[key]['user']
            else:
                del ss[key]
                return None
        else:
            return None

    def createSession(self,user):
        # Create a new Session
        s=sha1(str(ObjectId())).hexdigest()
        self.__sessions[s]={'user':user,'ttl':time()+TTL}
        return s

    def deleteSession(self,session):
        if self.__sessions.has_key(session):
            del self.__sessions[session]

    def clear(self):
        self.__sessions={}

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
        u=sessions[self.get_cookie('sid')]
        if not u:
            return None
        u.reload()
        return u

class LongPollMixin:
    ''' Long Polling '''
    _cb=[]

    @classmethod
    def fire_all(cls,*args,**kwargs):
        ''' Fire all Callbacks and remove if it returns False '''
        cls._cb=[i for i in cls._cb if not (
                    i.__self__.request.connection.stream.closed()
                    or i(*args,**kwargs)
                )]

    @classmethod
    def add_cb(cls,func):
        ''' Add a callback for LP '''
        cls._cb.append(func)

class Phase(object):
    def __str__(self):
        return str(Settings.objects().first().phase)

    def __eq__(self,rhs):
        return Settings.objects().first().phase==rhs

    def __ne__(self,rhs):
        return Settings.objects().first().phase!=rhs
    
phase=Phase()


def resetDB(name='tsp',host='localhost',port=27017,username=None,password=None):
    ''' DANGER: THIS WILL RESET DATABASE '''

    import pymongo

    # FIXME: Authenticate may break
    conn=pymongo.Connection(host=host,port=port)


    if name in conn.database_names():
        # Backup
        conn.copy_database(name,name+'_'+"_".join(map(str,localtime()[:5])),username=username,password=password)

        # Drop Database
        conn.drop_database(name)
    
    connect(name,reconnect=True)
    # (Re)initialize Database

    Admin(
            username='admin',
            password=passwordHash('admin','admin'),
            realname='administrator',
         ).save()
    Settings(phase=0).save()

def passwordHash(username,password):
    from hashlib import sha1
    H=lambda x:sha1(x).hexdigest()
    return H(password+H(username))
    
def authenticated(roles=[Student,Professor,Admin],phases=range(7)):
    def decorator(method):
        """Decorate methods with this to require that the user be logged in."""
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.current_user:
                raise HTTPError(403)

            if phase not in phases:
                return self.write({'err':'该阶段无法进行此操作'})

            if self.current_user.__class__ not in roles:
                return HTTPError(403)

            return method(self, *args, **kwargs)
        return wrapper
    return decorator

def clearSelection():
    Student.objects.update(set__selected=None)
    Subject.objects.update(set__selected_by=[])

