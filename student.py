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
        subject=self.get_argument('subject')

        u=self.current_user

        s=Subject.objects(id=ObjectId(subject)).first()
        if not s:
            return self.write({'err':'Subject not Exist'})

        ret={}

        # Clear Currently Selected
        if u.selected:
            old_s=u.selected
            #u.selected=None
            old_s.selected_by.remove(u)
            old_s.save()
            ret['dropped']=old_s.id

        # Beware if old_s==s
        s.reload()

        # Select New
        u.selected=s
        s.selected_by.append(u)

        s.save()
        u.save()

        ret['selected']=s.id
        return ret
