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

@leafHandler(r'''/phase''')
class hPhase(JsonRequestHandler):
    @authenticated([Admin])
    def get(self):
        self.write({'phase':str(phase)})

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
        if password!=get_current_user().password:
            raise HTTPError(403)
        resetDB()
        self.write({})

@leafHandler(r'''/import''')
class hImport(JsonRequestHandler):
    @authenticated([Admin],[0])
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

@leafHandler(r'''/match''')
class hMatch(JsonRequestHandler):
    @authenticated([Admin],[5])
    def post(self):
        pass
