# -*- coding: utf-8 -*-
from public import *
from model.validate import validate
from model.usermodel import *
from model.chargemodel import *
from model.captcha import *
import time
from config import setting
from model.language import lang
import libraries.geetest as geetest

apimsg = lang()        #文字类
class ValidCode(webHandler):
    def get(self):
        ic = ImageChar(fontColor=(100,211,90))
        ic.randEnglish(4)
        ic.save("JPEG")
        self.set_header('Content-Type','image/jpeg;charset=utf-8')
        captcha=ic.getCaptcha()
        self.set_secure_cookie('captcha',captcha,expires_days=None)
        self.write(ic.getImg())
        
#登录
class LoginHandler(webHandler):
    def get(self):
        error = self.get_secure_cookie('login_error')
        error = error if error else 0   #三元运算 相当于 error = error ? error : 0
        if int(error) <= 3 :
            nocaptcha = True
        else:
            nocaptcha = False
        time = self.random_str(6)
        self.render("wechat/login.html", time=time, nocaptcha=nocaptcha)

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)
        
class ActLogin(webHandler):
    @verify_login
    def post(self):
        username = self.get_argument('username','')
        password = self.get_argument('password','')
        captcha = self.get_argument('captcha','') 
        valid = validate()
        valid.Add( username,'用户名', ['NoEmpty'] )
        valid.Add( password,'密码', ['NoEmpty'] )
        if not valid._CheckMate():
            #跳转去相关页面
            self.tips( 0, apimsg.notice(400), 'back', valid._Message() )
            return 
        user = usermodel(self)
        openid = self.get_secure_cookie('openid')
        res = user.userlogin( username=username,password=password,captcha=captcha,openid=openid )
        if res == 1:
            self.redirect( '/wechat' )
        else:
            self.tips( 0, res )
        
    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error) 
        

#注册
class RegisterHandler(webHandler):
    def get(self):
        gt = geetest.geetest(setting['captcha_id'], setting['private_key'])
        url = ""
        try:
            challenge = gt.geetest_register()
        except:
            challenge = ""
        if len(challenge) == 32:
            url = "http://%s%s&challenge=%s&product=%s" % (setting['BASE_URL'], setting['captcha_id'], challenge, setting['product'])
        self.render("wechat/register.html", url=url)

        
    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)
       
 
class ActRegister(webHandler):
    def post(self):
        username = self.get_argument('username','')
        password = self.get_argument('password','')
        ckpass = self.get_argument('ckpass','')
        challenge = self.get_argument("geetest_challenge",'')
        geevalidate = self.get_argument("geetest_validate",'')
        seccode = self.get_argument("geetest_seccode",'')
        gt = geetest.geetest(setting['captcha_id'], setting['private_key'])
        result = gt.geetest_validate(challenge, geevalidate, seccode)
        if result:
            #验证码验证码通过
            valid = validate()
            valid.Add( username,'用户名', ['NoEmpty','IsLegalAccounts'], 4, 30 )
            valid.Add( password,'密码', ['NoEmpty','IsLegalAccounts'], 6, 30 )
            valid.Same( ckpass, '两次密码' )
            if not valid._CheckMate():
                self.tips( 0, apimsg.notice(400), 'back', valid._Message() )
                return
            user = usermodel(self)
            only = user.userinfo(username,False)
            if not only:
                res = user.register(username=username,password=password)
                if res == 1:  
                    self.tips( 1, apimsg.notice(302), '/login' )
                    return
                    #跳转去登录页面
                else:
                    self.tips( 0, res, '/register' )
                    return
            else:
                self.tips( 0, apimsg.notice(202), '/register' )
                return
        else:
            self.tips( 0, apimsg.notice(206), '/register' )
            return
        

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)


#登出
class ActCancel(webHandler):
    @verify_login
    def get(self):
        openid = self.get_secure_cookie('openid')
        user = usermodel(self)
        res = user.cancel(openid)
        if res:
            self.rd.expire('userbind:'+openid, 0)
            self.tips( 1, apimsg.notice(303), '/wechat' )
        else:
            self.tips( 1, apimsg.notice(212) )
        
    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)
        

#个人中心
class UcenterHandler(webHandler):
    @verify_login
    def get(self):
        openid = self.get_secure_cookie('openid')
        user = usermodel(self)
        info = user.userbind(openid)
        charge = chargemodel(self)
        info['balance'] = charge.getpackage(info['id'])
        self.render("wechat/ucenter.html", info=info )

        
    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)


class ActUinfo(webHandler):
    def post(self):
        openid = self.get_secure_cookie('openid')  
        key = self.get_argument('key','')
        val = self.get_argument('val','')
        user = usermodel(self)
        info = user.userbind(openid)
        res = user.editinfo(key,val,info['username'])
        if res == 1:
            self.write('1')
        else:
            self.write( res )


class ActOnebind(webHandler):
    @verify_login
    def get(self):
        openid = self.get_secure_cookie('openid')
        user = usermodel(self)
        info = user.user_wechats(openid)
        if not info or info['user_id'] == 0:
            res = user.oneBind(openid)
            if res:
                self.tips( 1, apimsg.notice(301), '/wechat' )
            else:
                self.tips( 0, apimsg.notice(213), '/wechat' )
        else:
            self.tips( 0, apimsg.notice(227), '/wechat' )


    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)