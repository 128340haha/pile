# -*- coding: utf-8 -*-
from model.language import lang
from config import setting
import uuid,time
from model.cardmodel import *
from model.usermodel import *

class logmodel():
    def __init__(self,obj):
        self.obj = obj
        self.apimsg = lang()
        self.doll = 1

    #收支相关日志
    def build_alipay(self,model=2):
        if self.doll > 9 :
            return False
        nowtime = time.strftime('%y%m%d%H')
        now = int(time.time())
        start = now - ( now % 86400 )
        token = "SELECT count(oid) as num FROM log_alipay WHERE acttime >= %s AND acttime <= %s" %(start,now)
        one = self.obj.db.get(token) 
        num = "%05d" % ( one['num'] + self.doll )
        newid = str(model) + nowtime + num
        only = "SELECT oid FROM log_alipay WHERE oid = %s"
        alone = self.obj.db.get(only,newid)
        if alone:
            self.doll = self.doll + 1
            return self.build_alipay(model)
        else:
            return newid


    def log_info(self,table,oid):
        sql = "SELECT l.*,p.balance FROM "+table+" AS l LEFT JOIN user_purse AS p ON l.user_id = p.id WHERE l.oid = %s "
        info = self.obj.db.get( sql, oid )
        if info:
            return info
        else:
            return None


    def expire_alipay(self):
        #过期时间暂定一周
        expire_time = int(time.time()) - 604800
        sql = "DELETE FROM log_alipay WHERE ispay = 0 AND acttime < %s"
        try:
            self.obj.db.execute( sql, expire_time )
            self.obj.db.commit()
            return True
        except:
            return False


##########↓↓↓特殊功能函数↓↓↓################
    #站点注册属性写入
    def newcard_infomation(self,**param):
        nowtime = int(time.time())
        descript = param['sellername']+u',用户'+param['username']+'('+param['nickname']+u')充值'+param['balance']
        try:
            #填写用户名与电话
            self.save_uinfo( param['nickname'], param['phone'], param['user_id'] )
            #冲入初始值
            self.change_purse( param['balance'], param['user_id'] )
            #写入充值订单
            self.save_order( param['oid'], param['user_id'], param['balance'], nowtime, 'point', param['sellername'] )
            #写入收支记录
            self.save_payments( param['oid'], param['sellerid'], param['balance'], param['user_id'], descript, nowtime )
            #修改密码
            if param.has_key('password') and param['password']:
                self.change_pwd( self.obj.md5(param['password']), param['user_id'] )
            #提交
            self.commit_submit()
            return 1
        except:
            return self.apimsg.notice(310)
        
    #填写用户名与电话
    def save_uinfo( self, nickname, phone, user_id ):
        userinfo = "UPDATE user_info SET nickname = %s,phone = %s WHERE id = %s"
        self.obj.db.update( userinfo, nickname, phone, user_id )

    #更改钱数
    def change_purse( self, balance, user_id ):
        purse = "UPDATE user_purse SET balance = %s WHERE id = %s"
        self.obj.db.update( purse, balance, user_id )

    #写入充值订单
    def save_order( self, oid, user_id, balance, nowtime, model, sellername ):
        order = "INSERT INTO purse_order( oid, user_id, increase, acttime, model, depict ) VALUES( %s, %s, %s ,%s ,%s ,%s )"
        self.obj.db.insert( order, oid, user_id, balance, nowtime, model, sellername )

    #写入收支记录
    def save_payments( self, oid, sellerid, balance, user_id, descript, nowtime ):
        payments = "INSERT INTO log_payments( oid, seller, amount, user_id, descript, acttime ) values( %s, %s, %s, %s, %s, %s )"
        self.obj.db.insert( payments, oid, sellerid, balance, user_id, descript, nowtime )

    #支付宝收支记录
    def save_alipay( self, oid, user_id, amount, descript, nowtime ):
        alipay = "INSERT INTO log_alipay( oid, user_id, amount, descript, acttime ) values( %s, %s, %s, %s, %s )"
        self.obj.db.insert( alipay, oid, user_id, amount, descript, nowtime )

    #支付宝设定为支付成功
    def success_alipay( self, oid, nowtime, trade_no ):
        alipay = "UPDATE log_alipay SET ispay = 1, endtime = %s, trade_no = %s WHERE oid = %s"
        self.obj.db.update( alipay, nowtime, trade_no, oid )

    #修改密码
    def change_pwd(self, password, user_id):
        pwd = "UPDATE card SET pwd = %s WHERE user_id = %s"
        self.obj.db.update( pwd, password, user_id )

    #提交sql
    def commit_submit(self):
        self.obj.db.commit()

    def __del__(self):
        self.obj.db.close()