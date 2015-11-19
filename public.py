# -*- coding: utf-8 -*-
from config import setting
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import hashlib,re,urllib,urllib2,time,json
import functools    #防错机制

def verify_login(func):
    @functools.wraps(func)
    def _deco(self, *args, **kwargs):
        if not self.current_user:
            return self.write_error(402)
        return func(self, *args, **kwargs)
    return _deco


def access_token(func):
    @functools.wraps(func)
    def _doll(self, *args, **kwargs):
        if not self.verify_token():
            return self.write_error(2)
        return func(self, *args, **kwargs)
    return _doll

#售电服务器通信
def api_token(func):
    @functools.wraps(func)
    def _doll(self, *args, **kwargs):
        if not self.server_access():
            return self.write_error(9)
        return func(self, *args, **kwargs)
    return _doll

#售店站点接口验证
def seller_token(func):
    @functools.wraps(func)
    def _doll(self, *args, **kwargs):
        if not self.seller_access():
            return self.write_error(9)
        return func(self, *args, **kwargs)
    return _doll 

#后台权限
def admin_access(func):
    @functools.wraps(func)
    def _deco(self, *args, **kwargs):
        if not self.admin_check():
            return self.write_error(402)
        return func(self, *args, **kwargs)
    return _deco

#前台登录
def user_access(func):
    def _deco(self, *args, **kwargs):
        if not self.user_check():
            return self.write_error(402)
        return func(self, *args, **kwargs)
    return _deco

#站点登录
def seller_login(func):
    def _deco(self, *args, **kwargs):
        if not self.seller_check():
            return self.write_error(402)
        return func(self, *args, **kwargs)
    return _deco


class webHandler(tornado.web.RequestHandler):
    def __init__(self, *argc, **argkw):
        # *argc代表普通类型的传参(1,2,3,4)
        # **argkw代表kv类型的参数{a:1,b:2,c:3}
        super(webHandler, self).__init__(*argc, **argkw)
        
    @property
    def db(self):
        return self.application.db
    
    @property
    def rd(self):       
        return self.application.rd
    
    #sha256加密
    def encrypt(self, key=None):       
        if key:
            return hashlib.sha256( key ).hexdigest()
        else:
            return False
        
    def md5(self, key=None):
        if key:
            return hashlib.md5( key ).hexdigest()
        else:
            return False

    def make_token(self, appid=None, sessionid=None):
        key = self.encrypt(appid+sessionid+str(setting['secretkey']))
        param = self.appid+','+self.sessionid+','+key
        token = base64.b64encode( param )
        return token

    def random_str(self, randomlength=8, model='all'):
        from random import Random
        str = ''
        if model == 'all':
            chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        elif model == 'str':
            chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
        elif model == 'num':
            chars = '0123456789'
        elif model == 'no':
            chars = '123456789'

        length = len(chars) - 1
        random = Random()
        for i in range(randomlength):
            str+=chars[random.randint(0, length)]
        return str

    def get_ip(self):
        return self.request.remote_ip

    #登录验证
    def get_current_user(self):
        openid = self.get_secure_cookie('openid')
        if openid:
            return True
        else:
            return False

    #提示跳转页
    def tips(self,sign=1,notice='',reback='back',mess=''):
        if not reback or reback == 'back':
            reback = 'javascript:history.go(-1)'
        params = urllib.urlencode({'sign':sign, 'notice':notice, 'mess':mess, 'reback':reback}) 
        url = "/tips?%s" %(params)
        self.redirect( url )


    #提示跳转页
    def prompt(self,sign=1,notice='',reback='back',mess=''):
        if not reback or reback == 'back':
            reback = 'javascript:history.go(-1)'
        params = urllib.urlencode({'sign':sign, 'notice':notice, 'mess':mess, 'reback':reback}) 
        url = "/notice?%s" %(params)
        self.redirect( url )


    #token权限验证
    def verify_token(self):
        openid = self.get_secure_cookie('openid')
        if not openid:
            code = self.get_argument('code','')
            status = self.get_argument('status','')
            url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid="+setting['appid']+"&secret="+setting['appsecret']+"&code="+str(code)+"&grant_type=authorization_code"
            respone = self.httplib_get(url)
            if respone.has_key('openid'):
                #存入cookie
                self.set_secure_cookie('openid',str(respone['openid']),expires_days=None)
                #因为cookie第一次访问无法读取，临时存入redis
                self.rd.set('code:'+code, str(respone['openid']))
                self.rd.expire('code:'+code, setting['redisexpire'])
                return True
            else:
                return False
        return True


    #后台登录验证
    def admin_check(self):
        sessionid = self.get_secure_cookie('sessionid')
        if sessionid:
            uinfo = self.rd.hgetall('admininfo:'+str(sessionid))
            if uinfo:
                self.rd.expire('admininfo:'+str(sessionid), setting['redisexpire'])
                return True
        return False

    #前台登录
    def user_check(self):
        session = self.get_secure_cookie('session')
        if session:
            username = self.rd.get('username:'+str(session))
            if username:
                self.rd.expire('username:'+str(session), setting['redisexpire'])
                return True
        return False

    #售电站点登录
    def seller_check(self):
        session = self.get_secure_cookie('seller')
        if session:
            sid = self.rd.get('seller:'+str(session))
            if sid:
                self.rd.expire('seller:'+str(session), setting['redisexpire'])
                return True
        return False


    def httplib_get(self,url=''):
        # header = {'Referer': url, 'Content-Type': 'application/json'}
        # resp = requests.get(url=url, headers=header)
        resp = urllib2.urlopen(url)
        res = json.loads(resp.read())
        return res


    #获取操作秘钥access_token
    def get_access_token(self):
        access_token = self.rd.get('access_token')
        if access_token:
            return access_token
        else:
            url ="https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid="+setting['appid']+"&secret="+setting['appsecret']
            info = self.httplib_get(url)
            if info.has_key('access_token'):
                self.rd.set('access_token',info['access_token'])
                self.rd.expire('access_token',info['expires_in'])
                return info['access_token']
            else:
                return False



    #二维码扫描用函数jsapi_ticket
    def get_signature(self,access_token=''):
        ticket = self.rd.get('ticket')
        if not ticket:
            sql = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token="+str(access_token)+"&type=jsapi"
            info = self.httplib_get(sql)
            if info.has_key('ticket'):
                self.rd.set('ticket',info['ticket'])
                self.rd.expire('ticket',info['expires_in'])
                ticket = info['ticket']
            else:
                return False
        param = {'jsapi_ticket':ticket,'noncestr':self.random_str(16,'str'),'timestamp':int(time.time()),'url':'http://'+str(self.request.host)+str(self.request.uri)}
        sign = self.formatBizQueryParaMap( param, False )
        param['signature'] = hashlib.sha1( sign ).hexdigest()
        param['appid'] = setting['appid']
        param['errcode'] = '0'
        return param


    def formatBizQueryParaMap(self, paraMap, urlencode):
        """格式化参数，签名过程需要使用"""  
        slist = sorted(paraMap)  
        buff = []  
        for k in slist:  
            v = quote(paraMap[k]) if urlencode else paraMap[k]  
            buff.append("{0}={1}".format(k, v))  
        return "&".join(buff)

    #防止sql注入
    def health_param(self,value):
        pattern = re.compile(r'^\w+$')
        health = pattern.match( value )
        return health

    def respone_data(self,result=1,value=''):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        respone = {'res':result,'data':value}
        return json.dumps(respone)

    def respone_list(self,value=[],page={}):
        #列表
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        respone = {'data':value,'page':page}
        return json.dumps(respone)


    def __del__(self):
        self.db.close()


