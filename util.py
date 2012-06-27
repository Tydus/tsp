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
from time import time
from functools import wraps
from model import Settings,Student,Professor,Admin

# Session Storage
TTL=15*60 # 15min
class SessionStorage():

    def __init__(self):
        self.__dict__['__sessions']={}

    def __getitem__(self,key):
        if key==None:
            return None

        ss=self.__dict__['__sessions']
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
        ss=self.__dict__['__sessions']
        ss[s]={'user':user,'ttl':time()+TTL}
        return s

    def deleteSession(self,session):
        ss=self.__dict__['__sessions']
        if ss.has_key(session):
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
        import pdb
        pdb.set_trace()
        u=sessions[self.get_cookie('sid')]
        if not u:
            return None
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


def resetDB(name='tsp',host='localhost',port='27017',username='tsp',password='tsp'):
    ''' DANGER: THIS WILL RESET DATABASE '''

    # FIXME: Authenticate may break
    conn=Connection(host=host,port=port)

    # Backup
    conn.copy_database(name,name+'_'+"_".join(map(str,localtime()[:5])),username=username,password=password)

    # Drop Database
    conn.drop_database(name)

    # Reinitialize Database
    Settings(phase=0).save()
    Admin(username='admin',password=passwordHash('admin','admin')).save()

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
                return self.write({'err':'not your turn'})

            if self.current_user.__class__ not in roles:
                return HTTPError(403)

            return method(self, *args, **kwargs)
        return wrapper
    return decorator
