
from mongoengine import *
from common import JsonRequestHandler,leafHandler,Settings
from user import Student
from task import Task

# View
@leafHandler(r'''/phase''')
class Phase(JsonRequestHandler):
    def get(self):
        d=Settings.objects().first()
        self.write({'phase':d.phase})

    def post(self):
        d=Settings.objects().first()
        d.phase+=1
        d.save()
        self.write({'phase':d.phase})


@leafHandler(r'''/student''')
class Student_(JsonRequestHandler):
    def get(self):
        l=[]
        for i in Student.objects(applied=None):
            l.append({'username':i.username,'name':i.realname})

        return self.write({'student':l})

