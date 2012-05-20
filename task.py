
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
@leafHandler(r'''/task''')
class Task_(JsonRequestHandler):
    def get(self):
        l=[]
        for i in Task.objects:
            l.append({
                'name':i.name,
                'desc':i.description,
                'prof':{'name':i.professor.realname},
                'stu':[{'name':x.realname} for x in i.students],
                })
        return self.write({'task':l})

