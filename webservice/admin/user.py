# -*- coding: utf-8 -*-
from public import *
from model.validate import validate
from model.usermodel import *
from model.chargemodel import *
import time
from config import setting
from model.language import lang

apimsg = lang()        #文字类
#用户列表
class UserListHandler(webHandler):
    @admin_access
    def get(self):
        showtype = self.get_argument('showtype','0')
        username = self.get_argument('username','')
        nickname = self.get_argument('nickname','')
        mail = self.get_argument('mail','')
        phone = self.get_argument('phone','')
        balance = self.get_argument('balance','')
        page = self.get_argument('page',1)
        where = ' where 1=1 '
        if showtype == '1':
            where += " AND u.status = 0"
        elif showtype == '2':
            where += " AND u.status = 1"
        else:
            where += " AND u.status < 2"
        if username:
            where += " AND u.username like '%%"+username+"%%'"
        if nickname:
            where += " AND i.nickname like '%%"+nickname+"%%'"
        if mail:
            where += " AND i.mail = '"+mail+"'"
        if phone:
            where += " AND i.phone = '"+phone+"'"
        if balance:
            where += " AND p.balance > %s " %int(balance)
        user = usermodel(self)
        ulist = user.user_list( where, page, 20 )
        if ulist:
            page_bar = user.page_bar(1)
            pinfo = user.page_bar(2)
        else:
            page_bar = None
            pinfo = {'this_page':1,'all_page':0,'per_page':20}
        search = {'showtype':showtype,'username':username,'nickname':nickname,'mail':mail,'phone':phone,'balance':balance}
        self.render("admin/userlist.html", ulist=ulist, search=search,page_bar=page_bar,pinfo=pinfo )

    def write_error(self, status_code, **kwargs):
        if status_code == 402:
            self.redirect('/admin/login')
        else:
            error = apimsg.notice(status_code)
            self.render("admin/error.html", code=status_code, error=error)


#用户状态改变
class UserStatus(webHandler):
    @admin_access
    def post(self):
        id = self.get_argument('id','')
        value = self.get_argument('val','1')
        user = usermodel(self)
        res = user.change_status( id, value )
        self.finish( res )

#删除用户
class UserDelete(webHandler):
    @admin_access
    def get(self):
        id = self.get_argument('id','')
        user = usermodel(self)
        res = user.user_delete( id )
        if res == 1:
            self.prompt( 1, apimsg.notice(305), self.request.headers['Referer'] )
        else:
            self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)', res )

    def write_error(self, status_code, **kwargs):
        if status_code == 402:
            self.redirect('/admin/login')
        else:
            error = apimsg.notice(status_code)
            self.render("admin/error.html", code=status_code, error=error)

#重置用户
class UserResetHandler(webHandler):
    @admin_access
    def get(self):
        id = self.get_argument('id','')
        user = usermodel(self)
        info = user.trueinfo( '', id )
        referer = self.request.headers['Referer']
        if info:
            self.render("admin/pwdreset.html", info=info,referer=referer )
        else:
            self.prompt( 0, apimsg.notice(400), 'javascript:history.go(-1)' )

    def write_error(self, status_code, **kwargs):
        if status_code == 402:
            self.redirect('/admin/login')
        else:
            error = apimsg.notice(status_code)
            self.render("admin/error.html", code=status_code, error=error)

#重置密码操作
class ActReset(webHandler):
    @admin_access
    def post(self):
        id = self.get_argument('id','')
        password = self.get_argument('password','')
        referer = self.get_argument('referer','')
        valid = validate()
        valid.Add( id,'id', ['NoEmpty'] )
        valid.Add( password,'密码', ['NoEmpty'], 6, 30 )
        if not valid._CheckMate():
            self.prompt( 0, apimsg.notice(400), 'javascript:history.go(-1)', valid._Message() )
            return
        user = usermodel(self)
        res = user.pass_reset( id, password )
        if res == 1:
            self.prompt( 1, apimsg.notice(305), referer )
        else:
            self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)', res )

    def write_error(self, status_code, **kwargs):
        if status_code == 402:
            self.redirect('/admin/login')
        else:
            error = apimsg.notice(status_code)
            self.render("admin/error.html", code=status_code, error=error)


