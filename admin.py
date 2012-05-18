
from mongoengine import *
from common import JsonRequestHandler

# Model
class Settings(DynamicDocument):
    pass

# View
class AdvancePhase(AdminRequestHandler):
    d=Settings.get(phase__not=None)
    d.phase+=1
    d.save()
    self.write({'err':0,'phase':d.phase})
