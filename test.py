#!/usr/bin/python
# -*- coding: utf-8 -*-


from util import passwordHash,resetDB
import json_rpc
from urllib2 import HTTPError
from operator import itemgetter
from sys import argv
from pprint import pformat

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

            ret_p=pformat(ret)

            if criteria==Error:
                return (ret.has_key('err'),ret_p)
            elif isinstance(criteria,dict):
                return (ret==criteria,ret_p)
            elif isinstance(criteria,StatusCode):
                return (False,ret_p)
            else: # Callable
                return (criteria(ret),ret_p)
        except HTTPError,e:
            return (
                    isinstance(criteria,StatusCode) and criteria.code==e.code,
                    "HTTPError %s"%e.code
                   )



Verbose=len(argv)==2 and argv[1]=='-v'

# Reset DB
resetDB()

# Test Script Starts Here

# Phase 0
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

admin.test('/import','Import Student and Professor',{},file=[('student','student.csv',open('student.csv').read()),('professor','professor.csv',open('professor.csv').read())])

pro1=Session()
pro1.test('/login','Professor Login',{"role":"Professor"},username='1901801001',password=passwordHash('1901801001','1901801001'))
pro1.test('/profile','Professor profile',lambda r:r['role']=='Professor')
pro1.test('/chpasswd','Professor Change Password',{},password=passwordHash('1901801001','1901801001'),new_password=passwordHash('1901801001','test'))
pro1.test('/logout','Professor Logout',{},foo='bar')
pro1.test('/login','Professor Login with new Pw',{"role":"Professor"},username='1901801001',password=passwordHash('1901801001','test'))
pro1.test('/add','Professor Add Subject',{},name='s1',desc='This is subject1\nNewline\n',type1='1',type2='1',source='1')
pro1.test('/add','Professor Add Subject',{},name='中文测试',desc='This is subject2\nNewline\n',type1='2',type2='2',source='1')


pro2=Session()
pro2.test('/login','Professor Login',{"role":"Professor"},username='1901801002',password=passwordHash('1901801002','1901801002'))
pro2.test('/add','Professor Add Subject',{},name='s21',desc='This is subject21\nNewline\n',type1='1',type2='1',source='2')
pro2.test('/add','Professor Add Subject',{},name='s22',desc='This is subject22\nNewline\n',type1='2',type2='1',source='2')

pro3=Session()
pro3.test('/login','Professor Login',{"role":"Professor"},username='1901801003',password=passwordHash('1901801003','1901801003'))
pro3.test('/add','Professor Add Subject',{},name='s31',desc='This is subject31\nNewline\n',type1='2',type2='2',source='2')
pro3.test('/add','Professor Add Subject',{},name='s32',desc='This is subject32\nNewline\n',type1='2',type2='1',source='2')

stu1=Session()
stu1.test('/login','Student Login',{"role":"Student"},username='09212001',password=passwordHash('09212001','09212001'))

subjectids=[]
def getSubjectIds(x):
    global subjectids
    try:
        subjectids=map(itemgetter('id'),x['subject'])
        return True
    except Exception:
        return False

stu1.test('/student','Show Student',lambda x:x.get('student') and x['student'][0].get('username'))
stu1.test('/subject','Show Subject',getSubjectIds)
pro2.test('/subject','Show Subject',getSubjectIds)
admin.test('/subject','Show Subject',getSubjectIds)

stu1.test('/select','Select in phase 0',Error,subject=subjectids[0])

admin.test('/phase','Advance to Phase 1 with no PW',StatusCode(400),foo='bar')
admin.test('/phase','Advance to Phase 1',{'phase':1},foo='bar',password=passwordHash('admin','admin'))

# Phase 1
stu1.test('/select','Select',{},subject=subjectids[0])
stu2=Session()
stu2.test('/login','Student Login',{"role":"Student"},username='09212002',password=passwordHash('09212002','09212002'))
stu2.test('/select','Select',{},subject=subjectids[1])
stu2.test('/select','Change Selection',{},subject=subjectids[0])

stu3=Session()
stu3.test('/login','Student Login',{"role":"Student"},username='09212003',password=passwordHash('09212003','09212003'))
stu3.test('/select','Select',{},subject=subjectids[1])
stu1.test('/student','Check Student Selection',lambda x:reduce(lambda c,i:c+bool(i['selected']),x['student'],0)==3)

studentnames=[]
def getStudentNames(x):
    global studentnames
    try:
        studentnames=[map(itemgetter('username'),i['selected_by']) for i in x['subject']]
        return True
    except Exception:
        return False

admin.test('/subject','Show Subject',getStudentNames)

admin.test('/phase','Advance to Phase 2',{'phase':2},foo='bar',password=passwordHash('admin','admin'))
# Phase 2
stu1.test('/select','Select in phase 2',Error,subject=subjectids[0])
pro2.test('/approve',"Approve other Professor's Subject",Error,subject=subjectids[0],student=studentnames[0][0])
pro1.test('/approve',"Approve",{},subject=subjectids[0],student=studentnames[0][0])
admin.test('/subject','Check if Approved',lambda x:x['subject'][0]['applied_to']['username']==studentnames[0][0])
pro1.test('/approve',"Change Approvement",{},subject=subjectids[0],student=studentnames[0][1])
stu2.test('/subject','Check if Approvement Changed',lambda x:x['subject'][0]['applied_to']['username']==studentnames[0][1])
pro2.test('/approve',"Approve None",{},subject=subjectids[1],student=None)
pro3.test('/subject','Check None Approvement',lambda x:x['subject'][1]['applied_to']==None)

pro3.test('/subject','Check Selection',lambda x:x['subject'][0]['selected_by'] and x['subject'][1]['selected_by'])
stu1.test('/student',"Check Student's Approvement",lambda x:reduce(lambda c,i:c+bool(i['applied_to']),x['student'],0)==1)
stu1.test('/student','Check Student Selection',lambda x:reduce(lambda c,i:c+bool(i['selected']),x['student'],0)==3)

admin.test('/phase','Advance to Phase 3',{'phase':3},foo='bar',password=passwordHash('admin','admin'))
stu1.test('/student','Check Student Selection Clearation',lambda x:reduce(lambda c,i:c+bool(i['selected']),x['student'],0)==0)
stu2.test('/subject','Check Approvement Clearation',lambda x:reduce(lambda c,i:c+(i['selected_by']!=[]),x['subject'],0)==0)
# Phase 3

