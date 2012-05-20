
from mongoengine import *
from common import JsonRequestHandler,leafHandler
from user import Professor,Student

# Model
class Task(Document):
    name=StringField(required=True)
    description=StringField()
    professor=ReferenceField(Professor,required=True)
    students=ListField(ReferenceField(Student))
    

# View
@leafHandler(r'''/stu/task''')
class Stu_Task(JsonRequestHandler):
    def get(self):
        raise NotImplementedError

@leafHandler(r'''/stu/task/([^/]+)''')
class Stu_Task_(JsonRequestHandler):
    def get(self,t):
        raise NotImplementedError
    def post(self,t):
        raise NotImplementedError

@leafHandler(r'''/pro/task''')
class Pro_Task(JsonRequestHandler):
    def get(self):
        raise NotImplementedError

@leafHandler(r'''/pro/task/([^/]+)''')
class Pro_Task_(JsonRequestHandler):
    def get(self,t):
        raise NotImplementedError
    def post(self,t,s):
        raise NotImplementedError

@leafHandler(r'''/admin/student''')
class Admin_Student(JsonRequestHandler):
    def get(self):
        raise NotImplementedError

@leafHandler(r'''/admin/task''')
class Admin_Task(JsonRequestHandler):
    def get(self):
        raise NotImplementedError

@leafHandler(r'''/admin/task/([^/]+)''')
class Admin_Task_(JsonRequestHandler):
    def get(self,t):
        raise NotImplementedError
    def post(self,t):
        raise NotImplementedError

