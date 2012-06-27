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
from util import JsonRequestHandler,leafHandler,authenticated
from tornado.web import HTTPError
from bson import ObjectId
from json import dumps
from operator import itemgetter

@leafHandler(r'''/add''')
class hAdd(JsonRequestHandler):
    @authenticated([Professor],[0])
    def post(self):
        u=self.current_user
        if u.__class__!=Professor:
            raise HTTPError(403)

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
    @authenticated([Professor],[2,4])
    def post(self):

        subject=self.get_argument('subject')
        student=self.get_argument('student')

        s=Subject.objects(id=ObjectId(subject)).first()
        if not s:
            return self.write({'err':'Subject not Exist'})

        # FIXME: may break since EmbeddedDocument
        if subject.professor!=self.current_user:
            return self.write({'err':'Not your Subject'})

        '''
        # Make sure the selected student exists
        exists=False
        for u in s.selected_by:
            if u.name==student:
                exists=True
        if not Exists:
            return self.write({'err':'No such student'})
        '''

        for u in s.selected_by:
            u.selected=None
            if u.name==student:
                # You are the one!
                s.applied_to=u
                u.applied_to=s
            u.save()

        s.selected_by=[]
        s.save()

        self.write({})
