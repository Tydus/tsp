# -*- coding: utf-8 -*-

################################################################################
#                 Graduation Design Subject Double-Choose System               #
#                               Background Components                          #
#                                                                              #
#   Author: Tydus Ken <Tydus@Tydus.org>                                        #
#   Written: June. 2012                                                        #
#                                                                              #
################################################################################

from mongoengine import *

# Users
class User(Document,EmbeddedDocument):
    meta={'allow_inheritance':True}

    username=StringField(required=True)                   # 用户名（学号，工号）
    #username=StringField(required=True,primary_key=True)  # 用户名（学号，工号）
    password=StringField(required=True)                   # 密码
    realname=StringField(required=True)                   # 姓名

class Student(User):
    department=StringField(required=True)                 # 专业
    cls=StringField(required=True)                        # 班级
    cls_index=IntField(required=True)                     # 班内序号

    # Attention: these are a part of circular-reference,
    #            use string to solve the issue
    selected=ReferenceField('Subject')                    # 选择的课题
    applied_to=ReferenceField('Subject')                  # 被选中的课题

    excluded=BooleanField(required=True,default=False)    # 不参与选择

class Professor(User):
    department=StringField(required=True)                 # 单位
    title=StringField(required=True)                      # 职称
    direction=StringField(required=True)                  # 研究方向

class Admin(User):
    pass


# Subject
class Subject(Document,EmbeddedDocument):
    name=StringField(required=True)                          # 课题名
    desc=StringField(required=True)
    type1=StringField(required=True)                         # 分类1
    type2=StringField(required=True)                         # 分类2
    source=StringField(required=True)                        # 题目来源

    professor=EmbeddedDocumentField(Professor,required=True) # 导师
    selected_by=ListField(EmbeddedDocumentField(Student))    # 待选学生
    applied_to=EmbeddedDocumentField(Student)                # 选中学生

# Settings
class Settings(Document):
    phase=IntField(required=True)                            # 系统进行阶段

connect('tsp')
