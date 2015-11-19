# -*- coding: utf-8 -*-
from model.language import lang
from model.page import pagemodel
from config import setting
import uuid,time,datetime

class usermodel():
    def __init__(self,obj):
        self.obj = obj
        self.apimsg = lang()
        self.usepage = pagemodel()
        self.data = {}
        self.doll = 1
        self.insert_id = None

    def _respone(self, code):
        return self.apimsg.notice(code)
    
    #用户登录
    def userlogin(self,*arg,**argkw):   #*arg是吧外面传进来的所有 a,b,c此类的参数集合成arg这个元组,而a=a,b=b这样的则放入**argkw这样的集合
        #判断验证码
        error = self.obj.get_secure_cookie('login_error')
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
        info = self.trueinfo(argkw['username']);
        if info:
            if info['status'] == 1:
                ckpwd = self.make_pass(argkw['password'],info['salt'])
                if ckpwd == info['password']:
                    #登录成功,将session带入用户信息
                #    sessionid = str(uuid.uuid4())
                    openid = self.obj.get_secure_cookie('openid')
                    res = self.flush_bind(info['id'],openid)
                    if res == 1:
                        #数据不存redis
                    #   self.rdsave(argkw['username'])
                        #存入redis
                        self.obj.rd.set('userbind:'+argkw['openid'], argkw['username'])
                        self.obj.rd.expire('userbind:'+argkw['openid'], setting['redisexpire'])
                    #   self.obj.set_secure_cookie('sessionid',sessionid,expires_days=None)
                        #清空错误
                        self.obj.set_secure_cookie('login_error','0',expires_days=None)
                        return 1
                    else:
                        return res
                else:
                    error = int(error) + 1
                    self.obj.set_secure_cookie('login_error',str(error),expires_days=None)
                    return self._respone(201) 
            else:
                return self._respone(205) 
        else:
            error = int(error) + 1
            self.obj.set_secure_cookie('login_error',str(error),expires_days=None)
            return self._respone(200) 
    
    
    #用户注册
    def register(self,**argkw):
        salt = self.obj.random_str(6,'str').lower()
        reg_time = time.time()
        reg_ip = self.obj.get_ip()
        pwd = self.make_pass( argkw['password'], salt )
        #分类
        cardtype = argkw['cardtype'] if argkw.has_key('cardtype') else 9003
        #识别码
        cardno = argkw['cardno'] if argkw.has_key('cardno') else 0
        #新卡号
        if argkw.has_key('cardid'):
            num = argkw['cardid']
        elif cardtype == 9003:
            cr = "SELECT max(cardid) AS num FROM card WHERE cardtype = %s"
            card = self.obj.db.get( cr, cardtype )
            num = card['num'] + 1 if card else 0
        else:
            return self._respone(304)
        sql = "INSERT INTO user (username,password,salt,reg_time,reg_ip) VALUES ( %s, %s, %s, %s, %s )"
        id = self.obj.db.execute_lastrowid( sql, argkw['username'], pwd, salt, reg_time, reg_ip)
        self.obj.db.commit()
        try: 
            sql = "INSERT INTO user_face ( id ) VALUES(%s)"
            self.obj.db.insert(sql, id)
            sql = "INSERT INTO user_info ( id ) VALUES(%s)"
            self.obj.db.insert(sql, id)
            sql = "INSERT INTO user_purse ( id, balance ) VALUES( %s, 0 )"
            self.obj.db.insert(sql, id)
            sql = "INSERT INTO card ( cardno, cardid, cardtype, user_id ) VALUES( %s, %s, %s, %s )"
            self.obj.db.insert(sql, cardno, num, cardtype, id )
            self.obj.db.commit()
            self.insert_id = id
            return 1
        except:
            # Rollback in case there is any error
            self.obj.db.execute( "DELETE FROM user WHERE id = '%s'", id )
            self.obj.db.commit()
            self.obj.db.close()
            return self._respone(500) 
    
    #绑定现有卡
    def bind_card( self,**argkw ):
        salt = self.obj.random_str(6,'str').lower()
        reg_time = time.time()
        reg_ip = self.obj.get_ip()
        pwd = self.make_pass( argkw['password'], salt )
        sql = "INSERT INTO user (username,password,salt,reg_time,reg_ip) VALUES ( %s, %s, %s, %s, %s )"
        id = self.obj.db.execute_lastrowid( sql, argkw['username'], pwd, salt, reg_time, reg_ip)
        self.obj.db.commit()
        try: 
            sql = "INSERT INTO user_face ( id ) VALUES(%s)"
            self.obj.db.insert(sql, id)
            sql = "INSERT INTO user_info ( id ) VALUES(%s)"
            self.obj.db.insert(sql, id)
            sql = "INSERT INTO user_purse ( id, balance ) VALUES( %s, 0 )"
            self.obj.db.insert(sql, id)
            sql = "UPDATE card SET user_id = %s WHERE cardno = %s AND cardtype = %s AND cardid = %s"
            self.obj.db.execute(sql, id, argkw['cardno'], argkw['cardtype'], argkw['cardid'] )
            self.obj.db.commit()
            self.insert_id = id
            return 1
        except:
            # Rollback in case there is any error
            self.obj.db.execute( "DELETE FROM user WHERE id = '%s'", id )
            self.obj.db.commit()
            self.obj.db.close()
            return self._respone(500) 


    def get_insert_id(self):
        if self.insert_id:
            return self.insert_id
        else:
            return False
        
    def userinfo(self,username=False,save=True):
        username = str(username)
        if username:
            info = self.obj.rd.hgetall('userinfo:'+username)
            if info:
                #有缓存则直接获取,并且更新时间
                self.obj.rd.expire('userinfo:'+username, setting['redisexpire'])
                return info
            else:
                #无缓存查库
                info = self.trueinfo(username)
                if save:
                    self.rdsave(username)
                return info
        else:
            return False
      
    #查库
    def trueinfo(self,username='',id=''):
        if username:
            info = self.obj.db.get("select u.*,i.*,f.path as headimgurl from user as u left join user_info as i on u.id = i.id left join user_face as f on u.id = f.id where username = %s", username)
        elif id:
            info = self.obj.db.get("select u.*,i.*,f.path as headimgurl from user as u left join user_info as i on u.id = i.id left join user_face as f on u.id = f.id where u.id = %s", id)
        if info:
            self.data = info
            return info
        else:
            return None

    #微信信息
    def wechat_info(self,openid='',flush=False):
        if not flush:
            info = self.obj.rd.hgetall('wechatinfo:'+openid)
            if info:
                #有缓存则直接获取,并且更新时间
                self.obj.rd.expire('wechatinfo:'+openid, setting['redisexpire'])
                return info
        #获取access_token
        access_token = self.obj.get_access_token()
        if access_token:
            url ="https://api.weixin.qq.com/cgi-bin/user/info?access_token="+access_token+"&openid="+openid+"&lang=zh_CN"
            info = self.obj.httplib_get(url)
            if info.has_key('errcode'):
                return {'nickname':'获取失败1','bind':False,'errcode':info['errcode']}
            else:
                self.obj.rd.hmset('wechatinfo:'+openid, info) 
                self.obj.rd.expire('wechatinfo:'+openid, setting['redisexpire'])
                return info
        else:
            return {'nickname':'获取失败2','bind':False}


    #绑定信息
    def userbind(self,openid=''):
        username = self.obj.rd.get('userbind:'+openid)
        if not username or username == 'None':
            #redis没缓存则查库
            sql = "SELECT u.username FROM wechat_user AS w LEFT JOIN user AS u ON w.user_id = u.id WHERE w.openid = %s"
            token = self.obj.db.get( sql, openid )
            if token and token['username']:
                #存在绑定信息,获取用户名并且缓存
                username = token['username']
                self.obj.rd.set('userbind:'+openid, username)
                self.obj.rd.expire('userbind:'+openid, setting['redisexpire'])
            else:
                #没有绑定信息，返回微信信息
                info = self.wechat_info( openid, True )
                info['bind'] = False
                return info
        else:
            #更新缓存时间
            self.obj.rd.expire('userbind:'+openid, setting['redisexpire'])
        #返回用户信息
        info = self.userinfo( username )
        info['bind'] = True
        return info


    def rdsave(self,username='0'):
        self.obj.rd.hmset('userinfo:'+username, self.data) 
        self.obj.rd.expire('userinfo:'+username, setting['redisexpire'])
    

    def editinfo(self,key,val,username=''):
        info = self.userinfo(username)
        #邮箱与电话的唯一性
        if key == 'phone':
            code = 209
        elif key == 'mail':
            code = 208
        else:
            code = False
        if code:
            select = "SELECT count(id) AS num FROM user_info WHERE "+key+" = %s AND id != %s "
            only = self.obj.db.get( select, val, info['id'] )
            if only['num'] > 0:
                 return self._respone( code )

        sql = "UPDATE user_info SET "+key+" = %s WHERE id = %s"
        try:
            self.obj.db.execute_lastrowid( sql, val, info['id'] )
            self.obj.db.commit()
            #更新redis
            self.trueinfo(info['username'])
            self.rdsave(info['username'])
            return 1
        except:
            return self._respone(500) 

    #电话唯一性验证
    def only_phone(self,phone,id=None):
        if id:
            w = ' AND id != %s' %id
        else:
            w = ''
        sql = "SELECT count(id) AS num FROM user_info WHERE phone = %s" + w
        only = self.obj.db.get( sql, phone )
        if only['num'] == 0:
            return True
        else:
            return False


    def make_pass(self,pwd='',salt='asdfgh'):
        key = pwd+salt
        return self.obj.md5(key)


    def flush_bind(self,id='',openid=''):      
        wechat = self.obj.db.get('SELECT id FROM wechat_user WHERE openid = %s',openid)
        head = self.obj.rd.hgetall('wechatinfo:'+openid)
        #送的金额
        gift = self.obj.db.get("SELECT value FROM system_param WHERE item = 'reg_gift'")
        give = int(gift['value']) if gift else 0
        #保存头像地址
        query = "UPDATE user_face SET path = %s WHERE id = %s" 
        #保存用户名
        nickname = "UPDATE user_info SET nickname = %s WHERE id = %s"
        if wechat:
            sql = "UPDATE wechat_user SET user_id = %s WHERE id = %s" %( id, wechat['id'] )
            give = "UPDATE user_purse SET balance = balance WHERE id = %s" %(id)
        else:
            sql = "INSERT into wechat_user ( openid, user_id ) VALUES( '%s', '%s' )" %( openid, id )
            give = "UPDATE user_purse SET balance = balance + %s WHERE id = %s" %( give, id )
        try:
            self.obj.db.execute( nickname, head['nickname'], id )
            self.obj.db.execute( give )
            self.obj.db.execute( sql )
            self.obj.db.execute( query, head['headimgurl'], id )
            self.obj.db.commit()
            return 1
        except:
            return self._respone(500) 
  
    #取消绑定
    def cancel(self,openid=''):
        sql = "UPDATE wechat_user SET user_id = 0 WHERE openid = %s"
        try:
            self.obj.db.execute( sql, openid )
            self.obj.db.commit()
            return 1
        except:
            return self._respone(500) 

    #一键注册
    def oneBind(self,openid=''):
        username = self.used_name()
        reg = self.register(username=username,password=username)
        id = self.get_insert_id()
        bind = self.flush_bind(id,openid)
        if reg == 1 and bind == 1:
            return 1
        elif reg == 1:
            return bind
        elif bind == 1:
            return reg


    #判断用户名唯一性
    def used_name(self):
        username = self.obj.random_str(10,'str').lower()
        row = self.trueinfo(username)
        if row:
            return self.used_name()
        else:
            return username

    #id查卡信息
    def cardinfo(self,id):
        card = self.obj.db.get("select * from card where user_id = %s", id)
        if card:
            return card
        else:
            return None
    #卡查id
    def carduser(self,cardno,cardtype,cardid):
        sql = "select user_id from card where cardno = %s AND cardtype = %s AND cardid = %s"
        card = self.obj.db.get( sql %(cardno,cardtype,cardid) )
        if card:
            return card
        else:
            return None

    #钱相关
    def userpurse(self, id):
        if id:
            sql = "SELECT * FROM user_purse WHERE id = %s"
            package = self.obj.db.get( sql, id )
            return package
        else:
            return None


