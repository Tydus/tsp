
from tornado.web import RequestHandler,HTTPError
from tornado.escape import json_encode

class JsonRequestHandler(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('u')

    def write(self,obj):
        return RequestHandler.write(self,json_encode(obj))

    def prepare(self):
        url=self.__doc__.strip().split('/')
        if url[0] in ['student','professor','admin']:
            if not self.current_user or lower(self.get_secure_cookie('t'))!=url[0]:
                raise HTTPError(403)

