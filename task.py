
from mongoengine import *
from common import JsonRequestHandler
from user import Professor,Student

# Model
class Task(Document):
    name=StringField(required=True)
    description=StringField()
    professor=ReferenceField(Professor,required=True)
    students=ListField(ReferenceField(Student))
    

# View
class Stu_Task(JsonRequestHandler):
    '''/stu/task'''
    def get(self):
        raise NotImplementedError

class Stu_Task_(JsonRequestHandler):
    '''/stu/task/([^/]+)'''
    def get(self,t):
        raise NotImplementedError
    def post(self,t):
        raise NotImplementedError

class Pro_Task(JsonRequestHandler):
    '''/pro/task'''
    def get(self):
        raise NotImplementedError

class Pro_Task_(JsonRequestHandler):
    '''/pro/task/([^/]+)'''
    def get(self,t):
        raise NotImplementedError
    def post(self,t,s):
        raise NotImplementedError

class Admin_Student(JsonRequestHandler):
    '''/admin/student'''
    def get(self):
        raise NotImplementedError

class Admin_Task(JsonRequestHandler):
    '''/admin/task'''
    def get(self):
        raise NotImplementedError

class Admin_Task_(JsonRequestHandler):
    '''/admin/task/([^/]+)'''
    def get(self,t):
        raise NotImplementedError
    def post(self,t):
        raise NotImplementedError

