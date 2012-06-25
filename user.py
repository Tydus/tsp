# -*- coding: utf-8 -*-

################################################################################
#                 Graduation Design Subject Double-Choose System               #
#                               Background Components                          #
#                                                                              #
#   Author: Tydus Ken <Tydus@Tydus.org>                                        #
#   Written: June. 2012                                                        #
#                                                                              #
################################################################################

from model import User,Student,Professor,Admin
from tornado.web import authenticated
from common import JsonRequestHandler,leafHandler


# View
@leafHandler(r'''/login''')
class hLogin(JsonRequestHandler):
    def post(self):
        u=User.objects(username=self.get_argument('username')).first()
        if not u:
            return self.write({'err':'No such user'})
        if u.password!=self.get_argument('password'):
            return self.write({'err':'Password mismatch'})

        sid=sessions.createSession(u)
        self.set_secure_cookie('sid',sid)
        return self.write({'type':u.__class__.__name__})

@leafHandler(r'''/logout''')
class hLogout(JsonRequestHandler):
    @authenticated
    def post(self):
        self.deleteSession(self.get_secure_cookie('sid'))
        self.clear_cookie('sid')
        return self.write({})

@leafHandler(r'''/me''')
class hMe(JsonRequestHandler):
    @authenticated
    def get(self):
        u=get_current_user()
        return self.write({'username':u.username,'name':u.realname})
