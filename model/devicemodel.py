# -*- coding: utf-8 -*-
from model.language import lang
from config import setting
import uuid,time
from model.page import pagemodel
from model.adminmodel import *

class devicemodel():
    def __init__(self,obj):
        self.obj = obj
        self.apimsg = lang()
        self.usepage = pagemodel()

    def _respone(self, code):
        return self.apimsg.notice(code)


    #设备列表
    def devicelist(self,where,page=1,per_page=15):
        token = "SELECT count(id) AS num FROM device %s"
        doll = self.obj.db.get(token %where)
        if not doll or doll['num'] <= 0:
            return None
        self.num = doll['num']
        self.this_page = page
        start = self.usepage.make_page( doll['num'], page, per_page )  
        sql = "SELECT * FROM device %s ORDER BY id DESC LIMIT %s, %s"
        dlist = self.obj.db.query( sql %(where,start,per_page) )
        if dlist:
            return dlist
        else:
            return None


    def device_info(self,id):
    	sql = "SELECT * FROM device WHERE id = %s"
    	info = self.obj.db.get(sql,id)
    	if info:
            return info
        else:
            return None


    def change_open(self,value,id):
        sql = "UPDATE device SET isopen = %s WHERE id = %s"
        try:
            self.obj.db.execute( sql, value, id )
            self.obj.db.commit()
            return True
        except:
            return False

    #添加设备
    def add_device(self,**param):
        sql = "INSERT INTO device (code,name,latitude,longitude,isopen) VALUES(%s,%s,%s,%s,%s)"
        try:
            self.obj.db.insert( sql, param['code'], param['name'], param['latitude'], param['latitude'], param['isopen'] )
            self.obj.db.commit()
            return True
        except:
            return False


    def edit_device(self,**param):
        sql = "UPDATE device SET code=%s,name=%s,latitude=%s,longitude=%s,isopen=%s WHERE id=%s"
        try:
            self.obj.db.execute( sql, param['code'], param['name'], param['latitude'], param['latitude'], param['isopen'], param['id'] )
            self.obj.db.commit()
            return True
        except:
            return False

    def only_code(self,code,id=''):
    	if id:
    		where = " AND id != %s" %str(id)
    	else:
    		where = ''
    	sql = "SELECT count(id) AS num FROM device WHERE code = %s" + where
    	token = self.obj.db.get( sql, code )
        if token and token['num'] == 0:
        	return True
        else:
        	return False
        

    def delete_device(self,id):
    	sql = "DELETE FROM device WHERE id=%s"
        try:
            self.obj.db.execute( sql,id )
            self.obj.db.commit()
            return True
        except:
            return False

    def error_number(self,nowtime=int(time.time())):
		adm = adminmodel(self.obj)
		server = adm.server_setting()
		limit = int(server['device_pass']) * 60
		sql = "SELECT count(id) as num FROM device WHERE isopen = 1 AND %s - heart_time > %s limit 100" %(nowtime,limit)
		token = self.obj.db.get( sql )
		res = token['num'] if token and token['num'] else 0
		return res

    def error_list(self,nowtime=int(time.time())):
		adm = adminmodel(self.obj)
		server = adm.server_setting()	
		limit = int(server['device_pass']) * 60
		sql = "SELECT * FROM device WHERE isopen = 1 AND %s - heart_time > %s ORDER BY heart_time limit 100" %(nowtime,limit)
		dlist = self.obj.db.query( sql )
		if dlist:
			return dlist
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