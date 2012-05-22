
from mongoengine import *
from common import JsonRequestHandler,leafHandler
from user import Professor,Student
from admin import Settings
from bson import ObjectId

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
                'id':str(i.id),
                'name':i.name,
                'desc':i.description,
                'prof':{'name':i.professor.realname},
                'stu':[{'name':x.realname} for x in i.students],
                })
        return self.write({'task':l})
    def post(self):
        phase=Settings.objects().first().phase

        t=self.get_secure_cookie('t')
        if t=='stu':
            task=self.get_argument('task')

            if phase not in [0,2]:
                return self.write({'err':'Not Your Turn'})

            d=Task.objects(id=ObjectId(task)).first()
            if not d:
                return self.write({'err':'Task not Exist'})
            d.students.append(Student.objects(username=self.get_secure_cookie('u').first()))
            d.save()

        if t=='pro':
            task=self.get_argument('task')
            choice=int(self.get_argument('choice'))

            if phase not in [1,3]:
                return self.write({'err':'Not Your Turn'})

            d=Task.objects(id=ObjectId(task)).first()
            if not d:
                return self.write({'err':'Task not Exist'})
            if choice>=len(d.students):
                return self.write({'err':'Out of Range'})
            d.students=[d.students[choice]]
            d.save()

        if t=='admin':
            task=self.get_argument('task')
            stu=self.get_argument('stu')

            if phase!=5:
                return self.write({'err':'Not Your Turn'})

            d=Task.objects(id=ObjectId(task)).first()
            if not d:
                return self.write({'err':'Task not Exist'})
            if d.students:
                return self.write({'err':'Already has Assignee'})
            s=Student.objects(id=stu).first()
            if not s:
                return self.write({'err':'No Such Student'})
            d.students=[s]
            d.save()

        return self.write({})

