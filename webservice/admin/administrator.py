# -*- coding: utf-8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from public import *
from model.language import lang
from config import setting
from model.validate import validate
from model.adminmodel import *
from model.devicemodel import *
from model.chargemodel import *
import urllib
apimsg = lang()

#后台首页框架
class IndexHandler(webHandler):
	@admin_access
	def get(self):
		left = {}
		dev = devicemodel(self)
		#电桩异常提示数量
		left['error'] = dev.error_number()
		nowtime = int(time.time())
		#电桩异常提示详情
		if left['error'] > 0:
			dlist = dev.error_list( nowtime )
		else:
			dlist = None

		charge = chargemodel(self)
		where = {'o.finish =':0}
		clist = charge.workinglist(where,1,1)
		pinfo = charge.page_bar(2)
		if pinfo:
			left['working'] = pinfo['all_num']
		else:
			left['working'] = 0
		self.render("admin/main.html",left=left,dlist=dlist)

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)

#欢迎页
class WelcomeHandler(webHandler):
	@admin_access
	def get(self):
		adm = adminmodel(self)
		statistics = adm.data_statistics()
		month = adm.month_money()
		orders = adm.new_orders()
		self.render("admin/index.html",statistics=statistics,month=month,orders=orders)

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)


#登录
class LoginHandler(webHandler):
	def get(self):
		admin = self.get_argument('admin','')
		message = self.get_argument('message','')
		error = self.get_secure_cookie('admin_error')
		error = error if error else 0
	#	error = 5
		if int(error) <= 3 :
			nocaptcha = True
		else:
			nocaptcha = False
		time = self.random_str(6)
		self.render("admin/login.html",admin=admin,message=message,time=time,nocaptcha=nocaptcha)

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)

#登录处理
class ActLogin(webHandler):
	def post(self):
		admin = self.get_argument('admin','')
		password = self.get_argument('password','')
		captcha = self.get_argument('captcha','') 
		valid = validate()
		valid.Add( admin,'账号', ['NoEmpty'] )
		valid.Add( password,'密码', ['NoEmpty'] )
		if not valid._CheckMate():
			#跳转去相关页面
			params = urllib.urlencode({'admin':admin,'message':'用户名密码不能为空'}) 
			url = "/admin/login?%s" %(params)
			self.redirect(url)
			return 
		adm = adminmodel(self)
		res = adm.adminlogin( admin=admin,password=password,captcha=captcha )
		if res == 1:
			self.write("<script>top.window.location='/admin/index'</script>")
		#	self.redirect( '/admin/index' )
		else:
			params = urllib.urlencode({'admin':admin,'message':res}) 
			url = "/admin/login?%s" %(params)
			self.redirect(url)

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)

#添加管理员
class NewadminHandler(webHandler):
	@admin_access
	def get(self):
		info = {'id':'','admin':''}
		self.render('admin/adminpass.html',act='add',info=info)

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)


#管理员列表
class AdminListHandler(webHandler):
	@admin_access
	def get(self):
		admin = self.get_argument('admin','')
		nickname = self.get_argument('nickname','')
		page = self.get_argument('page','')
		where = "where 1=1 "
		if admin:
			where += " AND a.admin = '%s' "%admin
		if nickname:
			where += " AND i.nickname like '%%"+nickname+"%%'"
		adm = adminmodel(self)
		admin_list = adm.adminlist( where, page, 20 )
		if admin_list:
			page_bar = adm.page_bar(1)
			pinfo = adm.page_bar(2)
		else:
			page_bar = None
			pinfo = {'this_page':1,'all_page':0,'per_page':20}
		search = {'admin':admin,'nickname':nickname}
		self.render("admin/adminlist.html",admin_list=admin_list,search=search,page_bar=page_bar,pinfo=pinfo)

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)


#编辑管理员
class EditAdminHandler(webHandler):
	@admin_access
	def get(self):
		admin = self.get_argument('admin','')
		adm = adminmodel(self)
		info = adm.adminmain(admin)
		if info:
			self.render('admin/adminpass.html',act='reset',info=info)
		else:
			self.prompt( 0, apimsg.notice(400), 'javascript:history.go(-1)' )

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)

