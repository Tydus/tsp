
from mongoengine import *
from common import JsonRequestHandler,leafHandler,Settings
from user import Professor,Student,User
from bson import ObjectId

# Model
class Task(Document):
    name=StringField(required=True)
    description=StringField()
    professor=ReferenceField(Professor,required=True)
    students=ListField(ReferenceField(Student))
    applyTo=ReferenceField(Student)
    
# View
@leafHandler(r'''/addtask''')
class AddTask(JsonRequestHandler):
    def post(self):
        phase=Settings.objects().first().phase
        if phase!=0:
            return self.write({'err':'Not Your Turn'})

        try:
            user=Professor.objects(username=self.get_secure_cookie('u')).first()
        except:
            return self.write({'err':'No Such User'})

        t=self.get_secure_cookie('t')

        if t!='pro':
            return self.write({'err':'Access Denied'})

        name=self.get_argument('name')
        desc=self.get_argument('desc')

        Task(name=name,description=desc,professor=user,students=[]).save()
        return self.write({})

@leafHandler(r'''/task''')
class Task_(JsonRequestHandler):
    def get(self):
        l=[]
        for i in Task.objects:
            t={
                'id':str(i.id),
                'name':i.name,
                'desc':i.description,
                'prof':i.professor.realname,
                'stu':[{'name':x.realname,'username':x.username} for x in i.students],
                }
            if i.applyTo:
                t['apply']={'name':i.applyTo.realname,'username':i.applyTo.username}
            l.append(t)

        if self.get_argument('filter',None)=='unassigned':
            l=[i for i in l if i['stu']==[]]

        return self.write({'task':sorted(l,key=lambda x:x['name'])})

    def post(self):
        phase=Settings.objects().first().phase
        if not User.objects(username=self.get_secure_cookie('u')).first():
            return self.write({'err':'No Such User'})

        t=self.get_secure_cookie('t')
        if t=='stu':
            task=self.get_argument('task')

            if phase not in [1,3]:
                return self.write({'err':'Not Your Turn'})

            s=Student.objects(username=self.get_secure_cookie('u')).first()

            d=Task.objects(id=ObjectId(task)).first()
            if not d:
                return self.write({'err':'Task not Exist'})

            # Clear Currently Selected
            Task.objects.update(pull__students=s)

            d.reload()
            d.students.append(s)
            d.save()

        if t=='pro':
            task=self.get_argument('task')
            choice=self.get_argument('choice')

            if phase not in [2,4]:
                return self.write({'err':'Not Your Turn'})

            d=Task.objects(id=ObjectId(task)).first()
            if not d:
                return self.write({'err':'Task not Exist'})
            c=None
            for i in d.students:
                if i.username==choice:
                    c=i
            if not c:
                return self.write({'err':'Out of Range'})

            c.applied=d.name
            c.save()

            d.applyTo=c
            d.student=[]
            d.save()

        if t=='admin':
            task=self.get_argument('task')
            stu=self.get_argument('choice')

            if phase!=5:
                return self.write({'err':'Not Your Turn'})

            d=Task.objects(id=ObjectId(task)).first()
            if not d:
                return self.write({'err':'Task not Exist'})
            if d.applyTo:
                return self.write({'err':'Already applied'})
            s=Student.objects(username=stu).first()
            if not s:
                return self.write({'err':'No Such Student'})
    
            s.applied=d.name
            s.save()
            
            d.applyTo=s
            d.save()

        return self.write({})

