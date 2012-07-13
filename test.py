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

Verbose=len(argv)==2 and argv[1]=='-v'

class Error: pass
''' Predicted Error '''

class StatusCode:
    ''' HTTP Status Code '''
    def __init__(self,code):
        self.code=code

testCount=0

class Session(json_rpc.Json_RPC):
    ''' User Session '''
    def test(self,url,description,criteria,file=None,no_json=False,**postData):
        global testCount
        log("%3d: "%(testCount+1),description,'...')
        result,v=self._Go(url,description,criteria,file,no_json,**postData)
        if not result:
            log('fail\n')
            log(v,'\n')
            log('Total of %d tests passed'%testCount)
            exit(-1)
        log('pass\n')
        verbose('    ',v,'\n')
        testCount+=1

    def _Go(self,url,description,criteria,file=None,no_json=False,**postData):
        try:
            method='POST' if file or postData else 'GET'
            if no_json:
                ret=self.http_rpc(UrlPrefix+url,method,data=postData,file=file)
            else:
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

# Reset DB
resetDB()

# Test Script Starts Here

subjectids=[]
def getSubjectIds(x):
    global subjectids
    try:
        subjectids=map(itemgetter('id'),x['subject'])
        return True
    except Exception:
        return False

studentnames=[]
def getAllStudentNames(x):
    global studentnames
    try:
        studentnames=map(itemgetter('username'),x['student'])
        return True
    except Exception:
        return False

selectedstudentnames=[]
def getSelectedStudentNames(x):
    global selectedstudentnames
    try:
        selectedstudentnames=[map(itemgetter('username'),i['selected_by']) for i in x['subject']]
        return True
    except Exception:
        return False

# Phase 0
admin=Session()

admin.test('/announce','Show Announce',{'announce':""})
admin.test('/login','Admin Login',{"role":"Admin"},username='admin',password=passwordHash('admin','admin'))
admin.test('/announce','Set Announce',{},announce='Test<br>Wrap')
admin.test('/profile','Admin profile',lambda r:r['role']=='Admin')
admin.test('/chpasswd','Admin Change Password',{},password=passwordHash('admin','admin'),new_password=passwordHash('admin','test'))
admin.test('/logout','Admin Logout',{},foo='bar')
admin.test('/profile','Admin Profile without Login',StatusCode(403))
admin.test('/announce','Show Announce',{'announce':'Test<br>Wrap'})
admin.test('/login','Admin Login with new Pw',{"role":"Admin"},username='admin',password=passwordHash('admin','test'))
admin.test('/reset','Reset DB without Pw',Error,foo='bar')
admin.test('/reset','Reset DB',{},password=passwordHash('admin','test'))

admin.test('/profile','Admin Profile after Reset DB',StatusCode(403))
admin.test('/login','Admin Login',{"role":"Admin"},username='admin',password=passwordHash('admin','admin'))
admin.test('/phase','Show Phase',{'phase':0})

admin.test('/import','Import Student and Professor',{},file=[('student','student.csv',open('student.csv').read()),('professor','professor.csv',open('professor.csv').read())])

pro1=Session()
pro1.test('/login','Professor Login',{"role":"Professor"},username='1901801001',password=passwordHash('1901801001','1901801001'))
pro1.test('/profile','Professor profile',lambda r:r['role']=='Professor')
pro1.test('/chpasswd','Professor Change Password',{},password=passwordHash('1901801001','1901801001'),new_password=passwordHash('1901801001','test'))
pro1.test('/logout','Professor Logout',{},foo='bar')
pro1.test('/login','Professor Login with new Pw',{"role":"Professor"},username='1901801001',password=passwordHash('1901801001','test'))
pro1.test('/add','Professor Add Subject',lambda x:x.has_key('id'),name='s1',desc='This is subject1\nNewline\n',type1='1',type2='1',source='1')
pro1.test('/add','Professor Add Subject',lambda x:x.has_key('id'),name='中文测试',desc='This is subject2\nNewline\n',type1='2',type2='2',source='1')

