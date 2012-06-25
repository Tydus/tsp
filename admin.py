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
from util import JsonRequestHandler,leafHandler,phase,resetDB,passwordHash
from tornado.web import HTTPError

class AdminRequestHandler(JsonRequestHandler):
    def prepare(self):
        if get_current_user().__class__!=Admin:
            raise HTTPError(403)

@leafHandler(r'''/phase''')
class hPhase(AdminRequestHandler):
    def get(self):
        self.write({'phase':str(phase)})

    def post(self):
        d=Settings.objects().first()
        d.phase+=1
        d.save()
        self.write({'phase':d.phase})


@leafHandler(r'''/reset''')
class hReset(AdminRequestHandler):
    def post(self):
        password=self.get_argument('password')
        if password!=get_current_user().password:
            raise HTTPError(403)
        resetDB()
        self.write({})

@leafHandler(r'''/import''')
class hImport(AdminRequestHandler):
    def post(self):

        t=request.get_argument('type').lower()

        from csv import reader
        from StringIO import StringIO

        b=request.files[0].body
        r=reader(StringIO(b))

        # Strip first 2 lines
        r.next()
        r.next()

        # Import Data to DB
        if t='student':
            for i in r:
                d=zip([
                    'foo',
                    'username',
                    'realname',
                    'cls',
                    'cls_index',
                    'department',
                    ], i)
                del d['foo']
                d['password']=passwordHash(d['username'],d['username'])
                Student(**d).save()
        elif t=='professor':
            for i in r:
                d=zip([
                    'foo',
                    'username',
                    'realname',
                    'title',
                    'direction',
                    'department',
                    ], i)
                del d['foo']
                d['password']=passwordHash(d['username'],d['username'])
                Professor(**d).save()
        else:
            raise HTTPError(400)

