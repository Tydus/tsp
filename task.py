
from mongoengine import *
from common import JsonRequestHandler
from user import Professor,Student

# Model
class Task(Document):
    name=StringField(required=True)
    professor=ReferenceField(Professor)
    students=ListField(ReferenceField(Student))
    

# View
class ChooseTask(StudentRequestHandler):
    def post(self):
        raise NotImplementedError

class ChooseStudent(ProfessorRequestHandler):
    def post(self):
        raise NotImplementedError

class AssignStudent(AdminRequestHandler):
    def post(self):
        raise NotImplementedError

