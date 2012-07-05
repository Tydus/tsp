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
            return self.write({'err':'用户不存在'})
        if u.password!=self.get_argument('password'):
            return self.write({'err':'密码错误'})

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
            return self.write({'err':'旧密码错误'})
        if not newpw:
            return self.write({'err':'没有新密码'})

        u.password=newpw
        u.save()
        self.write({})

@leafHandler(r'''/profile''')
class hProfile(JsonRequestHandler):
    @authenticated()
    def get(self):
        u=self.current_user

        ret={
            'username':u.username,
            'realname':u.realname,
            'role':u.__class__.__name__,
        }
        if u.__class__==Student:
            ret['department']=u.department
            ret['cls']=u.cls
            ret['cls_index']=u.cls_index
            ret['selected']=str(u.selected.id) if u.selected else None
            ret['applied_to']=str(u.applied_to.id) if u.applied_to else None
            ret['excluded']=u.excluded
        elif u.__class__==Professor:
            ret['department']=u.department
            ret['title']=u.title
            ret['direction']=u.direction

        self.write(ret)

@leafHandler(r'''/subject''')
class hSubject(JsonRequestHandler):
    def get(self):
        l=[]
        for i in Subject.objects:
            t={
                'id':str(i.id),
                'name':i.name,
                'desc':i.desc,
                'type1':i.type1,
                'type2':i.type2,
                'source':i.source,
                'professor':{
                    'username':i.professor.username,
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

