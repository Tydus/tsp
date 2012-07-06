# -*- coding: utf-8 -*-

################################################################################
#                 Graduation Design Subject Double-Choose System               #
#                               Background Components                          #
#                                                                              #
#   Author: Tydus Ken <Tydus@Tydus.org>                                        #
#   Written: June. 2012                                                        #
#                                                                              #
################################################################################

from model import User,Admin,Settings,Professor,Student,Subject
from util import JsonRequestHandler,leafHandler,phase,resetDB,passwordHash,authenticated,sessions,clearSelection
from tornado.web import HTTPError
from bson import ObjectId

@leafHandler(r'''/phase''')
class hPhase(JsonRequestHandler):
    def get(self):
        d=Settings.objects().first()
        self.write({'phase':d.phase})

    @authenticated([Admin])
    def post(self):
        password=self.get_argument('password',"")
        if password!=self.current_user.password:
            return self.write({'err':'密码错误'})

        d=Settings.objects().first()

        if d.phase==6:
            return self.write({'err':'不能再推进阶段'})

        if d.phase in [2,4]:
            clearSelection()

        d.phase+=1
        d.save()
        self.write({'phase':d.phase})

@leafHandler(r'''/announce''')
class hAnnounce(JsonRequestHandler):
    def get(self):
        d=Settings.objects().first()
        self.write({'announce':d.announce})

    @authenticated([Admin])
    def post(self):
        d=Settings.objects().first()
        d['announce']=self.get_argument('announce')
        d.save()
        self.write({})

@leafHandler(r'''/reset''')
class hReset(JsonRequestHandler):
    @authenticated([Admin])
    def post(self):
        password=self.get_argument('password',"")
        if password!=self.current_user.password:
            return self.write({'err':'密码错误'})
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
            return self.write({'err':'课题不存在'})
        if s.applied_to:
            return self.write({'err':'课题已被分配给'+s.applied_to.realname.encode('utf-8')})

        u=Student.objects(username=student).first()
        if not u:
            return self.write({'err':'学生不存在'})
        if u.applied_to:
            return self.write({'err':'学生已被分配'+u.applied_to.name.encode('utf-8')+'课题'})

        # Match Straightly
        s.selected_by=[]
        s.applied_to=u
        u.selected=None
        u.applied_to=s

        s.save()
        u.save()

        self.write({})
