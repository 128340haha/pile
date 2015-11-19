# -*- coding: utf-8 -*-
from public import *
from model.validate import validate
from model.cardmodel import *
import time
from config import setting
from model.language import lang
apimsg = lang()        #文字类

class AccessToken(apiHandler):
    def get(self):
        appid = self.get_argument('appid','')
        appkey = self.get_argument('appkey','')
        valid = validate()
        valid.Add( appid,'appid', ['NoEmpty'] )
        valid.Add( appkey,'秘钥', ['NoEmpty'] )
        if not valid._CheckMate():
            #跳转去相关页面
            self.finish(self.respone_data(0,valid._Message()))
            return
        sql = "SELECT id FROM seller WHERE appid = %s AND appkey = %s"
        res = self.db.get( sql, appid, appkey )
        if res:
            #验证通过
            access_token = str(uuid.uuid1())
            #保存验证记录
            self.rd.set('token:'+access_token, 1)
            self.rd.expire('token:'+access_token, setting['redisexpire'])
            self.finish( self.respone_data(1,access_token) )
        else:
            self.finish( self.respone_data(0,apimsg.notice(401)) )


    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.finish('500')