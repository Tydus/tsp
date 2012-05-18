
from mongoengine import *
from common import JsonRequestHandler

# Model

class User(Document):
    username=StringField(required=True)
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
    def post(self):
        raise NotImplementedError


class Logout(JsonRequestHandler):
    def post(self):
        raise NotImplementedError