###################后台##############################

    def user_list(self,where = '',page=1,per_page=15):
        token = "SELECT count(u.id) AS num FROM user AS u LEFT JOIN user_info AS i ON u.id = i.id LEFT JOIN user_purse AS p ON u.id = p.id " + where
        doll = self.obj.db.get(token)
        if not doll or doll['num'] <= 0:
            return None
        self.num = doll['num']
        self.this_page = page
        start = self.usepage.make_page( doll['num'], page, per_page )  
        sql = "SELECT u.username,u.reg_ip,u.reg_time,u.status,i.*,p.balance,p.payed FROM user AS u LEFT JOIN user_info AS i ON u.id = i.id LEFT JOIN user_purse AS p ON u.id = p.id %s ORDER BY u.reg_time DESC LIMIT %s, %s"
        ulist = self.obj.db.query( sql %(where,start,per_page) )
        if ulist:
            return ulist
        else:
            return None

    #更改用户状态
    def change_status(self,id,value):
        sql = "UPDATE user SET status = %s WHERE id = %s"
        try:
            self.obj.db.execute( sql, value, id )
            self.obj.db.commit()
            return '1'
        except:
            return self._respone(307)

    #回收站
    def user_delete(self,id):
        sql = "UPDATE user SET status = 2 WHERE id = %s"
        try:
            self.obj.db.execute( sql, id )
            self.obj.db.commit()
            return 1
        except:
            return self._respone(307)

    #重置密码
    def pass_reset(self,id,password):
        info = self.trueinfo( '', id )
        newpass = self.make_pass(password,info['salt'])
        sql = "UPDATE user SET password = %s WHERE id = %s"
        try:
            self.obj.db.execute( sql, newpass, id )
            self.obj.db.commit()
            return 1
        except:
            return self._respone(307)

    #绑定信息
    def user_wechat(self,id):
        sql = "SELECT * FROM wechat_user WHERE user_id = %s"
        wechat = self.obj.db.get( sql, id )
        return wechat

    #绑定信息
    def user_wechats(self,openid):
        sql = "SELECT * FROM wechat_user WHERE openid = %s"
        wechat = self.obj.db.get( sql, openid )
        return wechat

    #用户信息批量修改
    def uinfo_edit(self,**param):
        #电话唯一性
        if param.has_key('phone') and param['phone']:
            phone = "SELECT count(id) AS num FROM user_info WHERE phone = %s AND id != %s "
            ho = self.obj.db.get( phone, param['phone'], param['id'] )
            if ho['num'] > 0:
                return '0'
        #邮箱唯一性
        if param.has_key('mail') and param['mail']:
            mail = "SELECT count(id) AS num FROM user_info WHERE mail = %s AND id != %s "
            mo = self.obj.db.get( mail, param['mail'], param['id'] )
            if mo['num'] > 0:
                return '0'

        sql = "UPDATE user_info SET nickname = %s,mail = %s,phone = %s,sex = %s WHERE id = %s"
        try:
            self.obj.db.execute( sql, param['nickname'], param['mail'], param['phone'], param['sex'], param['id'] )
            self.obj.db.commit()
            return '1'
        except:
            return '0'

    #修改钱
    def purse_edit(self,**param):
        sql = "UPDATE user_purse SET balance = %s WHERE id = %s"
        try:
            self.obj.db.execute( sql, param['balance'], param['id'] )
            self.obj.db.commit()
            return '1'
        except:
            return '0'

    #写入充值订单
    def purse_order(self,user_id, increase, model, depict):
        oid = self.build_order()
        sql = "INSERT INTO purse_order( oid, user_id, increase, acttime, model, depict ) VALUES( %s, %s, %s ,%s ,%s ,%S )"
        try:
            self.obj.db.insert( sql, oid, user_id, increase, int(time.time()), model, depict )
            self.obj.db.commit()
            return True
        except:
            return False


    def user_live(self,id):
        sql = "UPDATE user SET status = 1 WHERE FIND_IN_SET( id, '%s' )"
        try:
            self.obj.db.execute( sql %id )
            self.obj.db.commit()
            return True
        except:
            return False

    def user_kill(self,id):
        sql = "DELETE FROM user WHERE FIND_IN_SET( id, '%s' )"
        info = "DELETE FROM user_info WHERE FIND_IN_SET( id, '%s' )"
        face = "DELETE FROM user_face WHERE FIND_IN_SET( id, '%s' )"
        purse = "DELETE FROM user_purse WHERE FIND_IN_SET( id, '%s' )"
        card = "DELETE FROM card WHERE FIND_IN_SET( user_id, '%s' )"
        wechat = "UPDATE wechat_user SET user_id = 0 WHERE FIND_IN_SET( user_id, '%s' )"
        try:
            self.obj.db.execute( sql %id )
            self.obj.db.execute( info %id )
            self.obj.db.execute( face %id )
            self.obj.db.execute( purse %id )
            self.obj.db.execute( card %id )
            self.obj.db.execute( wechat %id )
            self.obj.db.commit()
            return True
        except:
            return False


    def charge_count(self,id):
        d = datetime.date.today().replace(day=1)
        start = int( time.mktime(d.timetuple()) )
        sql = "SELECT count(oid) AS num FROM charge_order WHERE finish > 0 AND user_id = %s"
        doll = self.obj.db.get(sql, id)
        query = 'SELECT count(oid) AS num FROM charge_order WHERE finish > 0 AND user_id = %s AND creatime > %s '
        month = self.obj.db.get(query,id,start)
        res = {}
        res['all'] = doll['num'] if doll else 0
        res['month'] = month['num'] if month else 0
        return res

    # mode 1是线下站点充值
    def build_order(self,model=1):
        if self.doll > 9 :
            return False
        nowtime = time.strftime('%y%m%d%H')
        now = int(time.time())
        start = now - ( now % 86400 )
        token = "SELECT count(oid) as num FROM purse_order WHERE acttime >= %s AND acttime <= %s" %(start,now)
        one = self.obj.db.get(token)
        num = "%05d" % ( one['num'] + self.doll )
        newid = str(model) + nowtime + num
        only = "SELECT oid FROM purse_order WHERE oid = %s"
        alone = self.obj.db.get(only,newid)
        if alone:
            self.doll = self.doll + 1
            return self.build_order(model)
        else:
            return newid


    #分页
    def page_bar(self,model=1,number=2):
        if model == 1:
            url = self.obj.request.uri
            res = self.usepage.make_bar(url,number);
        elif model == 2:
            res = self.usepage.page_info();
        return res

    def __del__(self):
        self.obj.db.close()
          