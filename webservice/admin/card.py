# -*- coding: utf-8 -*-
from public import *
from model.validate import validate
from model.cardmodel import *
from model.usermodel import *
import time,hashlib
from config import setting
from model.language import lang

apimsg = lang()        #文字类
#用户列表
class CardListHandler(webHandler):
	@admin_access
	def get(self):
		cardno = self.get_argument('cardno','')
		cardtype = self.get_argument('cardtype','')
		cardnumber = self.get_argument('cardnumber','')
		page = self.get_argument('page',1)
		where = ' where u.status < 2 '
		if cardno:
			where += " AND c.cardno = '"+cardno+"'"
		if cardtype:
			where += " AND c.cardtype like '"+str(int(cardtype))+"%%'"
		if cardnumber:
			cardtype = int(cardnumber[0:4])
			cardid = int(cardnumber[4:])
			where += " AND c.cardtype = '"+str(cardtype)+"' AND c.cardid = '"+str(cardid)+"'"
		card = cardmodel(self)
		clist = card.card_list( where, page, 20 )
		if clist:
			page_bar = card.page_bar(1)
			pinfo = card.page_bar(2)
		else:
			page_bar = None
			pinfo = {'this_page':1,'all_page':0,'per_page':20}
		search = {'cardno':cardno,'cardnumber':cardnumber,'cardtype':cardtype}
		self.render("admin/cardlist.html", clist=clist, search=search,page_bar=page_bar,pinfo=pinfo )


	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)

#新卡
class NewCardHandler(webHandler):
	@admin_access
	def get(self):
		card = cardmodel(self)
		type_list = card.card_type()
		self.render("admin/newcard.html", type_list=type_list )

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)

#添加卡
class AddCard(webHandler):
	@admin_access
	def post(self):
		cardtype = self.get_argument('cardtype','')
		cardno = self.get_argument('cardno','')
		if cardno and cardtype:
			card = cardmodel(self)
			#识别码唯一
			ck = card.only_cardno(cardno)
			if ck:
				user = usermodel(self)
				username = user.used_name()
				res = user.register(username=username,password=username,cardno=cardno,cardtype=cardtype)
				id = user.get_insert_id()
				info = user.cardinfo( id )
				if res:
					self.prompt( 1, apimsg.notice(306), '/admin/cardlist', '卡号:'+'%04d%08d'%(info['cardtype'],info['cardid']) )
				else:
					self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)' )
			else:
				self.prompt( 0, apimsg.notice(220), 'javascript:history.go(-1)' )
		else:
			self.prompt( 0, apimsg.notice(400), 'javascript:history.go(-1)' )


#卡分类
class CardTypeHandler(webHandler):
	@admin_access
	def get(self):
		card = cardmodel(self)
		type_list = card.card_type()
		self.render("admin/cardtype.html", type_list=type_list )


	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)


#新分类
class NewTypeHandler(webHandler):
	@admin_access
	def get(self):
		info = {'id':'','cardtype':'','typename':'','ascno':5}
		self.render("admin/typeinfo.html",info=info,act='add')

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)


#编辑分类
class EditTypeHandler(webHandler):
	@admin_access
	def get(self):
		id = self.get_argument('id','')
		card = cardmodel(self)
		info = card.typeinfo( id )
		self.render("admin/typeinfo.html",info=info,act='edit')

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)

#排序
class ChangeAsc(webHandler):
	@admin_access
	def post(self):
		id = self.get_argument('id','')
		number = self.get_argument('no',5)
		if id:
			card = cardmodel(self)
			sett = "ascno = %s" %number
			where = "id = %s" %id
			res = card.change_type( sett, where )
			if res:
				self.finish('1')
			else:
				self.finish('0')
		else:
			self.finish('2')


#操作分类(增加,修改)
class TypeAction(webHandler):
	@admin_access
	def post(self):
		act = self.get_argument('act','')
		cardtype = self.get_argument('cardtype','')
		typename = self.get_argument('typename','')
		ascno = self.get_argument('ascno','')
		id = self.get_argument('id','')
		card = cardmodel(self)
		only = card.only_cardtype( cardtype, id )
		if only:
			if act == 'add':
				res = card.addtype(cardtype,typename,ascno)
			elif act == 'edit':
				sett = "cardtype=%s,typename='%s',ascno=%s" %(int(cardtype),typename,int(ascno))
				where = "id=%s" %id
				res = card.change_type( sett, where )
			if res:
				self.prompt( 1, apimsg.notice(305), '/admin/card_type' )
			else:
				self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)' )
		else:
			self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)', apimsg.notice(221) )

			
class DeleteCard(webHandler):
	@admin_access
	def get(self):
		id = self.get_argument('id','')
		card = cardmodel(self)
		res = card.delete_card(id)
		if res == 1:
			self.prompt( 1, apimsg.notice(305), self.request.headers['Referer'] )
		else:
			self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)' )


#删除分类
class DeleteType(webHandler):
	@admin_access
	def get(self):
		id = self.get_argument('id','')
		card = cardmodel(self)
		res = card.delete_type( id )
		if res == 1:
			self.prompt( 1, apimsg.notice(305), self.request.headers['Referer'] )
		else:
			self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)', res )


