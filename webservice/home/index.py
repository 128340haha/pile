# -*- coding: utf-8 -*-
from public import *
from model.cardmodel import *
from model.usermodel import *
from model.chargemodel import *
from model.logmodel import *
from model.language import lang
import time
from model.validate import validate
from config import setting
from libraries.alipay import *

apimsg = lang()
#首页
class IndexHandler(webHandler):
    def get(self):
        #获取访问openid
        self.render("home/index.html")

        
    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("home/error.html", code=status_code, error=error)
        
#关于
class AboutHandler(webHandler):
    def get(self):
    #获取访问openid
        self.render("home/about.html")

        
    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("home/error.html", code=status_code, error=error)

#合作
class PartnerHandler(webHandler):
    def get(self):
    #获取访问openid
        self.render("home/partner.html")

        
    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("home/error.html", code=status_code, error=error)


class CardLogin(webHandler):
    def post(self):
        card = self.get_argument('card','')
        pwd = self.get_argument('pwd','')
        valid = validate()
        valid.Add( card,'卡号', ['NoEmpty'] )
        valid.Add( pwd,'密码', ['NoEmpty'] )
        if not valid._CheckMate():
            #跳转去相关页面
            self.finish('3')
            return
        ca = cardmodel(self)
        res = ca.cardlogin(card,pwd)
        self.finish(res)

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.finish('0')


#用户中心
class UsercenterHandler(webHandler):
    @user_access
    def get(self):
        session = self.get_secure_cookie('session')
        card = cardmodel(self)
        username = card.getusername( session )
        user = usermodel(self)
        uinfo = user.userinfo(username)
        purse = user.userpurse(uinfo['id'])
        uinfo['balance'] = purse['balance'] if purse else 0
        wechat = user.user_wechat(uinfo['id'])
        if wechat and wechat['openid']:
            uinfo['wechat'] = 1
        else:
            uinfo['wechat'] = 0
        card = user.cardinfo(uinfo['id'])
        recharge = user.charge_count( uinfo['id'] )
        self.render("home/usercenter.html",info=uinfo,card=card,charge=recharge)

        
    def write_error(self, status_code, **kwargs):
        if status_code == 402:
            self.redirect('/user')
        else:
            error = apimsg.notice(status_code)
            self.render("home/error.html", code=status_code, error=error)


#ajax获取订单列表
class ChargeList(webHandler):
    @user_access
    def post(self):
        page = self.get_argument('page',1)
        session = self.get_secure_cookie('session')
        card = cardmodel(self)
        username = card.getusername( session )
        user = usermodel(self)
        uinfo = user.userinfo(username)
        charge = chargemodel(self)
        where = {'o.user_id =':int(uinfo['id']),'o.finish >':0}
        clist = charge.chargelist(where,int(page),10)
        if clist:
            #页面信息
            pinfo = charge.page_bar(2)
            reback = {'clist':clist,'pinfo':pinfo}
            self.finish( json.dumps(reback) )
        else:
            self.finish('0')

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.finish('0')


class SaveList(webHandler):
    @user_access
    def post(self):
        page = self.get_argument('page',1)
        session = self.get_secure_cookie('session')
        card = cardmodel(self)
        username = card.getusername( session )
        user = usermodel(self)
        uinfo = user.userinfo(username)
        charge = chargemodel(self)
        where = {'user_id =':int(uinfo['id'])}
        slist = charge.savelist(where,int(page),20)
        if slist:
            #页面信息
            pinfo = charge.page_bar(2)
            reback = {'slist':slist,'pinfo':pinfo}
            self.finish( json.dumps(reback) )
        else:
            self.finish('0')

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.finish('0')


class UpdateInfo(webHandler):
    @user_access
    def post(self):
        card = cardmodel(self)
        session = self.get_secure_cookie('session')
        username = card.getusername( session )
        user = usermodel(self)
        key = self.get_argument('key','')
        val = self.get_argument('val','')
        res = user.editinfo(key,val,username)
        if res == 1:
            self.write('1')
        else:
            self.write( res )

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.finish('0')


class OrderInfo(webHandler):
    @user_access
    def get(self):
        session = self.get_secure_cookie('session')
        card = cardmodel(self)
        username = card.getusername( session )
        user = usermodel(self)
        #用户信息
        uinfo = user.userinfo(username)
        oid = self.get_argument('oid','')
        if id:
            charge = chargemodel(self)
            detail = charge.order_info(oid)
            #验证自己的订单以及
            if detail and detail['user_id'] == int(uinfo['id']):
                self.finish( json.dumps(detail) )
                return
        self.finish( '0' )

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.finish('0')


#支付宝
class UseAlipay(webHandler):
    @user_access
    def get(self):
        session = self.get_secure_cookie('session')
        card = cardmodel(self)
        username = card.getusername( session )
        user = usermodel(self)
        uinfo = user.userinfo(username)
        money = self.get_argument('money','0')
        bank = self.get_argument('bank','alipay') 
        log = logmodel(self)
        if money.isdigit():
            if int(money) > 0: 
                #订单号
                oid = log.build_alipay(2)
                #订单名称
                subject = u'充值'+str( money )+u'元'
                #描述
                body = subject
                #充钱
                total_fee = money
                #写入临时订单表
                try:
                    log.save_alipay( oid, uinfo['id'], total_fee, username+subject, int(time.time()) )
                    log.commit_submit()
                    self.redirect( create_direct_pay_by_user( oid, subject, body, bank, total_fee ) )
                except:
                    self.finish('2')
            else:
                self.finish('1')
        else:
            self.finish('0')

    def write_error(self, status_code, **kwargs):
        self.finish(str(status_code))