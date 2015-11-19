# -*- coding: utf-8 -*-
from model.language import lang
from config import setting
import uuid,time,datetime,calendar
from model.page import pagemodel

class adminmodel():
    def __init__(self,obj):
        self.obj = obj
        self.apimsg = lang()
        self.data = {}
        self.usepage = pagemodel()

    def _respone(self, code):
        return self.apimsg.notice(code)
    
    #用户登录
    def adminlogin(self,*arg,**argkw):   
        #判断验证码
        error = self.obj.get_secure_cookie('admin_error')
        error = error if error else 0   #三元运算 相当于 error = error ? error : 0
        if int(error) <= 3 :
            #出错3次后再使用验证码
            pass
        else:
            if self.obj.get_secure_cookie('captcha') == argkw['captcha']:
                #验证码通过
                pass
            else:
                return self._respone(206) 
        #用户信息
        info = self.adminmain(argkw['admin']);
        if info:
            ckpwd = self.adminpass(argkw['password'],info['salt'])
            if ckpwd == info['password']:
                #登录成功,将session带入用户信息
                sessionid = str(uuid.uuid4())
                #数据存入redis
                self.rdsave(sessionid)
                #关键session存入cookie
                self.obj.set_secure_cookie('sessionid',sessionid,expires_days=None)
                #清空错误
                self.obj.set_secure_cookie('admin_error','0',expires_days=None)
                return 1
            else:
                error = int(error) + 1
                self.obj.set_secure_cookie('admin_error',str(error),expires_days=None)
                return self._respone(201) 
        else:
            error = int(error) + 1
            self.obj.set_secure_cookie('admin_error',str(error),expires_days=None)
            return self._respone(200) 

    #查库的管理员详情
    def adminmain(self,admin):
        info = self.obj.db.get("SELECT a.*,i.nickname FROM admins AS a LEFT JOIN admin_info AS i ON a.id = i.id WHERE a.admin = %s", admin)
        if info:
            self.data = info
            return info
        else:
            return False

    #管理员信息
    def admininfo(self,sessionid=False):
        if sessionid:
            info = self.obj.rd.hgetall('admininfo:'+sessionid)
            if info:
            	info['nickname'] = info['nickname'] if info['nickname'] and info['nickname'] != 'None' else info['admin']
                return info

        return None


    #管理员密码
    def adminpass(self,pwd='',salt='asdfgh'):
    	key = self.obj.md5(pwd)+self.obj.md5(salt)
        return self.obj.md5(key)


    #数据保存
    def rdsave(self,sessionid):
        self.obj.rd.hmset('admininfo:'+sessionid, self.data) 
        self.obj.rd.expire('admininfo:'+sessionid, setting['redisexpire'])


    #管理员注册
    def newadmin(self,**argkw):
        salt = self.obj.random_str(6,'str').lower()
        reg_time = time.time()
        reg_ip = self.obj.get_ip()
        pwd = self.adminpass( argkw['password'], salt )
        sql = "INSERT INTO admins (admin,password,salt) VALUES ( %s, %s, %s )"
        id = self.obj.db.execute_lastrowid( sql, argkw['admin'], pwd, salt )
        self.obj.db.commit()
        try: 
            sql = "INSERT INTO admin_info ( id ) VALUES(%s)"
            self.obj.db.insert(sql, id)
            sql = "INSERT INTO admin_log ( id ) VALUES( %s )"
            self.obj.db.insert(sql, id)
            self.obj.db.commit()
            self.insert_id = id
            return 1
        except:
            # Rollback in case there is any error
            self.obj.db.execute( "DELETE FROM admins WHERE id = '%s'", id )
            self.obj.db.commit()
            self.obj.db.close()
            return self._respone(500) 
    

    def get_insert_id(self):
        if self.insert_id:
            return self.insert_id
        else:
            return False


    #站点设定
    def server_setting(self):
		setting = self.obj.db.query('SELECT * FROM system_param')
		if setting:
			res = {}
			for c in setting:
				res[c['item']] = c['value']
			return res
		else:
			return None

    #更新站点设置
    def update_setting(self,param):
		try:
			for x in param:
				self.obj.db.execute("UPDATE system_param SET value=%s WHERE item = %s",param[x],x)
			self.obj.db.commit()
			return True
		except:
			# Rollback in case there is any error
			self.obj.db.close()
			return self._respone(307)

    #管理员列表
    def adminlist(self,where,page=1,per_page=15):
        token = "SELECT count(a.id) AS num FROM admins AS a LEFT JOIN admin_info AS i ON a.id = i.id %s"
        doll = self.obj.db.get(token %where)
        if doll['num'] <= 0:
            return None
        self.num = doll['num']
        self.this_page = page
        start = self.usepage.make_page( doll['num'], page, per_page )  
        sql = '''SELECT a.*,i.nickname,i.priv FROM admins AS a 
                 LEFT JOIN admin_info AS i on a.id = i.id
                 %s ORDER BY a.id LIMIT %s, %s'''
        alist = self.obj.db.query( sql %(where,start,per_page) )
        if alist:
            return alist
        else:
            return None

    #更改密码
    def change_pass(self,password,id):
        sql = "UPDATE admin SET password = %s WHERE id = %s"
        try:
            self.obj.db.execute( sql,password,id )
            self.obj.db.commit()
            return True
        except:
            return False

    #改名
    def change_name(self,nickname,id):
        sql = "UPDATE admin_info SET nickname = %s WHERE id = %s"
        try:
            self.obj.db.execute( sql,nickname,id )
            self.obj.db.commit()
            return True
        except:
            return False


    def delete_admin(self,id):
        sql = "DELETE FROM admins WHERE id = %s"
        info = "DELETE FROM admin_info WHERE id = %s"
        try:
            self.obj.db.execute( sql,id )
            self.obj.db.execute( info,id )
            self.obj.db.commit()
            return True
        except:
            return False

    #统计
    def data_statistics(self):
        res = {}
        #用户
        sql = "SELECT count(id) AS num FROM user WHERE status < 2"
        doll = self.obj.db.get(sql)
        res['users'] = doll['num']
        #卡
        sql = "SELECT count(id) AS num FROM card WHERE cardtype != 9003"
        doll = self.obj.db.get(sql)
        res['cards'] = doll['num']
        #微信绑定过的用户
        sql = "SELECT count(id) AS num FROM wechat_user WHERE user_id > 0"
        doll = self.obj.db.get(sql)
        res['wechat'] = doll['num']
        #充电中
        sql = "SELECT count(oid) AS num FROM charge_order WHERE finish = 0"
        doll = self.obj.db.get(sql)
        res['working'] = doll['num']
        #工作中的电桩
        sql = "SELECT count(id) AS num FROM device WHERE status > 0"
        doll = self.obj.db.get(sql)
        res['device'] = doll['num']
        return res

    #总结本月金额支出
    def month_money(self):
        #月初
        d = datetime.date.today().replace(day=1)
        start = int( time.mktime(d.timetuple()) )
        #当月天数
        nowdate = time.localtime()
        number = nowdate.tm_mday + 1
        #订单数
        sql = "SELECT * FROM charge_order WHERE creatime > %s AND finish > 0 ORDER BY creatime"
        paylist = self.obj.db.query(sql,start)
        allpay = 0
        maxpay = 0
        if paylist:
            #运算每日
            pays = {}
            for i in range( 1,number ):
                limit = start + ( i * 86400 )
                pays[i] = 0 
                for x in range(0,len(paylist)):  
                    allpay += paylist[x]['pay']*100
                    if paylist[x]['creatime'] < limit: 
                        pays[i] += paylist[x]['pay']*100
                        paylist[x]['pay'] = 0
                        #paylist.remove(x)
                    else:
                        break;
                if maxpay < pays[i]:
                    maxpay = pays[i]

            return {'pays':pays,'allpay':allpay,'maxpay':maxpay}
        else:
            return {'pays':'','allpay':0,'maxpay':0}
        # time.mktime(time.strptime("%a %b 01 00:00:00 %Y"))



    #最新完成的订单
    def new_orders(self,limit=8):
        sql = "SELECT o.*,u.username FROM charge_order AS o LEFT JOIN user AS u on u.id = o.user_id WHERE o.finish > 0 ORDER BY o.creatime DESC LIMIT %s" %limit
        res = self.obj.db.query(sql)
        if res:
            return res
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