#管理员操作
class ActAdmin(webHandler):
	@admin_access
	def post(self):
		admin = self.get_argument('admin','')
		password = self.get_argument('password','')
		id = self.get_argument('id','')
		act = self.get_argument('act','')
		valid = validate()
		if act == 'add':
			valid.Add( admin,'管理员ID', ['NoEmpty'], 6, 30 )
		valid.Add( password,'密码', ['NoEmpty'], 6, 30 )
		if not valid._CheckMate():
			self.prompt( 0, apimsg.notice(400), 'javascript:history.go(-1)', valid._Message() )
			return
		adm = adminmodel(self)
		if act == 'add':
			res = adm.newadmin(admin=admin,password=password)
		elif act == 'reset':
			info = adm.adminmain(admin)
			if info and id:
				newpass = adm.adminpass(password,info['salt'])
				res = adm.change_pass(newpass,id)
			else:
				self.prompt( 0, apimsg.notice(400), '/admin/admin_list' )
				return
		if res == 1:
			self.prompt( 1, apimsg.notice(305), '/admin/admin_list' )
		else:
			self.prompt( 0, apimsg.notice(307), '/admin/admin_list' )

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)

#删除
class DeleteAdmin(webHandler):
	@admin_access
	def get(self):
		id = self.get_argument('id','')
		adm = adminmodel(self)
		res = adm.delete_admin( id )
		if res == 1:
			self.prompt( 1, apimsg.notice(305), self.request.headers['Referer'] )
		else:
			self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)', res )


class AdminChangeNickname(webHandler):
	def post(self):
		id = self.get_argument('id','')
		if id:
			nickname = self.get_argument('nickname','')
			adm = adminmodel(self)
			res = adm.change_name( nickname, id )
			if res:
				self.finish('1')
			else:
				self.finish('0')
		else:
			self.finish('2')


#站点设定
class SettingHandler(webHandler):
	@admin_access
	def get(self):
		adm = adminmodel(self)
		setting = adm.server_setting()
		self.render("admin/setting.html",setting=setting)

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)


#更改设定
class ActSetting(webHandler):
	@admin_access
	def post(self):
		reg_gift = self.get_argument('reg_gift',0)
		register = self.get_argument('register',1)
		wechat = self.get_argument('wechat',1)
		deposit = self.get_argument('deposit',1)
		device_pass = self.get_argument('device_pass',1)
		adm = adminmodel(self)
		param = {'reg_gift':float(reg_gift),'register':register,'wechat':wechat,'deposit':deposit,'device_pass':device_pass}
		res = adm.update_setting( param )
		if res == 1:
			self.prompt( 1, apimsg.notice(305), '/admin/setting' )
		else:
			self.prompt( 0, apimsg.notice(307), '/admin/setting', res )

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)


#提示
class NoticeHandler(webHandler):
	def get(self):
		#成功或者失败
		sign = self.get_argument('sign','1')
		notice = self.get_argument('notice','')
		#信息提示
		mess = self.get_argument('mess','')
		#跳转地址
		reback = self.get_argument('reback','')
		self.render("admin/notice.html", sign=sign, notice=notice, mess=mess, reback=reback)

#注销
class Layout(webHandler):
	def get(self):
		sessionid = self.get_secure_cookie('sessionid')
		if sessionid:
			self.rd.expire('admininfo:'+str(sessionid), 0)
		self.set_secure_cookie('sessionid','0',expires_days=None)
		self.redirect('/admin/login')


#头文件
class AdminHeadModule(tornado.web.UIModule):
	def render(self,obj=''):
		if obj:
			sessionid = obj.get_secure_cookie('sessionid')
			adm = adminmodel(obj)
			ainfo = adm.admininfo(sessionid)

		#没ainfo
		if not ainfo:
			ainfo = {'nickname':'神秘人'}
		html = '''  <div id="mws-user-info" class="mws-inset">
	                	<div id="mws-user-functions">
	                    	<div id="mws-username">
		                        欢迎您登录, '''+ainfo['nickname']+'''
		                    </div>
		                    <ul>
		                        <li><a target="myframe" href="/admin/edit_admin?admin='''+ainfo['admin']+'''">更改密码</a></li>
		                        <li><a target="myframe" href="/admin/layout">注销</a></li>
		                    </ul>
		                </div>
		            </div>'''
		return html

#页底文件
class AdminFootModule(tornado.web.UIModule):
	def render(self):
		html = '''  <div id="mws-footer">
					    Copyright &copy; 2015.Company name All rights reserved.
					</div>'''
		return html
