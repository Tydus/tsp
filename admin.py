# -*- coding: utf-8 -*-

################################################################################
#                 Graduation Design Subject Double-Choose System               #
#                               Background Components                          #
#                                                                              #
#   Author: Tydus Ken <Tydus@Tydus.org>                                        #
#   Written: June. 2012                                                        #
#                                                                              #
################################################################################

from model import User,Admin,Settings
from common import JsonRequestHandler,leafHandler,phase


@leafHandler(r'''/phase''')
class hPhase(JsonRequestHandler):

    def prepare(self):
        if get_current_user().__class__!=Admin:
            raise HTTPError(403)

    def get(self):
        self.write({'phase':str(phase)})

    def post(self):
        d=Settings.objects().first()
        d.phase+=1
        d.save()
        self.write({'phase':d.phase})

