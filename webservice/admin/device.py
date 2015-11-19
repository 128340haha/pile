# -*- coding: utf-8 -*-
from public import *
from model.validate import validate
from model.devicemodel import *
import time
from config import setting
from model.language import lang

apimsg = lang()        #文字类
#用户列表
class DeviceListHandler(webHandler):
	@admin_access
	def get(self):
		code = self.get_argument('code','')
		name = self.get_argument('name','')
		status = self.get_argument('status','9')
		page = self.get_argument('page',1)
		where = ' where 1=1 '
		if code:
			where += " AND code = '"+code+"'"
		if name:
			where += " AND name like '%%"+name+"%%'"
		if status == '0':
			where += " AND %s - heart_time > 120 " %int(time.time())
		elif int(status) < 9:
			where += " AND status = '"+str(status)+"' AND %s - heart_time <= 120 " %int(time.time())
		dev = devicemodel(self)
		dlist = dev.devicelist( where, page, 20 )
		if dlist:
			page_bar = dev.page_bar(1)
			pinfo = dev.page_bar(2)
		else:
			page_bar = None
			pinfo = {'this_page':1,'all_page':0,'per_page':20}
		search = {'code':code,'name':name,'status':status}
		self.render("admin/devicelist.html", dlist=dlist, search=search,page_bar=page_bar,pinfo=pinfo )


	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)


class NewDeviceHandler(webHandler):
	@admin_access
	def get(self):
		info = {'id':'','code':'','name':'','status':'','latitude':'','longitude':'','isopen':1}
		self.render("admin/deviceinfo.html", info=info, act='add', referer='' )

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)

class EditDeviceHandler(webHandler):
	@admin_access
	def get(self):
		id = self.get_argument('id','')
		dev = devicemodel(self)
		info = dev.device_info(id)
		referer = self.request.headers['Referer']
		self.render("admin/deviceinfo.html", info=info, act='edit', referer=referer )

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)


class ActDevice(webHandler):
	@admin_access
	def post(self):
		act = self.get_argument('act','')
		code = self.get_argument('code','')
		name = self.get_argument('name','')
		latitude = self.get_argument('latitude','')
		longitude = self.get_argument('longitude','')
		isopen = self.get_argument('isopen','')
		id = self.get_argument('id','')
		dev = devicemodel(self)
		if act == 'add':
			one = dev.only_code( code )
			if not one:
				self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)', '该设备号已经存在' )
				return
			res = dev.add_device(code=code,name=name,latitude=latitude,longitude=longitude,isopen=isopen)
			referer = '/admin/device_list'
		elif id and act == 'edit':
			one = dev.only_code( code, id )
			if not one:
				self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)', '该设备号已经存在' )
			res = dev.edit_device(id=id,code=code,name=name,latitude=latitude,longitude=longitude,isopen=isopen)
			referer = self.get_argument('referer','javascript:history.go(-1)')
		if res == 1:
			self.prompt( 1, apimsg.notice(305), referer )
		else:
			self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)', res )


class DeleteDevice(webHandler):
	@admin_access
	def get(self):
		id = self.get_argument('id','')
		if id:
			dev = devicemodel(self)
			res = dev.delete_device(id)
			if res:
				self.prompt( 1, apimsg.notice(305), '/admin/device_list' )
			else:
				self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)' )


#异常提醒
class DeviceErrorHandler(webHandler):
	@admin_access
	def get(self):
		dev = devicemodel(self)
		num = dev.error_number()
		nowtime = int(time.time())
		if num > 0:
			dlist = dev.error_list( nowtime )
		else:
			dlist = None
		self.render("admin/device_error.html", dlist=dlist, nowtime=nowtime )

#ajax更改状态
class OpenDevice(webHandler):
	@admin_access
	def post(self):
		id = self.get_argument('id','')
		if id:
			dev = devicemodel(self)
			val = self.get_argument('val','')
			res = dev.change_open(val,id)
			#写入日志文件
			if res:
				self.finish('1')
				return
		self.finish('0')
