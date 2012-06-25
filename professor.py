# -*- coding: utf-8 -*-

################################################################################
#                 Graduation Design Subject Double-Choose System               #
#                               Background Components                          #
#                                                                              #
#   Author: Tydus Ken <Tydus@Tydus.org>                                        #
#   Written: June. 2012                                                        #
#                                                                              #
################################################################################

from model import Professor,Student,User,Settings
from util import JsonRequestHandler,leafHandler,phase
from tornado.web import HTTPError
from bson import ObjectId
from json import dumps
from operator import itemgetter

@leafHandler(r'''/add''')
class hAdd(JsonRequestHandler):
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

@leafHandler(r'''/approve''')
class hApprove(JsonRequestHandler):
    def post(self):
        if not User.objects(username=self.get_secure_cookie('u')).first():
            return self.write({'err':'No Such User'})

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