#用户详情页
class UserDetailsHandler(webHandler):
    @admin_access
    def get(self):
        id = self.get_argument('id','')
        if id:
            user = usermodel(self)
            info = user.trueinfo( '', id )
            card = user.cardinfo(id)
            purse = user.userpurse(id)
            wechat = user.user_wechat(id)
            if wechat:
                card['wechat'] = True
            else:
                card['wechat'] = False
            self.render("admin/userdetails.html", info=info, card=card, purse=purse)
        else:
            self.prompt( 0, apimsg.notice(400), 'javascript:history.go(-1)' )


    def write_error(self, status_code, **kwargs):
        if status_code == 402:
            self.redirect('/admin/login')
        else:
            error = apimsg.notice(status_code)
            self.render("admin/error.html", code=status_code, error=error)

#ajax更改属性
class ActProperty(webHandler):
    @admin_access
    def post(self):
        id = self.get_argument('id','')
        if id:
            model = self.get_argument('model','')
            user = usermodel(self)
            if model == '1':
                nickname = self.get_argument('nickname','')
                mail = self.get_argument('mail','')
                phone = self.get_argument('phone','')
                sex = self.get_argument('sex','')
                idcard = self.get_argument('idcard','')
                res = user.uinfo_edit(id=id,nickname=nickname,mail=mail,phone=phone,sex=sex,idcard=idcard)
            elif model == '2':
                balance = self.get_argument('balance','')
                res = user.purse_edit(id=id,balance=balance)
            #写入日志文件
            #if res == '1':
            self.finish(res)
        else:
            self.finish('0')

#新用户
class AddUserHandler(webHandler):
    @admin_access
    def get(self):
        self.render("admin/adduser.html")

    def write_error(self, status_code, **kwargs):
        if status_code == 402:
            self.redirect('/admin/login')
        else:
            error = apimsg.notice(status_code)
            self.render("admin/error.html", code=status_code, error=error)

#添加新用户
class ActNewUser(webHandler):
    @admin_access
    def post(self):
        username = self.get_argument('username','')
        password = self.get_argument('password','')
        ckpass = self.get_argument('ckpass','')
        valid = validate()
        valid.Add( username,'用户名', ['NoEmpty','IsLegalAccounts'], 4, 30 )
        valid.Add( password,'密码', ['NoEmpty','IsLegalAccounts'], 6, 30 )
        valid.Same( ckpass, '两次密码' )
        if not valid._CheckMate():
            self.prompt( 0, apimsg.notice(400), 'back', valid._Message() )
            return
        user = usermodel(self)
        only = user.userinfo(username,False)
        if not only:
            res = user.register(username=username,password=password)
            if res == 1:  
                self.prompt( 1, apimsg.notice(302), '/admin/user_list' )
                return
                #跳转去登录页面
            else:
                self.prompt( 0, res, 'javascript:history.go(-1)' )
                return
        else:
            self.prompt( 0, apimsg.notice(202), 'javascript:history.go(-1)' )
            return

    def write_error(self, status_code, **kwargs):
        if status_code == 402:
            self.redirect('/admin/login')
        else:
            error = apimsg.notice(status_code)
            self.render("admin/error.html", code=status_code, error=error)
        
#充电列表
class RechargeHandler(webHandler):
    @admin_access
    def get(self):
        id = self.get_argument('id','')
        page = self.get_argument('page',1)
        start = self.get_argument('start','')
        end = self.get_argument('end','')
        user = usermodel(self)
        #绑定用户信息
    #    print id
    #    return
        info = user.trueinfo( '', id )
        charge = chargemodel(self)
        #查询条件
        where = {'o.user_id =':int(info['id'])}
        if start:
            st = time.mktime(time.strptime(start,'%Y-%m-%d'))
            where['o.creatime >='] = st
        if end:
            en = time.mktime(time.strptime(end,'%Y-%m-%d'))
            where['o.creatime <='] = en
        #查询列表
        clist = charge.chargelist(where,int(page),20)
        #页面信息
        if clist:
            page_bar = charge.page_bar(1)
            pinfo = charge.page_bar(2)
        else:
            page_bar = None
            pinfo = {'this_page':1,'all_page':0,'per_page':20}
        search = {'start':start,'end':end}
        self.render("admin/rechargelist.html",id=id,clist=clist,page_bar=page_bar,pinfo=pinfo,search=search)


    def write_error(self, status_code, **kwargs):
        if status_code == 402:
            self.redirect('/admin/login')
        else:
            error = apimsg.notice(status_code)
            self.render("admin/error.html", code=status_code, error=error)

