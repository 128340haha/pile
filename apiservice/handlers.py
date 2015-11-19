# -*- coding: utf-8 -*-
from apiservice.base import *
from model.validate import validate
from config import setting

class IndexHandler(APIHandler):
    def get(self):
        info = {'res':1,'info':'welcome to sooall Open platform. version:1.0 author:Shaka Time:2015-05-29'}
    #   valid = validate()
    #   valid.Add( abc,'提示名称abc', ['NoEmpty','IsLegalAccounts'] )
    #   valid.Add( bcd,'我擦', ['IsNumber'] )
    #   if not valid._CheckMate():
    #       print json.dumps(valid._Message(),ensure_ascii=False,indent=2)
        self.finish( info, 1 )
        
    def write_error(self, status_code, **kwargs):
        self.finish( code=status_code )
        #这个错误提示只是在post,get方法的调用能够用上，如果参数传错，无法使用

class AccessTokenHandler(APIHandler):
    def post(self):
        appid = self.get_argument('appid','')
        appsecret = self.get_argument('appsecret','')
        #验证参数
        valid = validate()
        valid.Add( appid,'appid', ['NoEmpty'] )
        valid.Add( appsecret,'appsecret', ['NoEmpty'] )
        if not valid._CheckMate():
            self.finish( valid._Message(), 0 )
            return
        rd = self.rd
        db = self.db
        self.appid = str(appid)
        #先判断redis中是否存在
        live = rd.get(self.appid)
        if live:
            live_info = eval( live )
            if live_info['appsecret'] == appsecret:   
                self.finish( live_info['token'], 1 ) 
            else:
                self.finish( code=9 )
        else:
            info = db.get("select * from api_access where appid = %s",self.appid)
            secret = self.md5(self.appid+str(setting['secretkey']))
            #秘钥验证
            if info and secret == appsecret:
                #验证通过 制作token
                import uuid
                self.sessionid = str(uuid.uuid4())       #相当于sessionid的随机码
                #加密编码
                token = self.make_token( self.appid, self.sessionid )
                #存入redis
                rd.set(self.appid,{'appsecret':secret,'token':token,'sessionid':self.sessionid,'content':info['content']})
                #过期时间
                rd.expire(self.appid,setting['keyexpire'])
                self.finish( token, 1 ) 
            else:
                self.finish( code=9 )
                
    
    def random_str(randomlength=8):
        from random import Random
        str = ''
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        length = len(chars) - 1
        random = Random()
        for i in range(randomlength):
            str+=chars[random.randint(0, length)]
        return str
            
    def write_error(self, status_code, **kwargs):
        self.finish( code=status_code )

        
        
class ErrorHandler(APIHandler):
    def get(self):
        self.finish( code=404 )
    def write_error(self, status_code, **kwargs):
        self.finish( code=status_code )
    '''    if status_code == 404:
            info = {'res':0,'info':'找不到您访问的页面'}
        elif status_code == 500:
            info = {'res':0,'info':'系统出错,请联系管理猿'}
        else:
            info = {'res':0,'info':'未知错误,请联系鹳狸猿'}
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write( json.dumps(info,ensure_ascii=False,indent=2) )
    '''    
        