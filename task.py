
from model import Professor,Student,User,Settings
from common import JsonRequestHandler,leafHandler,phase
from tornado.web import HTTPError
from bson import ObjectId
from json import dumps
from operator import itemgetter

@leafHandler(r'''/addtask''')
class hAddTask(JsonRequestHandler):
    def post(self):
        u=self.get_current_user()
        if u.__class__!=Professor:
            raise HTTPError(403)

        if phase!=0:
            return self.write({'err':'Not Your Turn'})

        name=self.get_argument('name')
        desc=self.get_argument('desc')
        
        type1=self.get_argument('type1')
        type2=self.get_argument('type2')
        source=self.get_argument('source')


        t=Task(name=name,professor=user)

        rol=dumps(dict(
                id=str(t.id),
                name=name,
                desc=desc,
                type1=type1,
                type2=type2,
                source=source,
                professor=user.realname,
                title=user.title,
                direction=user.direction,
        ))
        try:
            file('subjects.lst','a').write(rol)
        except:
            raise HTTPError(500,'Cannot write to subjects.lst')

        t.save()

        return self.write(rol)

@leafHandler(r'''/task''')
class hTask(JsonRequestHandler):
    def get(self):
        l=[]
        for i in Task.objects:
            t={
                'id':str(i.id),
                'name':i.name,
                'selected_by':[{'realname':x.realname,'username':x.username} for x in i.selected_by],
                'applied_to':{'realname':i.applied_to.realname,'username':i.applied_to.username},
                }
            l.append(t)

        return self.write({'task':sorted(l,key=itemgetter('name'))})

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

