
from mongoengine import *
from common import JsonRequestHandler

# Model
class Settings(DynamicDocument):
    pass

# View
class AdvancePhase(AdminRequestHandler):
    Settings.get(phase=).update(inc__phase=1)

    self.write({'ok':True})
