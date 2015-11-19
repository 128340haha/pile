# -*- coding: utf-8 -*-
from public import *
from model.validate import validate
from model.chargemodel import *
from model.usermodel import *
import time,re,json,struct,urllib
from model.language import lang
from model.socketmodel import SOCKETClient
import asyncore

apimsg = lang()        #文字类

class DepositHandler(webHandler):
    @verify_login
    def get(self):
        openid = self.get_secure_cookie('openid')
        user = usermodel(self)
        info = user.userbind(openid)
        charge = chargemodel(self)
        balance = charge.getpackage(info['id'])
        self.render("wechat/money.html", balance=balance)

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error) 

#支付操作
class ActPay(webHandler):
    def post(self):
        username = self.get_secure_cookie('username')


    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)   


#充电页面
class RechargeHandler(webHandler):
    @verify_login
    def get(self):
        #开启二维码扫描功能
        access_token = self.get_access_token()
        param = self.get_signature( access_token )
        self.render("wechat/charge.html",param=param)    

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)


class ActSelectPile(webHandler):
    @verify_login
    def get(self):
        code = self.get_argument('charge-number','')
        openid = self.get_secure_cookie('openid')
        #openid = 'oXq4LtyH8lET2u6iTuvxnWJGxr68'
        valid = validate()
        valid.Add( code,'设备码', ['NoEmpty','Isdigit','IsLegalAccounts'], 12, 12 )
        if not valid._CheckMate():
            #跳转去相关页面
            self.tips( 0, apimsg.notice(400), 'back', valid._Message() )
            return 
        user = usermodel(self)
        info = user.userbind(openid)
        charge = chargemodel(self)
        res = charge.bind_pile( info['id'], code )
        if res == 1:
            self.redirect('/combo')
        else:
            self.tips( 0, res )


    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)    

#充电套餐选择
class ComboHandler(webHandler):
    @verify_login
    def get(self):
        openid = self.get_secure_cookie('openid')
        #openid = 'oXq4LtyH8lET2u6iTuvxnWJGxr68'
        user = usermodel(self)
        info = user.userbind(openid)
        charge = chargemodel(self)
        balance = charge.getpackage(info['id'])
        code = charge.get_pile(info['id'])
        combos = charge.charge_combos()
        price = charge.newPrice( time.time() )
        if not code:
            self.tips( 0, apimsg.notice(400), '/recharge' )
            return
        if not price:
            self.tips( 0, apimsg.notice(211) )
            return
        self.render("wechat/combo.html", code=code, balance=balance, combos=combos, price=price ) 
            


    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)  


#确认充电
class ActRecharge(webHandler):
    @verify_login
    def post(self):
        openid = self.get_secure_cookie('openid')
        #openid = 'oXq4LtyH8lET2u6iTuvxnWJGxr68'
        user = usermodel(self)
        info = user.userbind(openid)
        card = user.cardinfo(info['id'])
        choose = self.get_argument('choose','') 
        code = self.get_argument('code','') 
        value = self.get_argument(choose+'_input','')
        valid = validate()
        valid.Add( code,'设备码', ['NoEmpty','Isdigit','IsLegalAccounts'], 12, 12 )
        valid.Add( choose,'充值方式', ['NoEmpty'] )
        if not valid._CheckMate():
            #跳转去相关页面
            self.tips( 0, apimsg.notice(400), 'back', valid._Message() )
            return 
        charge = chargemodel(self)
        #钱包余钱
        balance = charge.getpackage(info['id'])

        #验证充值参数
        param = check_value( choose, value, balance )
        if not param:
            self.tips( 0, apimsg.notice(400) )
            return

        if not card:
            self.tips( 0, apimsg.notice(304) )
            return

        price = charge.newPrice( time.time() )
        if not price or price < 0.5:
            self.tips( 0, apimsg.notice(211) )
            return

        #获取电桩状态 待机的话就开工
        status = charge.check_status( code )
        if status > 1:
            self.tips( 0, apimsg.notice(status) )
            return

        #订单唯一性
        only = charge.only_order(info['id'])
        if not only:
            self.tips( 0, apimsg.notice(217) )
            return
        
        thistime = int(time.time())
        
        #写入订单表
        #order = charge.make_order(info['id'],code,thistime)
        #if not order:
        #    self.tips( 0, apimsg.notice(216) )
        #    return

        #电桩设备码
        kind = int(code[0:4]) + 0xC000
        no = int(code[4:])
        #获取访问的地址
        _socket = SOCKETClient(setting['from_address'], setting['from_port'],False)
        packed_data = _socket.get_data(kind,no)
        try:
            respone = _socket.handle_send( packed_data )
        except:
            self.tips( 0, apimsg.notice(219) )
            return
        ip,port = _socket.find_ip( respone )
        if not ip:
            self.tips( 0, apimsg.notice(215) )
            return  

        #发起soket去通知电桩，带上设备码和用户id以及怎么充
        datas = [ 4,param['token'],price*100,card['cardno'],card['cardtype'],card['cardid'],balance*100,param['money']*100,0,param['mini'],0,param['elec']*100,0 ]
        _send = SOCKETClient(ip, port) 

        s = struct.Struct('<BBHIHIIIIHHII')
        packed_data = s.pack(*datas)
        #ns = struct.Struct('%dB' %s.size)
        #new_datas = ns.unpack(packed_data) 
        new_datas = [ord(x) for x in packed_data]
        set_data = _send.set_data(kind,no,0x2,0x1,new_datas)
        try:
            respone = _send.handle_send( set_data )
        except:
            self.tips( 0, apimsg.notice(219) )
            return
    #    print [hex(ord(x)) for x in respone] 
        #异步
        #asyncore.loop()

        if ord(respone[9]) == 0xc4:
            self.tips( 0, apimsg.notice(219) )
        else:    
            params = urllib.urlencode({'thistime':thistime,'choose':choose,'value':value,'code':code}) 
            url = "/charging?%s" %(params)
            self.redirect( url ) 

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)


