
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
                'id':str(i._id),
                'name':i.name,
                'desc':i.description,
                'prof':{'name':i.professor.realname},
                'stu':[{'name':x.realname} for x in i.students],
                })
        return self.write({'task':l})
    def post(self):
        t=self.get_secure_cookie('t')
        if t=='stu':
            task=self.get_argument('task')

            d=Task.objects(_id=ObjectId(task)).first()
            if not d:
                return self.write({'err':'Task not Exist'})
            d.students.append(Student.objects(username=self.get_secure_cookie('u').first()))
            d.save()

        if t=='pro':
            task=self.get_argument('task')
            choice=int(self.get_argument('choice'))

            d=Task.objects(_id=ObjectId(task)).first()
            if not d:
                return self.write({'err':'Task not Exist'})
            if choice>=len(d.students):
                return self.write({'err':'Out of Range'})
            d.students=[d.students[choice]]
            d.save()

        if t=='admin':
            task=self.get_argument('task')
            stu=self.get_argument('stu')
            d=Task.objects(_id=ObjectId(task)).first()
            if not d:
                return self.write({'err':'Task not Exist'})
            if d.students:
                return self.write({'err':'Already has Assignee'})
            s=Student.objects(_id=stu).first()
            if not s:
                return self.write({'err':'No Such Student'})
            d.students=[s]
            d.save()


        return self.write({})