pro2=Session()
pro2.test('/login','Professor Login',{"role":"Professor"},username='1901801002',password=passwordHash('1901801002','1901801002'))
pro2.test('/add','Professor Add Subject',lambda x:x.has_key('id'),name='s21',desc='This is subject21\nNewline\n',type1='1',type2='1',source='2')
pro2.test('/add','Professor Add Subject',lambda x:x.has_key('id'),name='s22',desc='This is subject22\nNewline\n',type1='2',type2='1',source='2')

pro3=Session()
pro3.test('/login','Professor Login',{"role":"Professor"},username='1901801003',password=passwordHash('1901801003','1901801003'))
pro3.test('/add','Professor Add Subject',lambda x:x.has_key('id'),name='s31',desc='This is subject31\nNewline\n',type1='2',type2='2',source='2')
pro3.test('/add','Professor Add Subject',lambda x:x.has_key('id'),name='s32',desc='This is subject32\nNewline\n',type1='2',type2='1',source='2')

stu1=Session()
stu1.test('/login','Student Login',{"role":"Student"},username='09212001',password=passwordHash('09212001','09212001'))
pro1.test('/phase','Show Phase',{'phase':0})
stu1.test('/phase','Show Phase',{'phase':0})

stu1.test('/student','Show Student',getAllStudentNames)
stu1.test('/subject','Show Subject',getSubjectIds)
pro2.test('/subject','Show Subject',getSubjectIds)
admin.test('/subject','Show Subject',getSubjectIds)

pro1.test('/modify','Modify Other\'s Subject',Error,id=subjectids[2],name='s21-modified',desc='This is subject21\nModified\n')
pro2.test('/modify','Modify Subject',{},id=subjectids[2],name='s21-modified',desc='This is subject21\nModified\n')
admin.test('/subject','Check Subject Modification',lambda x:x['subject'][2]['name']=='s21-modified')

pro2.test('/resume?student=09212001','Download resume (not exist)',StatusCode(404))
stu1.test('/resume','Upload resume',{},file=[('resume','resume.txt','Test Resume')])
admin.test('/resume?student=09212001','Download resume',lambda x: x=='Test Resume',no_json=True)
stu1.test('/select','Select in phase 0',Error,subject=subjectids[0])

admin.test('/phase','Advance to Phase 1 with no PW',Error,foo='bar')
admin.test('/phase','Advance to Phase 1',{'phase':1},password=passwordHash('admin','admin'))

# Phase 1
stu1.test('/resume','Update resume',{},file=[('resume','resume_new.txt','Test Update')])
admin.test('/resume?student=09212001','Download resume',lambda x: x=='Test Update',no_json=True)
stu1.test('/select','Select',{},subject=subjectids[0])
stu2=Session()
stu2.test('/login','Student Login',{"role":"Student"},username='09212002',password=passwordHash('09212002','09212002'))
stu2.test('/select','Select',{},subject=subjectids[1])
stu2.test('/select','Change Selection',{},subject=subjectids[0])

stu3=Session()
stu3.test('/login','Student Login',{"role":"Student"},username='09212003',password=passwordHash('09212003','09212003'))
stu3.test('/select','Select',{},subject=subjectids[1])
stu1.test('/student','Check Student Selection',lambda x:reduce(lambda c,i:c+bool(i['selected']),x['student'],0)==3)
admin.test('/subject','Show Subject',getSelectedStudentNames)

admin.test('/phase','Advance to Phase 2',{'phase':2},password=passwordHash('admin','admin'))

