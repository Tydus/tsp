
from mongoengine import *
from common import JsonRequestHandler,leafHandler,Settings
from user import Professor,Student
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
                'prof':i.professor.realname,
                'stu':[{'name':x.realname,'username':x.username} for x in i.students],
                })

        if self.get_argument('filter',None)=='unassigned':
            l=[i for i in l if i['stu']==[]]

        return self.write({'task':sorted(l,key=lambda x:x['name'])})

    def post(self):
        phase=Settings.objects().first().phase
        try:
            user=Student.objects(username=self.get_secure_cookie('u')).first()
        except:
            return self.write({'err':'No Such User'})


        t=self.get_secure_cookie('t')
        if t=='stu':
            task=self.get_argument('task')

            if phase not in [0,2]:
                return self.write({'err':'Not Your Turn'})

            d=Task.objects(id=ObjectId(task)).first()
            if not d:
                return self.write({'err':'Task not Exist'})
            if len(d.students)>=2:
                return self.write({'err':'Task Full'})

            # Clear Currently Selected
            Task.objects.update(pull__students=user)

            d.students.append(user)
            d.save()

        if t=='pro':
            task=self.get_argument('task')
            choice=self.get_argument('choice')

            if phase not in [1,3]:
                return self.write({'err':'Not Your Turn'})

            d=Task.objects(id=ObjectId(task)).first()
            if not d:
                return self.write({'err':'Task not Exist'})
            if d.professor!=user:
                return self.write({'err':'Not Your Task'})
            for i in d.students:
                if i.username==choice:
                    c=i
            if not c:
                return self.write({'err':'Out of Range'})
            d.students=[c]
            d.save()

        if t=='admin':
            task=self.get_argument('task')
            stu=self.get_argument('choice')

            if phase!=4:
                return self.write({'err':'Not Your Turn'})

            d=Task.objects(id=ObjectId(task)).first()
            if not d:
                return self.write({'err':'Task not Exist'})
            if d.students:
                return self.write({'err':'Already has Assignee'})
            s=Student.objects(username=stu).first()
            if not s:
                return self.write({'err':'No Such Student'})
            d.students=[s]
            d.save()

        return self.write({})

