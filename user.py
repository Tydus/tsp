
from mongoengine import *
from common import JsonRequestHandler

# Model

class User(Document):
    meta={'allow_inheritance':True}
    username=StringField(required=True,primary_key=True)
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
        if self.get_secure_cookie('u') and self.get_secure_cookie('t'):
            return self.write({'type':self.get_secure_cookie('t')})
        u=User.objects(username=self.get_argument('username')).first()
        if not u:
            return self.write({'err':'No such user'})
        if u.password!=self.get_argument('password'):
            return self.write({'err':'Password mismatch'})
        self.set_secure_cookie('u',u.username)
        for i in [Student,Professor,Admin]:
            if isinstance(u,i):
                self.set_secure_cookie('t',i.__name__)
        return self.write({'type':self.get_secure_cookie('t')})

class Logout(JsonRequestHandler):
    r'''/logout'''
    def post(self):
        self.clear_cookie('u')
        self.clear_cookie('t')
        return {}