# Phase 2
stu1.test('/select','Select in phase 2',Error,subject=subjectids[0])
pro2.test('/approve',"Approve other Professor's Subject",Error,subject=subjectids[0],student=selectedstudentnames[0][0])
pro1.test('/approve',"Approve",{},subject=subjectids[0],student=selectedstudentnames[0][0])
admin.test('/subject','Check if Approved',lambda x:x['subject'][0]['applied_to']['username']==selectedstudentnames[0][0])
pro1.test('/approve',"Change Approvement",{},subject=subjectids[0],student=selectedstudentnames[0][1])
stu2.test('/subject','Check if Approvement Changed',lambda x:x['subject'][0]['applied_to']['username']==selectedstudentnames[0][1])
pro2.test('/approve',"Approve None",{},subject=subjectids[1])
pro3.test('/subject','Check None Approvement',lambda x:x['subject'][1]['applied_to']==None)

pro3.test('/subject','Check Selection',lambda x:x['subject'][0]['selected_by'] and x['subject'][1]['selected_by'])
stu1.test('/student',"Check Student's Approvement",lambda x:reduce(lambda c,i:c+bool(i['applied_to']),x['student'],0)==1)
stu1.test('/student','Check Student Selection',lambda x:reduce(lambda c,i:c+bool(i['selected']),x['student'],0)==3)

admin.test('/phase','Advance to Phase 3',{'phase':3},password=passwordHash('admin','admin'))
stu1.test('/student','Check Student Selection Clearation',lambda x:reduce(lambda c,i:c+bool(i['selected']),x['student'],0)==0)
stu2.test('/subject','Check Approvement Clearation',lambda x:reduce(lambda c,i:c+(i['selected_by']!=[]),x['subject'],0)==0)

# Phase 3
pro1.test('/approve',"Approve in phase 3",Error,subject=subjectids[0],student=selectedstudentnames[0][0])
stu2.test('/select','Assigned Student Selecting',Error,subject=subjectids[2])
stu3.test('/select','Select Assigned Subject',Error,subject=subjectids[0])
stu3.test('/select','Select',{},subject=subjectids[2])

admin.test('/phase','Advance to Phase 4',{'phase':4},password=passwordHash('admin','admin'))
admin.test('/subject','Get Selected Students',getSelectedStudentNames)

# Phase 4
pro1.test('/approve','Approve Assigned Subject',Error,subject=subjectids[0],student=None)
pro2.test('/approve','Approve',{},subject=subjectids[2],student=selectedstudentnames[2][0])

admin.test('/phase','Advance to Phase 5',{'phase':5},password=passwordHash('admin','admin'))
stu1.test('/student','Check Student Selection Clearation',lambda x:reduce(lambda c,i:c+bool(i['selected']),x['student'],0)==0)
stu2.test('/subject','Check Approvement Clearation',lambda x:reduce(lambda c,i:c+(i['selected_by']!=[]),x['subject'],0)==0)

# Phase 5
stu1.test('/select','Select in Phase 5',Error,subject=subjectids[0])
pro2.test('/approve','Approve in Phase 5',Error,subject=subjectids[2],student=selectedstudentnames[2][0])

stu2.test('/select','Assigned Student Selecting',Error,subject=subjectids[2])
stu3.test('/select','Select Assigned Subject',Error,subject=subjectids[0])
admin.test('/match','Match Assigned Student',Error,subject=subjectids[2],student=selectedstudentnames[2][0])
admin.test('/match','Match',{},subject=subjectids[3],student=studentnames[4])

admin.test('/phase','Advance to Phase 6',{'phase':6},password=passwordHash('admin','admin'))
stu1.test('/subject','Show Subject',getSubjectIds)
admin.test('/student','Show Student',getAllStudentNames)

# Phase 6
stu1.test('/select','Select in Phase 6',Error,subject=subjectids[0])
pro2.test('/approve','Approve in Phase 6',Error,subject=subjectids[2],student=selectedstudentnames[2][0])
admin.test('/match','Match in Phase 6',Error,subject=subjectids[3],student=studentnames[4])
admin.test('/phase','Advance to Phase 7',Error,password=passwordHash('admin','admin'))

log('\n\nC13s! All of %d Tests Passed!\n'%testCount)