#电桩用户名提醒
class DeviceNotice(webHandler):
    @verify_login
    def post(self):
        openid = self.get_secure_cookie('openid')
    #    openid = 'oXq4LtyH8lET2u6iTuvxnWJGxr68'
        user = usermodel(self)
        info = user.userbind(openid)
        card = user.cardinfo(info['id'])
        choose = self.get_argument('choose','') 
        code = self.get_argument('code','') 
        value = self.get_argument('value','')
        valid = validate()
        valid.Add( code,'设备码', ['NoEmpty','Isdigit','IsLegalAccounts'], 12, 12 )
        valid.Add( choose,'充值方式', ['NoEmpty'] )
        if not valid._CheckMate():
            #跳转去相关页面
            self.finish('5')
            return 
        charge = chargemodel(self)

        #钱包余钱
        balance = charge.getpackage(info['id'])

        #验证充值参数
        param = check_value( choose, value, balance )
        if not param:
            self.finish('5')
            return
        #没有绑定卡
        if not card:
            self.finish('6')
            return

        price = charge.newPrice( time.time() )
        if not price or price < 0.5:
            self.finish('7')
            return
        #设备状态判断
        status = charge.check_status( code )
        if status == 226:
            self.finish('3')
            return
        elif status == 214:
            self.finish('2')
            return
        elif status == 210:
            self.finish('4')
            return    

        #订单唯一性
        only = charge.only_order(info['id'])
        if not only:
            self.finish('8')
            return

        #电桩设备码
        kind = int(code[0:4]) + 0xC000
        no = int(code[4:])
        #获取访问的地址
        _socket = SOCKETClient(setting['from_address'], setting['from_port'],False)
        packed_data = _socket.get_data(kind,no)
        try:
            respone = _socket.handle_send( packed_data )   
        except:
            self.finish('3')
            return
        ip,port = _socket.find_ip( respone )
        if not ip:
            self.finish('4')
            return

        #发送用户信息通知
        message = str(info['nickname']) if info['nickname'] else str(info['username'])
        doll = message.decode('utf-8').encode('gb2312')
        sendmess = []
        key = len(doll)
        #最多发送12字符
        for x in range(0,12):
            if x < key:
                sendmess.append( ord( doll[x] ) )
            else:
                sendmess.append(0)

        #时间
        nowtime = time.localtime() 
        datas = [ nowtime.tm_sec,nowtime.tm_min,nowtime.tm_hour,nowtime.tm_wday,5,0,0,0,0,0] + sendmess + [0]
        _mess = SOCKETClient(ip, port)
        set_mess = _mess.set_data(kind,no,0x2,0x4,datas)
        try:
            respone = _mess.handle_send( set_mess )   
        except:
            self.finish('3')
            return
        #异步
        #asyncore.loop()
    #    print balance
        #发起soket去通知电桩，带上设备码和用户id以及怎么充
        datas = [ 3,param['token'],price*100,card['cardno'],card['cardtype'],card['cardid'],balance*100,param['money']*100,0,param['mini'],0,param['elec']*100,0 ]
        _send = SOCKETClient(ip, port) 
        #数据流格式
        s = struct.Struct('<BBHIHIIIIHHII')
        packed_data = s.pack(*datas)
        #ns = struct.Struct('%dB' %s.size)
        #new_datas = ns.unpack(packed_data) 
        new_datas = [ord(x) for x in packed_data]
        set_data = _send.set_data(kind,no,0x2,0x1,new_datas)
        try:
            respone = _send.handle_send( set_data )
        except:
            self.finish('3')
            return
    #    print [hex(ord(x)) for x in respone] 
        #异步
        #asyncore.loop()

        if ord(respone[9]) == 0xc4:
            self.finish('3')
        else:
            self.finish('1')

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)


