# -*- coding: utf-8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.web import RequestHandler, HTTPError
import json
import redis
import functools    #防错机制，用装饰的时候使用
import hashlib
import base64
#from model.exceptions import exceptions
from model.language import lang
from config import setting

def verify_token(func):
    @functools.wraps(func)
    def _deco(self, *args, **kwargs):
        if not self.current_user:
            return self.write_error(2)
        return func(self, *args, **kwargs)
    return _deco

class MainHandler(RequestHandler):
    def __init__(self, *argc, **argkw):
        # *argc代表普通类型的传参(1,2,3,4)
        # **argkw代表kv类型的参数{a:1,b:2,c:3}
        super(MainHandler, self).__init__(*argc, **argkw)
    @property
    def db(self):
        return self.application.db
    
    @property
    def rd(self):
        self.r = redis.Redis(host='localhost',port=6379,db=0)
        return self.r
    
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

class APIHandler(MainHandler):
    #验证用户口令是否正确
    def get_current_user(self):
        token = self.get_argument('token','')
        if token:
            try:    #python的坑，无法解析则报错
                param = base64.b64decode(token)
                if param:
                    param_split = param.split(',')
                    if param_split[2] == self.encrypt(param_split[0]+param_split[1]+str(setting['secretkey'])):            
                        return True
            except:
                pass
        return False
    #    return self.get_secure_cookie("username")
    
    def finish(self, data=None, code=None, list=False):
        #跨域使用
        self.set_header("Access-Control-Allow-Origin", "*")
        if code != None :
            chunk = {'res':code}
            if code == 0:
                chunk["message"] = data
            elif code == 1:
                if list:
                    chunk['list'] = data
                else:
                    chunk['data'] = data               
            else:
                apimsg = lang()
                chunk["message"] = apimsg.notice(code)

            self.set_header("Content-Type", "application/json; charset=UTF-8")
            #返回json中文化 
            res = json.dumps(chunk,ensure_ascii=False,indent=2)
        else:
            res = None
        super(APIHandler,self).finish(res)
        #web函数中自带的一些属性
        self.flush(include_footers=True)
        self.request.finish()
        self._log()
        self._finished = True
        self.on_finish()
        
    # 返回数据格式化
    def respone_format(self, data=None, fomat=None ):
        if data == None or fomat == None :
            return False
        else:
            pass
    
    def write_error(self, status_code, **kwargs):
        """Override to implement custom error pages."""
        debug = self.settings.get("debug", False)
        try:
            exc_info = kwargs.pop('exc_info')
            e = exc_info[1]

            if isinstance(e, exceptions.HTTPAPIError):
                pass
            elif isinstance(e, HTTPError):
                e = exceptions.HTTPAPIError(e.status_code)
            else:
                e = exceptions.HTTPAPIError(500)

            exception = "".join([ln for ln in traceback.format_exception(*exc_info)])

            if status_code == 500 and not debug:
                pass

            if debug:
                e.response["exception"] = exception

            self.clear()
            self.set_status(200)  # always return 200 OK for API errors
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.finish(str(e))
        except Exception:
            logging.error(traceback.format_exc())
            return super(APIHandler, self).write_error(status_code, **kwargs)
        