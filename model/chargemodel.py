# -*- coding: utf-8 -*-
from model.language import lang
from config import setting
import time
from model.page import pagemodel

class chargemodel():
    def __init__(self,obj):
        self.obj = obj
        self.apimsg = lang()
        self.uid = False
        self.usepage = pagemodel()
        self.doll = 1

    def _respone(self, code):
        return self.apimsg.notice(code)
    
    #余额
    def getpackage(self, id='0'):
        if id:
            sql = "SELECT balance FROM user_purse WHERE id = %s"
            package = self.obj.db.get( sql, id )
            balance = package['balance'] if hasattr(package, 'balance') else 0
            return balance
        else:
            return 0

    #获取当前电桩信息
    def device_info(self,code=''):
        sql = "SELECT * FROM device WHERE code = %s"
        info = self.obj.db.get( sql, code )
        if info:
            return info
        else:
            return None

    #卡绑定的用户
    def user_card(self,cardno,cardtype,cardid):
        sql = """SELECT u.id,p.balance,p.freeze FROM card as c 
        LEFT JOIN user AS u on c.user_id = u.id
        LEFT JOIN user_purse AS p on u.id = p.id
        WHERE c.cardtype = %s AND c.cardid = %s AND c.cardno = %s """
        info = self.obj.db.get( sql %(cardtype,cardid,cardno) )
        if info:
            self.uid = info['id']
            self.balance = info['balance']
            self.freeze = info['freeze']
            return info
        else:
            return None

    #结算
    def account(self,**argkw):
        if self.uid:
            deposit = float(self.balance) - float(self.freeze) - argkw['pay']
            purse = "UPDATE user_purse SET balance = %s,payed = payed + %s WHERE id = %s " %(deposit,argkw['pay'],self.uid) 
            order = "UPDATE charge_order SET pay = %s,last = %s,electricity = %s,acttime = %s,finish = %s,endtime = %s WHERE code = '%s' AND user_id = %s AND finish = 0 "
            try:
                self.obj.db.execute( purse )
                self.obj.db.execute( order %(argkw['pay'],deposit,argkw['elec'],argkw['acttime'],argkw['finish'],int(time.time()),argkw['code'],self.uid) )
                self.obj.db.commit()
                return True
            except:
                return False      
        

    #保存绑定的电桩信息
    def bind_pile(self, id, code):
        sql = "SELECT * FROM device WHERE code = %s"
        device = self.obj.db.get( sql, code )
        if device and device['isopen'] == 1:
            self.obj.rd.set( 'userid:'+str(id), str(code) )
            self.obj.rd.expire('userid:'+str(id), setting['redisexpire'])
            return 1
        else:
            return self._respone(210) 

    #读取保存的电桩号
    def get_pile(self,id):
        code = self.obj.rd.get( 'userid:'+str(id) )
        self.obj.rd.expire('userid:'+str(id), setting['redisexpire'])
        return code

    #套餐列表
    def charge_combos(self):
        combos = self.obj.db.query( 'SELECT * FROM charge_combo ORDER BY ascno,id' )
        if combos:
            return combos
        else:
            return {}

    #获取最新的电价
    def newPrice(self,nowtime=0):
        nowtime = int(nowtime)
        sql = "SELECT * FROM elec_price WHERE price > 0 AND start < %s ORDER BY start DESC limit 1"
        info = self.obj.db.get( sql, nowtime )
        if info:
            return info['price']
        else:
            return False

    #检查电桩状态
    def check_status(self,code):
        sql = "SELECT status,heart_time FROM device WHERE code = %s"
        info = self.obj.db.get( sql, code )
        if info: 
            if int(time.time()) - info['heart_time'] > 120:
            #心跳超过2分钟未连接，表示为离线
                return 226
            elif info['status'] == 2:
            #状态字2为忙碌
                return 214
            else:
                return 1
        else:
            return 210

    #不能有未完成的订单
    def only_order(self,uid):
        sql = "SELECT count(oid) as num FROM charge_order WHERE user_id = %s AND finish = 0"
        token = self.obj.db.get(sql,uid)
        if token['num'] == 0:
            return True
        else:
            return False

    #订单结算的话 只能有一个未完成的订单
    def once_order(self,uid,code):
        sql = "SELECT count(oid) as num FROM charge_order WHERE user_id = %s AND code = '%s' AND finish = 0"
        token = self.obj.db.get(sql %(uid,code))
        if token['num'] == 1:
            return True
        else:
            return False

    #搜索未完成的最新订单
    def search_order(self,code,uid):
        sql = "SELECT * FROM charge_order WHERE user_id = %s AND code = %s AND finish = 0"
        info = self.obj.db.get(sql,uid,code)
        if info:
            return info
        else:
            return None

    #订单详情
    def order_info(self,oid):
        sql = "SELECT o.*,d.name FROM charge_order as o left join device as d on o.code = d.code WHERE o.oid = %s"
        res = self.obj.db.get(sql,oid)
        if res:
            if res['acttime'] > 60:
                res['hour'] = int( res['acttime'] / 60 )
                res['minute'] = res['acttime'] % 60
            return res
        else:
            return None


    def make_order(self,uid,code,times,price):
        oid = self.build_order(9)
        sql = "INSERT INTO charge_order ( oid, code, user_id, creatime, price ) VALUES( '%s', '%s', %s, %s, %s )"
        try:
            self.obj.db.insert( sql %( oid, code, uid, times, price ) )
            self.obj.db.commit()
            return True
        except:
            return False

    def chargelist(self,where={},page=1,per_page=10): 
        w = ''
        if where:
            for key in where:
                if w:
                    w += ' AND '+str(key)+str(where[key])
                else:
                    w = str(key)+str(where[key])
        else:
            return {}
        token = "SELECT count(o.oid) as num FROM charge_order as o WHERE %s"
        doll = self.obj.db.get(token %w)
        if doll['num'] <= 0:
            return []
        start = self.usepage.make_page( doll['num'], page, per_page )
        sql = "SELECT o.*,if(d.name is null,'',d.name) as name FROM charge_order AS o LEFT JOIN device AS d ON o.code = d.code WHERE %s ORDER BY o.creatime DESC LIMIT %s, %s"
        clist = self.obj.db.query(sql %(w,start,per_page))
        return clist

    #工作列表
    def workinglist(self,where='',page=1,per_page=20):
        w = ''
        if where:
            for key in where:
                if w:
                    w += ' AND '+str(key)+str(where[key])
                else:
                    w = str(key)+str(where[key])
        else:
            return None
        token = "SELECT count(o.oid) as num FROM charge_order as o WHERE %s"
        doll = self.obj.db.get(token %w)
        if doll['num'] <= 0:
            return []
        start = self.usepage.make_page( doll['num'], page, per_page )
        sql = '''SELECT o.*,u.username,if(d.name is null,'',d.name) as name,c.cardno,c.cardtype,c.cardid,p.balance FROM charge_order AS o 
                 LEFT JOIN device AS d ON o.code = d.code 
                 LEFT JOIN user as u ON o.user_id = u.id
                 LEFT JOIN card as c ON o.user_id = c.user_id
                 LEFT JOIN user_purse as p ON o.user_id = p.id
                 WHERE %s ORDER BY o.creatime DESC LIMIT %s, %s'''
        clist = self.obj.db.query(sql %(w,start,per_page))
        return clist


    #删除订单
    def del_recharge(self,id):
        if id:
            sql = "DELETE FROM charge_order WHERE oid = %s"
            try:
                self.obj.db.insert( sql, id )
                self.obj.db.commit()
                return True
            except:
                return False
        else:
            return False


    def build_order(self,model=1):
        if self.doll > 9 :
            return False
        nowtime = time.strftime('%y%m%d%H')
        now = int(time.time())
        start = now - ( now % 86400 )
        token = "SELECT count(oid) as num FROM charge_order WHERE creatime >= %s AND creatime <= %s" %(start,now)
        one = self.obj.db.get(token)
        num = "%05d" % ( one['num'] + self.doll )
        newid = str(model) + nowtime + num
        only = "SELECT oid FROM charge_order WHERE oid = %s"
        alone = self.obj.db.get(only,newid)
        if alone:
            self.doll = self.doll + 1
            return self.build_order(model)
        else:
            return newid


    def savelist(self,where = '1=1',page=1,per_page=10):
        w = ''
        if where:
            for key in where:
                if w:
                    w += ' AND '+str(key)+str(where[key])
                else:
                    w = str(key)+str(where[key])
        else:
            return None
        token = "SELECT count(oid) as num FROM purse_order WHERE %s"
        doll = self.obj.db.get(token %w)
        if doll['num'] <= 0:
            return []
        start = self.usepage.make_page( doll['num'], page, per_page )
        sql = "SELECT * FROM purse_order WHERE %s ORDER BY acttime DESC LIMIT %s, %s"
        slist = self.obj.db.query(sql %(w,start,per_page))
        return slist

    #强制复位
    def error_end(self,oid):
        sql = "UPDATE charge_order SET finish = 2 WHERE oid = %s"
    #   query = "UPDATE device SET status = 1 WHERE code = %s"
        try:
            self.obj.db.execute( sql, oid )
            self.obj.db.commit()
            return True
        except:
            return False

    def page_bar(self,model=1,number=2):
        if model == 1:
            url = self.obj.request.uri
            res = self.usepage.make_bar(url,number);
        elif model == 2:
            res = self.usepage.page_info();
        return res

    def __del__(self):
        self.obj.db.close()
