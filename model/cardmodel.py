# -*- coding: utf-8 -*-
from model.language import lang
from config import setting
import time,uuid,hashlib
from model.page import pagemodel

class cardmodel():
    def __init__(self,obj):
        self.obj = obj
        self.apimsg = lang()
        self.usepage = pagemodel()

    def _respone(self, code):
        return self.apimsg.notice(code)

    #卡片列表
    def card_list(self,where = '',page=1,per_page=15):
        token = "SELECT count(c.id) AS num FROM card AS c LEFT JOIN user AS u ON u.id = c.user_id %s"
        doll = self.obj.db.get(token %where)
        if doll['num'] <= 0:
            return None
        self.num = doll['num']
        self.this_page = page
        start = self.usepage.make_page( doll['num'], page, per_page )  
        sql = '''SELECT u.username,u.reg_time,c.*,i.idcard,i.phone,p.balance,p.payed FROM card AS c 
                 LEFT JOIN user AS u ON u.id = c.user_id  
                 LEFT JOIN user_info AS i on u.id = i.id
                 LEFT JOIN user_purse AS p ON u.id = p.id
                 %s ORDER BY u.reg_time DESC LIMIT %s, %s'''
        clist = self.obj.db.query( sql %(where,start,per_page) )
        if clist:
            return clist
        else:
            return None

    #检查流水号是否记录
    def show_card(self,cardno):
        sql = "SELECT * FROM card WHERE cardno = %s"
        card = self.obj.db.get( sql, cardno )
        if card:
            return card
        else:
            return None


    #开白卡
    def blank_card(self,cardno):
        cardtype = 9002
        cr = "SELECT max(cardid) AS num FROM card WHERE cardtype = %s"
        card = self.obj.db.get( cr, cardtype )
        num = card['num'] + 1 if card else 0
        sql = "INSERT INTO card ( cardno, cardid, cardtype, user_id ) VALUES( %s, %s, %s, 0 )"
        try: 
            self.obj.db.insert(sql, cardno, num, cardtype )
            self.obj.db.commit()
            cardinfo = {'cardno':cardno,'cardtype':cardtype,'cardid':num}
            return cardinfo
        except:
            return None


    #卡的分类
    def card_type(self):
        sql = "SELECT * FROM card_type ORDER BY ascno"
        res = self.obj.db.query( sql )
        if res:
            return res
        else:
            return None


    #唯一识别码
    def only_cardno(self,cardno):
        sql = "SELECT count(id) AS num FROM card WHERE cardno = %s"
        res = self.obj.db.get( sql, cardno )
        if res and res['num'] > 0:
            return False
        else:
            return True

    #分类详情
    def typeinfo(self,id):
        sql = "SELECT * FROM card_type WHERE id = %s"
        res = self.obj.db.get( sql, id )
        if res:
            return res
        else:
            return None


    #唯一分类
    def only_cardtype(self,cardtype,id=''):
        if id:
            sql = "SELECT count(id) AS num FROM card_type WHERE cardtype = %s AND id != %s" %(cardtype,id)
        else:
            sql = "SELECT count(id) AS num FROM card_type WHERE cardtype = %s" %cardtype
        res = self.obj.db.get( sql )
        if res and res['num'] > 0:
            return False
        else:
            return True


    #分类添加
    def addtype(self,cardtype,typename,ascno):
        sql = "INSERT INTO card_type( cardtype,typename,ascno ) VALUES( %s, %s, %s )"
        try:
            self.obj.db.insert( sql,cardtype,typename,ascno )
            self.obj.db.commit()
            return True
        except:
            return False

    #更改
    def change_type(self,sett,where):
        sql = "UPDATE card_type SET %s WHERE %s"
        try:
            self.obj.db.execute( sql %(sett,where) )
            self.obj.db.commit()
            return True
        except:
            return False


    def editinfo(self,key,value,id):
        sql = "UPDATE card SET "+key+"=%s WHERE user_id = %s"
        try:
            self.obj.db.execute( sql, value, id )
            self.obj.db.commit()
            return True
        except:
            return False


    #删除
    def delete_type(self,id):
        sql = "DELETE FROM card_type WHERE id = %s"
        try:
            self.obj.db.execute( sql,id )
            self.obj.db.commit()
            return True
        except:
            return False


    def delete_card(self,id):
        sql = "DELETE FROM card WHERE id = %s"
        try:
            self.obj.db.execute( sql,id )
            self.obj.db.commit()
            return True
        except:
            return False

    #查询
    def card_infomation(self,where=''):
        if where:
            sql = '''SELECT i.nickname,u.reg_time,u.status,c.cardno,c.cardid,c.cardtype,c.user_id,i.phone,p.balance FROM card AS c 
                     LEFT JOIN user AS u ON u.id = c.user_id  
                     LEFT JOIN user_info AS i on u.id = i.id
                     LEFT JOIN user_purse AS p ON u.id = p.id
                     %s '''
            info = self.obj.db.get( sql %(where) )
            if info:
                return info
        return {}


    def cardlogin(self,card,pwd):
        cardtype = int(card[0:4])
        cardid = int(card[4:])
        sql = '''SELECT c.*,i.phone,u.username FROM card AS c 
                 LEFT JOIN user_info AS i ON c.user_id = i.id 
                 LEFT JOIN user AS u ON c.user_id = u.id
                 WHERE c.cardtype = %s AND c.cardid = %s
              '''
        card = self.obj.db.get( sql, cardtype, cardid )
        if not card:
            return '2'
        elif not card['pwd']:
            if not card['phone']:
                return '4'
            elif card['phone'] == pwd:
                self.saveuser(card['username'])
                return '1'
            else:
                return '0'
        elif card['pwd'] == self.obj.md5(pwd):
            self.saveuser(card['username'])
            return '1'
        else:
            return '5'


    def saveuser(self,username):
        if username:
            session = str(uuid.uuid4())
            self.obj.rd.set('username:'+session, username)
            self.obj.rd.expire('username:'+session, setting['redisexpire'])
            self.obj.set_secure_cookie('session',session,expires_days=None)


    def getusername(self,session):
        if session:
            username = self.obj.rd.get('username:'+session)
            if username:
                return username
        return None


    def getsellers(self,where='',page=1,per_page=15):
        token = "SELECT count(id) AS num FROM seller %s"
        doll = self.obj.db.get(token %where)
        if doll['num'] <= 0:
            return None
        self.num = doll['num']
        self.this_page = page
        start = self.usepage.make_page( doll['num'], page, per_page )  
        sql = "SELECT * FROM seller %s ORDER BY id DESC LIMIT %s, %s"
        slist = self.obj.db.query( sql %(where,start,per_page) )
        if slist:
            return slist
        else:
            return None


    def change_sell_status(self,id,value):
        sql = "UPDATE seller SET status = %s WHERE id = %s"
        try:
            self.obj.db.execute( sql, value, id )
            self.obj.db.commit()
            return '1'
        except:
            return self._respone(307)


    def change_duty(self,value,id):
        sql = "UPDATE seller SET duty = %s WHERE id = %s"
        try:
            self.obj.db.execute( sql, value, id )
            self.obj.db.commit()
            return '1'
        except:
            return self._respone(307)


    def delete_seller(self,id):
        sql = "DELETE FROM seller WHERE id = %s"
        try:
            self.obj.db.execute( sql,id )
            self.obj.db.commit()
            return True
        except:
            return False

    def sellerinfo(self,id):
        sql = "SELECT * FROM seller WHERE id = %s"
        res = self.obj.db.get( sql, id )
        if res:
            return res
        else:
            return None

    def addseller(self,sellername,phone,appid,appkey,status,duty):
        sql = "INSERT INTO seller( sellername,phone,appid,appkey,status,duty ) VALUES( %s, %s, %s, %s, %s, %s )"
        try:
            self.obj.db.insert( sql,sellername,phone,appid,appkey,status,duty )
            self.obj.db.commit()
            return True
        except:
            return False

    def editseller(self,sett,where):
        sql = "UPDATE seller SET %s WHERE %s"
        try:
            self.obj.db.execute( sql %(sett,where) )
            self.obj.db.commit()
            return True
        except:
            return False


    def sellerlogin(self,username,password):
        #查询seller数据
        sql = "SELECT id,appkey,status FROM seller WHERE appid = %s"
        info = self.obj.db.get( sql, username )
        if info and info['status'] == 1:
            password = hashlib.sha1( password ).hexdigest()
            if password == info['appkey']:
                session = str(uuid.uuid1())
                #关键session存入cookie
                self.obj.rd.set('seller:'+session, info['id'])
                self.obj.rd.expire('seller:'+session, setting['redisexpire'])
                self.obj.set_secure_cookie('seller',session,expires_days=None)
                return '1'
            else:
                #密码错误
                return '4'
        else:
            #用户名不存在或者禁用
            return '3'

    #redis获取id
    def get_seller_id(self,session):
        sid = self.obj.rd.get('seller:'+session)
        return sid


    def seller_records(self,where='',page=1,per_page=15):
        if not where:
            return None
        token = "SELECT count(oid) AS num FROM log_payments %s"
        doll = self.obj.db.get(token %where)
        if doll['num'] <= 0:
            return None
        self.num = doll['num']
        self.this_page = page
        start = self.usepage.make_page( doll['num'], page, per_page )  
        sql = "SELECT * FROM log_payments %s ORDER BY acttime DESC LIMIT %s, %s"
        slist = self.obj.db.query( sql %(where,start,per_page) )
        if slist:
            return slist
        else:
            return None

    def page_bar(self,model=1,number=2):
        if model == 1:
            url = self.obj.request.uri
            res = self.usepage.make_bar(url,number);
        elif model == 2:
            res = self.usepage.page_info();
        return res

    def __del__(self):
        self.obj.db.close()