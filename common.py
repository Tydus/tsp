
from tornado.web import RequestHandler,HTTPError
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

    '''
    def write(self,obj):
        return RequestHandler.write(self,json_encode(obj))
    '''

    def prepare(self):
        uri=self.request.path.split('/')[1:]
        print uri
        if uri[0] in ['student','professor','admin']:
            if not self.current_user or lower(self.get_secure_cookie('t'))!=uri[0]:
                raise HTTPError(403)

