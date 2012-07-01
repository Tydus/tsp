# -*- coding: utf-8 -*-

################################################################################
#                 Graduation Design Subject Double-Choose System               #
#                               Background Components                          #
#                                                                              #
#   Author: Tydus Ken <Tydus@Tydus.org>                                        #
#   Written: June. 2012                                                        #
#                                                                              #
################################################################################

from model import User,Admin,Settings,Professor,Student
from util import JsonRequestHandler,leafHandler,phase,resetDB,passwordHash,authenticated,sessions
from tornado.web import HTTPError

@leafHandler(r'''/phase''')
class hPhase(JsonRequestHandler):
    @authenticated([Admin])
    def get(self):
        d=Settings.objects().first()
        self.write({'phase':d.phase})

    @authenticated([Admin])
    def post(self):
        d=Settings.objects().first()
        d.phase+=1
        d.save()
        self.write({'phase':d.phase})


@leafHandler(r'''/reset''')
class hReset(JsonRequestHandler):
    @authenticated([Admin])
    def post(self):
        password=self.get_argument('password')
        if password!=self.current_user.password:
            raise HTTPError(403)
        resetDB()
        sessions.clear()

        self.write({})

@leafHandler(r'''/import''')
class hImport(JsonRequestHandler):
    @authenticated([Admin],[0])
    def post(self):
        from csv import reader
        from StringIO import StringIO

        for t,v in self.request.files.items():
            b=v[0]['body']
            r=reader(StringIO(b))

            # Strip first 2 lines
            r.next()
            r.next()

            # Import Data to DB
            if t=='student':
                for i in r:
                    d=dict(zip([
                        'foo',
                        'username',
                        'realname',
                        'cls',
                        'cls_index',
                        'department',
                        ], i))
                    del d['foo']
                    d['password']=passwordHash(d['username'],d['username'])
                    Student(**d).save()
            elif t=='professor':
                for i in r:
                    d=dict(zip([
                        'foo',
                        'username',
                        'realname',
                        'title',
                        'direction',
                        'department',
                        ], i))
                    del d['foo']
                    d['password']=passwordHash(d['username'],d['username'])
                    Professor(**d).save()
            else:
                raise HTTPError(400)
        self.write({})

@leafHandler(r'''/match''')
class hMatch(JsonRequestHandler):
    @authenticated([Admin],[5])
    def post(self):

        subject=self.get_argument('subject')
        student=self.get_argument('student')

        s=Subject.objects(id=ObjectId(subject)).first()
        if not s:
            return self.write({'err':'Subject not Exist'})
        if s.applied_to:
            return self.write({'err':'The Subject is applied to '+s.applied_to.name})

        u=Student.objects(id=ObjectId(student)).first()
        if not u:
            return self.write({'err':'Student not Exist'})
        if u.applied_to:
            return self.write({'err':'the Student is approved by '+u.applied_to.name})

        # Match Straightly
        s.selected_by=[]
        s.applied_to=u
        u.selected=None
        u.applied_to=s

        s.save()
        u.save()

        self.write({})
