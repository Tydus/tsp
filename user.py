
from mongoengine import *
from common import JsonRequestHandler,leafHandler,HTTPError,Settings

# Model

class User(Document):
    meta={'allow_inheritance':True}
    username=StringField(required=True,primary_key=True)
    password=StringField(required=True)
    realname=StringField(required=True)
    applied=StringField()

class Student(User):
    pass

class Professor(User):
    pass

class Admin(User):
    pass

allow_phase={'stu':[1,3,6],'pro':[0,2,4,6],'admin':range(7)}

# View
@leafHandler(r'''/login''')
class Login(JsonRequestHandler):
    def post(self):
        u=User.objects(username=self.get_argument('username')).first()
        if not u:
            return self.write({'err':'No such user'})
        if u.password!=self.get_argument('password'):
            return self.write({'err':'Password mismatch'})
        for i in [Student,Professor,Admin]:
            if isinstance(u,i):
                t={'Student':'stu','Professor':'pro','Admin':'admin'}[i.__name__]
                phase=Settings.objects().first().phase
                if phase not in allow_phase[t]:
                    return self.write({'err':'Not your phase'})
                if u.applied:
                    return self.write({'err':'You are Selected by '+u.applied})

        self.set_secure_cookie('u',u.username)
        self.set_secure_cookie('t',t)
        return self.write({'type':t})

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
