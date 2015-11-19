# -*- coding: utf-8 -*-
from public import *
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from model.usermodel import *
from model.chargemodel import *
from model.language import lang
import hashlib,commands,time
import xml.etree.ElementTree as ET
from model.socketmodel import SOCKETClient
from config import setting

apimsg = lang()
#首页
class IndexHandler(webHandler):
    @access_token
    def get(self):
    	#获取访问openid
        openid = self.get_secure_cookie('openid')
        if not openid or openid == 'None':
            code = self.get_argument('code','')
            openid = self.rd.get('code:'+code)
            if not openid or openid == 'None':
                #redis依然无法获取openid
                self.write_error(2)
        user = usermodel(self)
        info = user.userbind(openid)
        if info['bind']:
            #已经绑定
            charge = chargemodel(self)
            info['balance'] = charge.getpackage(info['id'])
            card = user.cardinfo(info['id'])
        else:
            #未绑定
            info['balance'] = 0
            card = {'cardtype':0,'cardid':0}
        self.render("wechat/index.html", info=info, card=card)

        
    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)
        

class Clear(webHandler):
    def get(self):
        self.rd.flushdb()


class Test(webHandler):
    def get(self):
        _socket = SOCKETClient(setting['from_address'], setting['from_port'])
        packed_data = _socket.get_data()
        respone = _socket.handle_send( packed_data )
        ip,port = _socket.find_ip( respone )
        print ip,port

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)

class TipsHandler(webHandler):
    def get(self):
        #成功或者失败
        sign = self.get_argument('sign','1')
        notice = self.get_argument('notice','')
        #信息提示
        mess = self.get_argument('mess','')
        #跳转地址
        reback = self.get_argument('reback','')
        self.render("wechat/tips.html", sign=sign, notice=notice, mess=mess, reback=reback)

    def write_error(self, status_code, **kwargs):
        title = 'error'
        self.render("hello.html", title='error')
        

#微信验证
class TokenHandler(webHandler):
    def get(self):    ########验证时用
        #验证token备份
        signature = self.get_argument('signature','')
        timestamp = self.get_argument('timestamp','')
        nonce = self.get_argument('nonce','')
        echostr = self.get_argument('echostr','')
        if self.checksignature(signature, timestamp, nonce):
            self.write(echostr)
        else:
            self.write('fail')

    def post(self): #######简单接收和发送消息
        body = self.request.body
        if body:
            data = ET.fromstring(body)
            tousername = data.find('ToUserName').text
            fromusername = data.find('FromUserName').text
            createtime = data.find('CreateTime').text
            latitude = data.find('Latitude').text
            longitude = data.find('Longitude').text
            precision = data.find('Precision').text
            print 'fromusername: %s' % fromusername
            print 'tousername: %s' % tousername
            print 'createtime: %s' % createtime
            print 'latitude: %s' % latitude
            print 'longitude: %s' % longitude
            print 'precision: %s' % precision
            return
            if content.strip() in ('ls','pwd','w','uptime'):
                result = commands.getoutput(content)
            else:
                result = '不可以哦!!!'
            textTpl = """<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[%s]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                </xml>"""
            out = textTpl % (fromusername, tousername, str(int(time.time())), msgtype, result)
            self.write(out)


    def checksignature(self,signature='', timestamp='', nonce=''):
        args = []
        args.append('mdznbs_com') ####这里输入你的Token
        args.append(timestamp)
        args.append(nonce)
        args.sort()
        mysig = hashlib.sha1(''.join(args)).hexdigest()
        return mysig == signature


    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)


class ShareHandler(webHandler):
    def get(self):
        self.render("wechat/share.html")



class HelloModule(tornado.web.UIModule):
    def render(self):
        return '<h1>Hello, world!</h1>'
    
