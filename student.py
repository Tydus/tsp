# -*- coding: utf-8 -*-

################################################################################
#                 Graduation Design Subject Double-Choose System               #
#                               Background Components                          #
#                                                                              #
#   Author: Tydus Ken <Tydus@Tydus.org>                                        #
#   Written: June. 2012                                                        #
#                                                                              #
################################################################################

from model import Professor,Student,User,Settings,Subject
from util import JsonRequestHandler,leafHandler,authenticated
from tornado.web import HTTPError
from bson import ObjectId
from json import dumps
from operator import itemgetter
from StringIO import StringIO
from urllib import quote

@leafHandler(r'''/select''')
class hSelect(JsonRequestHandler):
    @authenticated([Student],[1,3])
    def post(self):
        subject=self.get_argument('subject',"")

        u=self.current_user
        if u.excluded:
            return self.write({'err':'你被从选课中排除'})
        if u.applied_to:
            return self.write({'err':'你已被'+u.applied_to.name.encode('utf-8')+'课题选中'})

        if not subject:
            # Clear Currently Selected
            if u.selected:
                old_s=u.selected
                #u.selected=None
                old_s.selected_by=[i for i in old_s.selected_by if i.id!=u.id]
                old_s.save()
                u.save()

	else:
            s=Subject.objects(id=ObjectId(subject)).first()
            if not s:
                return self.write({'err':'课题不存在'})
            if s.applied_to:
                return self.write({'err':'课题已被'+s.applied_to.realname.encode('utf-8')+'选中'})

            # Clear Currently Selected
            if u.selected:
                old_s=u.selected
                #u.selected=None
                old_s.selected_by=[i for i in old_s.selected_by if i.id!=u.id]
                old_s.save()

            # Beware if old_s==s
            s.reload()

            # Select New
            if subject:
                u.selected=s
                s.selected_by.append(u)
            s.save()

        u.save()

        self.write({})

@leafHandler(r'''/resume''')
class hResume(JsonRequestHandler):
    @authenticated()
    def get(self):
        student=self.get_argument('student',"")

        u=Student.objects(username=student).first()
        if not u or not u.resume:
            raise HTTPError(404)

        # Guess browser and write Content-Disposition

        # FIXME: an ugly hack here due to a MongoEngine bug
        #        must use `u.resume.name' for filename while write using `filename'

        # FIXME: filename will break on android with its internal browser
        e=quote(u.resume.name.encode('utf-8')).replace('+','%20')
        ua=self.request.headers['User-Agent'].lower()
        if "msie" in ua:
            cd='filename="%s"'%e
        elif "firefox" in ua:
            cd="filename*=UTF-8''%s"%e
        else:
            cd='filename="%s"'%u.resume.name
        self.set_header('Content-Disposition','attachment;'+cd)
        self.set_header('Content-Type','application/octet-stream')
        self.write(u.resume.read())

    @authenticated([Student],[0,1])
    def post(self):
        u=self.current_user

        r=self.request.files.get('resume')
        if not r:
            raise HTTPError(400)
        r=r[0]

        if u.resume:
            u.resume.replace(StringIO(r['body']),filename=r['filename'])
        else:
            u.resume.put(StringIO(r['body']),filename=r['filename'])

        u.save()

        self.write({})

