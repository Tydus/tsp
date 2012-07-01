# -*- coding: utf-8 -*-

################################################################################
#                 Graduation Design Subject Double-Choose System               #
#                               Background Components                          #
#                                                                              #
#   Author: Tydus Ken <Tydus@Tydus.org>                                        #
#   Written: June. 2012                                                        #
#                                                                              #
################################################################################

from model import User,Student,Professor,Admin,Subject
from util import JsonRequestHandler,leafHandler,authenticated,sessions
from operator import itemgetter

@leafHandler(r'''/login''')
class hLogin(JsonRequestHandler):
    def post(self):
        u=User.objects(username=self.get_argument('username')).first()
        if not u:
            return self.write({'err':'No such user'})
        if u.password!=self.get_argument('password'):
            return self.write({'err':'Password mismatch'})

        sid=sessions.createSession(u)
        self.set_cookie('sid',sid)
        return self.write({'role':u.__class__.__name__})

@leafHandler(r'''/logout''')
class hLogout(JsonRequestHandler):
    @authenticated()
    def post(self):
        sessions.deleteSession(self.get_cookie('sid'))
        self.clear_cookie('sid')
        return self.write({})

@leafHandler(r'''/chpasswd''')
class hChPasswd(JsonRequestHandler):
    @authenticated()
    def post(self):
        pw=self.get_argument('password')
        newpw=self.get_argument('new_password')

        u=self.current_user

        if pw!=u.password:
            return self.write({'err':'Old password mismatch'})
        if not newpw:
            return self.write({'err':'No new password'})

        u.password=newpw
        u.save()
        self.write({})

@leafHandler(r'''/profile''')
class hProfile(JsonRequestHandler):
    @authenticated()
    def get(self):
        u=self.current_user
        return self.write({
            'username':u.username,
            'realname':u.realname,
            'role':u.__class__.__name__,
        })

@leafHandler(r'''/subject''')
class hSubject(JsonRequestHandler):
    def get(self):
        l=[]
        for i in Subject.objects:
            t={
                'id':str(i.id),
                'name':i.name,
                'type1':i.type1,
                'type2':i.type2,
                'source':i.source,
                'professor':{
                    'realname':i.professor.realname,
                    'title':i.professor.title,
                    'direction':i.professor.direction,
                },
                   
                'selected_by':[{'realname':x.realname,'username':x.username} for x in i.selected_by],
                'applied_to':{'realname':i.applied_to.realname,'username':i.applied_to.username} if i.applied_to else None,
                }
            l.append(t)

        return self.write({'subject':sorted(l,key=itemgetter('name'))})

@leafHandler(r'''/student''')
class hStudent(JsonRequestHandler):
    def get(self):
        l=[]
        for i in Student.objects:
            t={
                'username':i.username,
                'realname':i.realname,
                'cls':i.cls,
                'cls_index':i.cls_index,
                'selected':str(i.selected.id) if i.selected else None,
                'applied_to':str(i.applied_to.id) if i.applied_to else None,
                'excluded':i.excluded,
                }
            l.append(t)

        return self.write({'student':sorted(l,key=itemgetter('username'))})

