
from mongoengine import *
from common import JsonRequestHandler

# Model

class User(Document):
    username=StringField(required=True,primaryKey=True)
    password=StringField(required=True)
    realname=StringField(required=True)

class Student(User):
    pass

class Professor(User):
    pass

class Admin(User):
    pass


# View
class Login(JsonRequestHandler):
    r'''/login'''
    def post(self):
        '''
        username=<>&password=<>
        '''
        if self.get_secure_cookie('u'):
            return {'err':0}
        u=User.get(username=self.get_argument('username'))
        if not u:
            return {'err':1,'desc':'No such user'}
        if u.password!=self.get_argument('password'):
            return {'err':1,'desc':'Password mismatch'}
        self.set_secure_cookie('u',u.username)
        for i in [Student,Professor,Admin]:
            if isinstance(u,i):
                self.set_secure_cookie('t',i.__name__)
        return {'err':0}

class Logout(JsonRequestHandler):
    r'''/logout'''
    def post(self):
        self.clear_cookie('u')
        self.clear_cookie('t')
        return {'err':0}

