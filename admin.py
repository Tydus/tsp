
from mongoengine import *
from common import JsonRequestHandler,leafHandler
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
        for i in Student.objects:
            l.append({'username':i.username,'name':i.realname})

        if self.get_argument('filter')=='unassigned':
            for i in Task.objects:
                for j in i.stu:
                    l.remove(j)

        return self.write({'student':l})

