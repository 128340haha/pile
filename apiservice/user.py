# -*- coding: utf-8 -*-
from apiservice.base import *
from model.validate import validate
from model.usermodel import *

class UserLoginHandler(APIHandler):
    def __init__(self,*argc,**argkw):
        #因为继承了APIHandler，那么如果需要使用初始化函数__init__就必须要继承父类的__init__如当前例子所述
        super(UserLoginHandler, self).__init__(*argc, **argkw)
        self.user = usermodel(*argc, **argkw)
    
    @verify_token
    def post(self):
        username = self.get_argument('username','')
        password = self.get_argument('password','')
        #验证参数
        valid = validate()
        valid.Add( username,'username', ['NoEmpty'] )
        valid.Add( password,'password', ['NoEmpty'] )
        if not valid._CheckMate():
            self.finish( valid._Message(), 0 )
            return
        res = self.user.userlogin(username,password)
        if res == 1:
            info = self.user.userinfo( username, 2 )
            self.finish( info, 1 )
        else:
            self.finish( code=res )
        
    def get(self):
        self.finish( code=400 )
        
    def write_error(self, status_code, **kwargs):
        self.finish( code=status_code )

class UserStatusHandler(APIHandler):
    def get(self):
        self.finish( '遭不住了呀', 1 )
        
    def write_error(self, status_code, **kwargs):
        self.finish( code=status_code )
    