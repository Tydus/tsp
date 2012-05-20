
from tornado.web import RequestHandler
from tornado.escape import json_encode

leafHandlers=[]

def leafHandler(path):
    def _deco(cls):
        leafHandlers.append((path,cls))
        return cls
    return _deco

class JsonRequestHandler(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('u')
