
from mongoengine import *
from common import JsonRequestHandler,leafHandler

# Model
class Settings(DynamicDocument):
    pass

# View
@leafHandler(r'''/admin/phase''')
class Admin_Phase(JsonRequestHandler):
    def get(self):
        d=Settings.get(phase__not=None)
        self.write({'phase':d.phase})

    def post(self):
        d=Settings.get(phase__not=None)
        d.phase+=1
        d.save()
        self.write({'phase':d.phase})
