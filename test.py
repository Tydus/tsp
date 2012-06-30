#!/usr/bin/python

from util import passwordHash
import json_rpc

Verbose=True

UrlPrefix='http://localhost:8080'

def log(*args):
    print "".join(args),

def verbose(*args):
    if Verbose:
        print "".join(args),

class Error: pass
''' Predicted Error '''

class Session(json_rpc.Json_RPC):
    def test(self,url,description,criteria,file=None,**postData):
        log(description,'... ')
        result,v=self._Go(url,description,criteria,file,**postData)
        if not result:
            log('fail\n')
            log(v,'\n')
            exit(-1)
        log('pass\n')
        verbose(v,'\n')

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
        except Exception,e:
            return (criteria==Error,"%s: %s"%(str(type(e)),e.message))


admin=Session()
admin.test('/login','Admin Login',{"role":"Admin"},username='admin',password=passwordHash('admin','admin'))
admin.test('/profile','Admin profile',lambda r:r['role']=='Admin')
admin.test('/chpasswd','Admin Change Password',{},password=passwordHash('admin','admin'),new_password=passwordHash('admin','test'))
admin.test('/logout','Admin Logout',{},foo='bar')
admin.test('/profile','Admin Profile without Login',Error)
admin.test('/login','Admin Login with new Pw',{"role":"Admin"},username='admin',password=passwordHash('admin','test'))
admin.test('/reset','Reset DB',{},password=passwordHash('admin','test'))

admin.test('/profile','Admin Profile after Reset DB',Error)
admin.test('/login','Admin Login',{"role":"Admin"},username='admin',password=passwordHash('admin','admin'))
admin.test('/phase','Phase',{'phase':0})