def check_value( choose, value, balance ):
    res = {}
    #按时间计算
    if choose == 'minute':
        res['token'] = 2
        res['money'] = 0
        res['mini'] = int(value)
        res['elec'] = 0
        pattern = re.compile(r'^\d+$')
        match = pattern.match(value)
        if not match:
            return False
    #按电量与钱计算
    elif choose == 'electric':
        res['token'] = 3
        res['money'] = 0
        res['mini'] = 0
        res['elec'] = float(value)
        pattern = re.compile(r'^\d+(\.\d{1})?$')
        match = pattern.match(value)
        if not match:
            return False
    elif choose == 'payment':
        res['token'] = 1
        res['money'] = float(value)
        res['mini'] = 0
        res['elec'] = 0
        pattern = re.compile(r'^\d+(\.\d{1})?$')
        match = pattern.match(value)
        if not match:
            return False
        #钱包
        #此处留白，以后高级会员则可以透支
        if float(balance) < float(value):
            return False
    else:
        res['token'] = 4
        res['money'] = 0
        res['mini'] = 0
        res['elec'] = 0
    return res


#充电通知页
class ChargingHandler(webHandler):
    def get(self):
        thistime = self.get_argument('thistime',0)
        choose = self.get_argument('choose','')
        value = self.get_argument('value','')
        code = self.get_argument('code','')
        self.render("wechat/charging.html",thistime=int(thistime),choose=choose,value=value,code=code)

#停止充电
class StopCharging(webHandler):
    @verify_login
    def post(self):
        code = self.get_argument('code','') 
        openid = self.get_secure_cookie('openid')
    #    openid = 'oXq4Lt-ob9EmU2AITP8Cz6Ur-bac'
        user = usermodel(self)
        info = user.userbind(openid)
        card = user.cardinfo(info['id'])
        charge = chargemodel(self)
        order_info = charge.search_order( code,info['id'] )
        #当前电桩详情
        device_info = charge.device_info( code )
        if device_info and device_info['status'] == 2:
            #订单状态为充电中
            if order_info:
                code = order_info['code']
                kind = int(code[0:4]) + 0xC000
                no = int(code[4:])
                #获取访问的地址
                _socket = SOCKETClient(setting['from_address'], setting['from_port'],False)
                packed_data = _socket.get_data(kind,no)
                respone = _socket.handle_send( packed_data )
                ip,port = _socket.find_ip( respone )
                if not ip:
                    #地址获取失败
                    self.finish('5')
                    return  

                #发起soket去通知电桩 停止充电
                datas = [ card['cardtype'], card['cardid'] ]
                _send = SOCKETClient(ip, port)

                s = struct.Struct('<HI')
                packed_data = s.pack(*datas)
                new_datas = [ord(x) for x in packed_data]
                set_data = _send.set_data(kind,no,0x9,0x0,new_datas)
                try:
                    respone = _send.handle_send( set_data )
                except:
                    #访问超时
                    self.finish('4')
                    return
                
            #    print [hex(ord(x)) for x in respone] 

                if ord(respone[9]) == 0xc4:
                    #离线
                    self.finish('0')
                else:
                    #正常完成
                    self.finish('1')
            else:
                #充电已经完成
                self.finish('2')
        else:
            #电桩非工作中
            self.finish('3')

    def write_error(self, status_code, **kwargs):
        self.finish(status_code)


