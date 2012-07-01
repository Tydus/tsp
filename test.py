#!/usr/bin/python

from util import passwordHash,resetDB
import json_rpc
from urllib2 import HTTPError

Verbose=True

UrlPrefix='http://localhost:8080'

def log(*args):
    print "".join(args),

def verbose(*args):
    if Verbose:
        print "".join(args),

class Error: pass
''' Predicted Error '''

class StatusCode:
    ''' HTTP Status Code '''
    def __init__(self,code):
        self.code=code

class Session(json_rpc.Json_RPC):
    def test(self,url,description,criteria,file=None,**postData):
        log(description,'...')
        result,v=self._Go(url,description,criteria,file,**postData)
        if not result:
            log('fail\n')
            log(v,'\n')
            exit(-1)
        log('pass\n')
        verbose('    ',v,'\n')

    def _Go(self,url,description,criteria,file=None,**postData):
        try:
            method='POST' if file or postData else 'GET'
            ret=self.json_rpc(UrlPrefix+url,method,data=postData,file=file)

            if criteria==Error:
                return (ret.has_key('err'),str(ret))
            elif isinstance(criteria,dict):
                return (ret==criteria,str(ret))
            else: # Callable
                return (criteria(ret),str(ret))
        except HTTPError,e:
            return (
                    isinstance(criteria,StatusCode) and criteria.code==e.code,
                    "HTTPError %s"%e.code
                   )

# Reset DB
resetDB()

# Test Script Starts Here
admin=Session()

admin.test('/login','Admin Login',{"role":"Admin"},username='admin',password=passwordHash('admin','admin'))
admin.test('/profile','Admin profile',lambda r:r['role']=='Admin')
admin.test('/chpasswd','Admin Change Password',{},password=passwordHash('admin','admin'),new_password=passwordHash('admin','test'))
admin.test('/logout','Admin Logout',{},foo='bar')
admin.test('/profile','Admin Profile without Login',StatusCode(403))
admin.test('/login','Admin Login with new Pw',{"role":"Admin"},username='admin',password=passwordHash('admin','test'))
admin.test('/reset','Reset DB',{},password=passwordHash('admin','test'))

admin.test('/profile','Admin Profile after Reset DB',StatusCode(403))
admin.test('/login','Admin Login',{"role":"Admin"},username='admin',password=passwordHash('admin','admin'))
admin.test('/phase','Phase',{'phase':0})

admin.test('/import','Import Student',{},type='student',file=[('file','student.csv',open('student.csv').read())])
admin.test('/import','Import Professor',{},type='professor',file=[('file','professor.csv',open('professor.csv').read())])



