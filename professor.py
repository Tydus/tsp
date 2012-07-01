# -*- coding: utf-8 -*-

################################################################################
#                 Graduation Design Subject Double-Choose System               #
#                               Background Components                          #
#                                                                              #
#   Author: Tydus Ken <Tydus@Tydus.org>                                        #
#   Written: June. 2012                                                        #
#                                                                              #
################################################################################

from model import Professor,Student,User,Subject
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

        name=self.get_argument('name')
        desc=self.get_argument('desc')
        type1=self.get_argument('type1')
        type2=self.get_argument('type2')
        source=self.get_argument('source')

        Subject(
                name=name,
                desc=desc,
                type1=type1,
                type2=type2,
                source=source,
                professor=u,
        ).save()

        return self.write({})

@leafHandler(r'''/approve''')
class hApprove(JsonRequestHandler):
    @authenticated([Professor],[2,4])
    def post(self):

        subject=self.get_argument('subject')
        student=self.get_argument('student')

        s=Subject.objects(id=ObjectId(subject)).first()
        if not s:
            return self.write({'err':'Subject not Exist'})

        if s.professor.username!=self.current_user.username:
            return self.write({'err':'Not your Subject'})

        if s.selected_by==[]:
            return self.write({'err':'Cannot Change Subject Approved in Previous Phase'})

        # Clear previous approvement
        if s.applied_to:
            u=Student.objects(username=s.applied_to.username).first()
            u.applied_to=None
            u.save()
            s.applied_to=None

        for u_embedded in s.selected_by:
            u=Student.objects(username=u_embedded.username).first()
            if u.username==student:
                # You are the one!
                s.applied_to=u
                u.applied_to=s
            u.save()

        s.save()

        self.write({})