#充电及时信息
class ChargeSocket(webHandler):
    def post(self):
        code = self.get_argument('code','')
        if code:
            kind = int(code[0:4]) + 0xC000
            no = int(code[4:])
            #获取访问的地址
            _socket = SOCKETClient(setting['from_address'], setting['from_port'],False)
            packed_data = _socket.get_data(kind,no)
            try:
                respone = _socket.handle_send( packed_data )
            except:
                self.finish('3')
                return
            ip,port = _socket.find_ip( respone )
            if not ip:
                #获取地址失败
                self.finish('2')
                return  
            
            #发起soket去通知电桩，带上设备码和用户id以及怎么充
            datas = [ 4,param['token'],price*100,card['cardno'],card['cardtype'],card['cardid'],balance*100,param['money']*100,0,param['mini'],0,param['elec']*100,0 ]
            _send = SOCKETClient(ip, port) 

            s = struct.Struct('<BBHIHIIIIHHII')
            packed_data = s.pack(*datas)
            #ns = struct.Struct('%dB' %s.size)
            #new_datas = ns.unpack(packed_data) 
            new_datas = [ord(x) for x in packed_data]
            set_data = _send.set_data(kind,no,0x2,0x1,new_datas)
            try:
                respone = _send.handle_send( set_data )
            except:
                self.tips( self.finish('4') )
                return
        #    print [hex(ord(x)) for x in respone] 
            #测试数据
            param = {'elec':15,'pay':3.4,'acttime':37}
            self.finish(json.dumps(param))
        else:
            self.finish('0')

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)

#充值记录
class DepositLogHandler(webHandler):
    @verify_login
    def get(self):
        self.render("wechat/deposit.html") 

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)    


#充电记录
class RechargeLogHandler(webHandler):
    @verify_login
    def get(self):
        openid = self.get_secure_cookie('openid')
        #openid = 'oXq4LtyH8lET2u6iTuvxnWJGxr68'
        page = self.get_argument('page',1)
        showtime = self.get_argument('st','1')
        if showtime == '1':
            #一个月内
            creatime = int(time.time()-2592000)
        elif showtime == '2':
            #六个月内
            creatime = int(time.time()-15552000)
        user = usermodel(self)
        #绑定用户信息
        info = user.userbind(openid)
        charge = chargemodel(self)
        #查询条件
        where = {'o.user_id =':int(info['id']),'o.creatime >=':creatime}
        #查询列表
        clist = charge.chargelist(where,int(page),4)
        #页面信息
        if clist:
            page_info = charge.page_bar(2)
            if page_info['all_num'] > page_info['per_page']:
                more = True
            else:
                more = False
        else:
            more = False
            page_info = {'this_page':1,'all_page':0}
        self.render("wechat/recharge.html",clist=clist,st=showtime,more=more,pinfo=page_info)

    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)


#分页获取
class MoreRecharge(webHandler):
    @verify_login
    def post(self):
        page = self.get_argument('page',1)
        openid = self.get_secure_cookie('openid')
        #openid = 'oXq4LtyH8lET2u6iTuvxnWJGxr68'
        showtime = self.get_argument('st','1')
        if showtime == '1':
            #一个月内
            creatime = int(time.time()-2592000)
        elif showtime == '2':
            #六个月内
            creatime = int(time.time()-15552000)
        user = usermodel(self)
        #绑定用户信息
        info = user.userbind(openid)   
        #查询条件
        where = {'o.user_id =':int(info['id']),'o.creatime >=':creatime}
        charge = chargemodel(self)
        #查询列表
        clist = charge.chargelist(where,int(page),4)
        #页面信息
        if clist:
            self.write(json.dumps(clist))
        else:
            self.write(False)


    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)


#订单详情页
class DetailHandler(webHandler):
    @verify_login
    def get(self):
        id = self.get_argument('id','')
        openid = self.get_secure_cookie('openid')
        #openid = 'oXq4LtyH8lET2u6iTuvxnWJGxr68'
        user = usermodel(self)
        info = user.userbind(openid)
        charge = chargemodel(self)
        detail = charge.order_info(id)
        #验证自己的订单以及
        if detail and detail['user_id'] == int(info['id']):
            self.render("wechat/charge_detail.html", detail=detail)
        else:
           self.tips( 0, apimsg.notice(400) )
 
    def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error)