class apiHandler(tornado.web.RequestHandler):
    def __init__(self, *argc, **argkw):
        # *argc代表普通类型的传参(1,2,3,4)
        # **argkw代表kv类型的参数{a:1,b:2,c:3}
        super(apiHandler, self).__init__(*argc, **argkw)
        
    def check_xsrf_cookie(self):
        pass

    @property
    def db(self):
        return self.application.db
    
    @property
    def rd(self):       
        return self.application.rd
    
    #sha256加密
    def encrypt(self, key=None):       
        if key:
            return hashlib.sha256( key ).hexdigest()
        else:
            return False
        
    def md5(self, key=None):
        if key:
            return hashlib.md5( key ).hexdigest()
        else:
            return False

    def random_str(self, randomlength=8, model='all'):
        from random import Random
        str = ''
        if model == 'all':
            chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        elif model == 'str':
            chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
        elif model == 'num':
            chars = '0123456789'
        elif model == 'no':
            chars = '123456789'

        length = len(chars) - 1
        random = Random()
        for i in range(randomlength):
            str+=chars[random.randint(0, length)]
        return str

    def get_ip(self):
        return self.request.remote_ip


    def httplib_get(self,url=''):
        resp = urllib2.urlopen(url)
        res = json.loads(resp.read())
        return res

    def server_access(self):
        token = self.get_argument('token','')
        if token == str( setting['apikey'] ):
            return True
        else:
            return False

    def seller_access(self):
        token = self.get_argument('token','')
        res = self.rd.get('token:'+token)
        if res == 1 or res == '1':
            return True
        else:
            return False

    def respone_data(self,result=1,value=''):
        respone = {'res':result,'data':value}
        return json.dumps(respone)

    def respone_list(self,value=[],page={}):
        #列表
        respone = {'data':value,'page':page}
        return json.dumps(respone)

    def __del__(self):
        self.db.close()