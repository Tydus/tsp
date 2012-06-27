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

@leafHandler(r'''/select''')
class hSelect(JsonRequestHandler):
    @authenticated([Student],[1,3])
    def post(self):
        if not User.objects(username=self.get_secure_cookie('u')).first():
            return self.write({'err':'No Such User'})

        t=self.get_secure_cookie('t')

        task=self.get_argument('task')

        s=Student.objects(username=self.get_secure_cookie('u')).first()

        d=Task.objects(id=ObjectId(task)).first()
        if not d:
            return self.write({'err':'Task not Exist'})

        # Clear Currently Selected
        Task.objects.update(pull__students=s)

        d.reload()
        d.students.append(s)
        d.save()
