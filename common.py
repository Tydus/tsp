
from tornado.web import RequestHandler,HTTPError
from tornado.escape import json_encode

class JsonRequestHandler(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('u')

    def write(self,obj):
        return RequestHandler.write(self,json_encode(obj))

class StudentRequestHandler(JsonRequestHandler):
    def prepare(self):
        if not self.current_user or self.get_secure_cookie('t')!='Student':
            raise HTTPError(403)

class ProfessorRequestHandler(JsonRequestHandler):
    def prepare(self):
        if not self.current_user or self.get_secure_cookie('t')!='Professor':
            raise HTTPError(403)

class AdminRequestHandler(JsonRequestHandler):
    def prepare(self):
        if not self.current_user or self.get_secure_cookie('t')!='Admin':
            raise HTTPError(403)


def strtime(tm=None):
    return "%04d-%02d-%02d %02d:%02d:%02d"%gmtime(tm or time())[:6]

# Log
LOG_FATAL=0
LOG_ERROR=1
LOG_WARNING=2
LOG_INFO=3
LOG_VERBOSE=4
def log(level,s,*args):
    if level<=verbosity:
        print >>logfd,"[%19s][%d]"%(strtime(),level)+s%tuple(args)
        logfd.flush()