class CardSeller(webHandler):
	@admin_access
	def get(self):
		page = self.get_argument('page',1)
		sellername = self.get_argument('sellername','')
		phone = self.get_argument('phone','')
		where = ' where 1=1 '
		if sellername:
			where += " AND sellername like '%%"+sellername+"%%'"
		if phone:
			where += " AND phone = '%s'" %phone
		card = cardmodel(self)
		slist = card.getsellers(where,page,15)
		if slist:
			page_bar = card.page_bar(1)
			pinfo = card.page_bar(2)
		else:
			page_bar = None
			pinfo = {'this_page':1,'all_page':0,'per_page':20}
		search = {'sellername':sellername,'phone':phone}
		self.render("admin/sellerlist.html", slist=slist, search=search,page_bar=page_bar,pinfo=pinfo )

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)



class SellerStatus(webHandler):
	@admin_access
	def post(self):
		id = self.get_argument('id','')
		value = self.get_argument('val','1')
		card = cardmodel(self)
		res = card.change_sell_status( id, value )
		self.finish( res )


class DeleteSeller(webHandler):
	@admin_access
	def get(self):
		id = self.get_argument('id','')
		card = cardmodel(self)
		res = card.delete_seller( id )
		if res == 1:
			self.prompt( 1, apimsg.notice(305), self.request.headers['Referer'] )
		else:
			self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)', res )


#新商家
class NewSellerHandler(webHandler):
	@admin_access
	def get(self):
		info = {'id':'','sellername':'','phone':'','appid':'','status':1,'duty':''}
		self.render("admin/sellerinfo.html",info=info,act='add')

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)


#编辑商家
class EditSellerHandler(webHandler):
	@admin_access
	def get(self):
		id = self.get_argument('id','')
		card = cardmodel(self)
		info = card.sellerinfo( id )
		self.render("admin/sellerinfo.html",info=info,act='edit')

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)

#操作
class ActSeller(webHandler):
	@admin_access
	def post(self):
		act = self.get_argument('act','')
		sellername = self.get_argument('sellername','')
		phone = self.get_argument('phone','')
		appid = self.get_argument('appid','')
		oldkey = self.get_argument('oldkey','')
		appkey = self.get_argument('appkey','')
		status = self.get_argument('status','')
		duty = self.get_argument('duty','')
		id = self.get_argument('id','')
		card = cardmodel(self)
		if act == 'add':
			appkey = hashlib.sha1( appkey ).hexdigest()
			res = card.addseller(sellername,phone,appid,appkey,status,duty)
		elif act == 'edit':
			sellerinfo = card.sellerinfo( id )
			sett = ''
			if oldkey and appkey:
				#有修改密码
				if hashlib.sha1( oldkey ).hexdigest() == sellerinfo['appkey']:
					#密码验证通过
					appkey = hashlib.sha1( appkey ).hexdigest()
					sett += "appkey='%s'," %appkey
				else:
					self.prompt( 1, apimsg.notice(201), 'javascript:history.go(-1)' )
					return
			sett += "sellername='%s',phone='%s',appid='%s',status=%s,duty='%s'" %(sellername,phone,appid,status,duty)
			where = "id=%s" %id
			res = card.editseller( sett, where )
		if res:
			self.prompt( 1, apimsg.notice(305), '/admin/card_seller' )
		else:
			self.prompt( 0, apimsg.notice(307), 'javascript:history.go(-1)' )
	
	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)

#负责人修改
class ActDuty(webHandler):
	@admin_access
	def post(self):
		id = self.get_argument('id','')
		if id:
			duty = self.get_argument('duty','')
			card = cardmodel(self)
			res = card.change_duty( duty, id )
			if res:
				self.finish('1')
			else:
				self.finish('0')
		else:
			self.finish('2')


	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)


class SellerRecord(webHandler):
	@admin_access
	def get(self):
		id = self.get_argument('id','')
		page = self.get_argument('page',1)
		start = self.get_argument('start','')
		end = self.get_argument('end','')
		if id:
			where = "WHERE seller = %s" %id
			if start:
				st = time.mktime(time.strptime(start,'%Y-%m-%d'))
				where += " AND acttime >= %s" %int(st)
			if end:
				en = time.mktime(time.strptime(end,'%Y-%m-%d'))
				where += " AND acttime <= %s" %int(en)
		else:
			self.prompt( 0, apimsg.notice(400), 'javascript:history.go(-1)' )
			return
		card = cardmodel(self)
		rlist = card.seller_records( where, page, 15 )
		if rlist:
			page_bar = card.page_bar(1)
			pinfo = card.page_bar(2)
		else:
			page_bar = None
			pinfo = {'this_page':1,'all_page':0,'per_page':15}
		search = {'start':start,'end':end,'id':id}
		self.render("admin/seller_records.html", rlist=rlist, search=search,page_bar=page_bar,pinfo=pinfo )

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/admin/login')
		else:
			error = apimsg.notice(status_code)
			self.render("admin/error.html", code=status_code, error=error)