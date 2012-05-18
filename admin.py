
from mongoengine import *
from common import JsonRequestHandler

# Model
class Settings(DynamicDocument):
    pass

# View
class Admin_Phase(JsonRequestHandler):
    r'''/admin/phase'''
    def get(self):
        d=Settings.get(phase__not=None)
        self.write({'phase':d.phase})

    def post(self):
        d=Settings.get(phase__not=None)
        d.phase+=1
        d.save()
        self.write({'err':0,'phase':d.phase})