#删除
class ActDelRecharge(webHandler):
    @admin_access
    def get(self):
        id = self.get_argument('id','')
        charge = chargemodel(self)
        res = charge.del_recharge(id)
        if res == 1:
            self.prompt( 1, apimsg.notice(305), self.request.headers['Referer'] )
        else:
            self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)', res )


#充值列表
class DepositHandler(webHandler):
    @admin_access
    def get(self):
        pass


#工作中的订单
class WorkOrderHandler(webHandler):
    @admin_access
    def get(self):
        page = self.get_argument('page',1)
        where = {'o.finish =':0}
        charge = chargemodel(self)
        clist = charge.workinglist(where,int(page),20)
        if clist:
            page_bar = charge.page_bar(1)
            pinfo = charge.page_bar(2)
        else:
            page_bar = None
            pinfo = {'this_page':1,'all_page':0,'per_page':20}
        self.render("admin/recharging.html",clist=clist,page_bar=page_bar,pinfo=pinfo)

    def write_error(self, status_code, **kwargs):
        if status_code == 402:
            self.redirect('/admin/login')
        else:
            error = apimsg.notice(status_code)
            self.render("admin/error.html", code=status_code, error=error)

#回收站
class RecycleHandler(webHandler):
    @admin_access
    def get(self):
        page = self.get_argument('page',1)
        username = self.get_argument('username','')
        where = ' where u.status = 2 '
        if username:
            where += " AND u.username like '%%"+username+"%%'"
        user = usermodel(self)
        ulist = user.user_list( where, page, 20 )
        if ulist:
            page_bar = user.page_bar(1)
            pinfo = user.page_bar(2)
        else:
            page_bar = None
            pinfo = {'this_page':1,'all_page':0,'per_page':20}
        search = {'username':username}
        self.render("admin/recycle.html", ulist=ulist, search=search,page_bar=page_bar,pinfo=pinfo )

    def write_error(self, status_code, **kwargs):
        if status_code == 402:
            self.redirect('/admin/login')
        else:
            error = apimsg.notice(status_code)
            self.render("admin/error.html", code=status_code, error=error)



class KillLive(webHandler):
    @admin_access
    def get(self):
        model = self.get_argument('model','')
        id = self.get_argument('id','')
        user = usermodel(self)
        if id:
            if model == '1':
                res = user.user_live( id )
            elif model == '2':
                res = user.user_kill( id )
            if res:
                self.prompt( 1, apimsg.notice(305), self.request.headers['Referer'] )
                return
        self.prompt( 0, apimsg.notice(307), self.request.headers['Referer'] )  

    def write_error(self, status_code, **kwargs):
        if status_code == 402:
            self.redirect('/admin/login')
        else:
            error = apimsg.notice(status_code)
            self.render("admin/error.html", code=status_code, error=error)

#强制结束订单
class OrderEnd(webHandler):
    @admin_access
    def get(self):
        oid = self.get_argument('oid','')
        if oid:
            charge = chargemodel(self)
            info = charge.order_info(oid)
            if info and info['finish'] == 0:
                res = charge.error_end( oid )
                if res:
                    #写入日志
                    self.prompt( 1, apimsg.notice(305), self.request.headers['Referer'] )
                else:
                    self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)' )
            else:
                self.prompt( 0, apimsg.notice(223), 'javascript:history.go(-1)' )
        else:
            self.prompt( 0, apimsg.notice(400), 'javascript:history.go(-1)' )

    def write_error(self, status_code, **kwargs):
        if status_code == 402:
            self.redirect('/admin/login')
        else:
            error = apimsg.notice(status_code)
            self.render("admin/error.html", code=status_code, error=error)
