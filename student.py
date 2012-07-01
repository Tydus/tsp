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

@leafHandler(r'''/select''')
class hSelect(JsonRequestHandler):
    @authenticated([Student],[1,3])
    def post(self):
        subject=self.get_argument('subject')

        u=self.current_user
        if u.excluded:
            return self.write({'err':'You are excluded from selecting'})
        if u.applied_to:
            return self.write({'err':'You are approved by '+u.applied_to.name})

        s=Subject.objects(id=ObjectId(subject)).first()
        if not s:
            return self.write({'err':'Subject not Exist'})
        if s.applied_to:
            return self.write({'err':'The Subject is applied to '+s.applied_to.name})

        # Clear Currently Selected
        if u.selected:
            old_s=u.selected
            #u.selected=None
            old_s.selected_by=[i for i in old_s.selected_by if i.id!=u.id]
            old_s.save()

        # Beware if old_s==s
        s.reload()

        # Select New
        u.selected=s
        s.selected_by.append(u)

        s.save()
        u.save()

        self.write({})
