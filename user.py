
from mongoengine import *
from common import JsonRequestHandler,leafHandler,HTTPError

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
@leafHandler(r'''/login''')
class Login(JsonRequestHandler):
    def post(self):
        '''
        username=<>&password=<>
        '''
        u=User.objects(username=self.get_argument('username')).first()
        if not u:
            return self.write({'err':'No such user'})
        if u.password!=self.get_argument('password'):
            return self.write({'err':'Password mismatch'})
        self.set_secure_cookie('u',u.username)
        for i in [Student,Professor,Admin]:
            if isinstance(u,i):
                self.set_secure_cookie('t',{'Student':'stu','Professor':'pro','Admin':'admin'}[i.__name__])
        return self.write({'type':self.get_secure_cookie('t')})

@leafHandler(r'''/logout''')
class Logout(JsonRequestHandler):
    def post(self):
        self.clear_cookie('u')
        self.clear_cookie('t')
        return self.write({})

@leafHandler(r'''/me''')
class Me(JsonRequestHandler):
    def get(self):
        u=self.get_secure_cookie('u')
        if not u:
            raise HTTPError(403)
        u=User.objects(username=u).first()
        if not u:
            return self.write({'err':'No such user'})
        return self.write({'username':u.username,'name':u.realname})


@leafHandler(r'''/student''')
class Student_(JsonRequestHandler):
    def get(self):
        l=[]
        for i in Student.objects:
            l.append({'username':i.username,'name':i.realname})
        return self.write({'student':l})

