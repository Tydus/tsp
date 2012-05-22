
from mongoengine import *
from common import JsonRequestHandler,leafHandler

# Model
class Settings(DynamicDocument):
    pass

# View
@leafHandler(r'''/phase''')
class Phase(JsonRequestHandler):
    def get(self):
        d=Settings.objects().first()
        self.write({'phase':d.phase})

    def post(self):
        d=Settings.objects().first()
        d.phase+=1
        d.save()
        self.write({'phase':d.phase})
