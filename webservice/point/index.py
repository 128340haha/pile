# -*- coding: utf-8 -*-
from public import *
from model.cardmodel import *
from model.chargemodel import *
from model.usermodel import *
from model.logmodel import *
from model.language import lang
import time,json
from model.validate import validate
from config import setting

apimsg = lang()
#登陆
class LoginHandler(webHandler):
	def get(self):
		self.render("point/login.html")

	def write_error(self, status_code, **kwargs):
		self.finish(str(status_code))


#登录操作  ajax
class ActLogin(webHandler):
	def post(self):
		username = self.get_argument('username','')
		password = self.get_argument('password','')
		valid = validate()
		valid.Add( username,'用户名', ['NoEmpty'] )
		valid.Add( password,'密码', ['NoEmpty'] )
		if not valid._CheckMate():
			#跳转去相关页面
			self.finish('0')
			return 
		elif not self.health_param(username):
			#用户名格式异常
			self.finish('2')
			return 
		card = cardmodel(self)
		res = card.sellerlogin( username,password )
		self.finish(res)

	def write_error(self, status_code, **kwargs):
		self.finish(str(status_code))


#首页
class IndexHandler(webHandler):
	@seller_login
	def get(self):
	#	session = self.get_secure_cookie('seller')
	#	card = cardmodel(self)
	#	sid = card.get_seller_id( session )
		self.render("point/index.html")

	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/point/login')
		else:
			error = apimsg.notice(status_code)
			self.finish(self.respone_data( 0, error))



class Print(webHandler):
	@seller_login
	def get(self):
		cardno = self.get_argument('cardno','')
		cardid = self.get_argument('cardid','')
		cardtype = self.get_argument('cardtype','')
		page = self.get_argument('page','1')
		per_page = self.get_argument('per_page',15)
		target = self.get_argument('target','')
		valid = validate()
		valid.Add( cardno,'识别码', ['Isdigit'] )
		valid.Add( cardid,'卡号', ['NoEmpty','Isdigit'] )
		valid.Add( cardtype,'卡分类', ['NoEmpty','Isdigit'] )
		valid.Add( page,'当前页', ['NoEmpty','Isdigit'] )
		valid.Add( per_page,'每页显示', ['NoEmpty','Isdigit'] )
		if not valid._CheckMate(): 
			self.finish( self.respone_data( 0, valid._Message() ) )
			return
		user = usermodel(self)
		userid = user.carduser(cardno,cardtype,cardid)
		charge = chargemodel(self)
		if target == 'deposit':
			where = {'user_id =':userid['user_id']}
			dlist = charge.savelist(where,int(page),int(per_page))
		elif target == 'recharge':
			where = {'o.user_id =':userid['user_id'],'o.finish >':0}
			dlist = charge.chargelist(where,int(page),int(per_page))
		else:
			dlist = []
		self.render("point/print.html",dlist=json.dumps(dlist),target=target,cardno=cardno,cardid=cardid,cardtype=cardtype,page=page,per_page=per_page)
	
	def write_error(self, status_code, **kwargs):
		if status_code == 402:
			self.redirect('/point/login')
		else:
			error = apimsg.notice(status_code)
			self.finish(self.respone_data( 0, error))	

#######################↓↓↓功能函数↓↓↓##################################

#卡信息
class CardInfo(webHandler):
	@seller_login
	def get(self):
		cardno = self.get_argument('cardno','')
		cardid = self.get_argument('cardid','')
		cardtype = self.get_argument('cardtype','')
		valid = validate()
		valid.Add( cardno,'识别码', ['NoEmpty','Isdigit'] )
		valid.Add( cardid,'卡号', ['NoEmpty','Isdigit'] )
		valid.Add( cardtype,'卡分类', ['NoEmpty','Isdigit'] )
		if not valid._CheckMate():
			self.finish( self.respone_data( 0, valid._Message() ) )
			return
		#识别码
		where = " WHERE c.cardno = %d" %int(cardno)
		#卡号
		where += " AND c.cardtype = %d AND c.cardid = %d" %(int(cardtype),int(cardid))
		card = cardmodel(self)
		info = card.card_infomation( where ) 
		if info:
			self.finish( self.respone_data( 1, info ) )
		else:
			self.finish( self.respone_data( 2, apimsg.notice(222) ) )

	def write_error(self, status_code, **kwargs):
		error = apimsg.notice(status_code)
		self.finish(self.respone_data( 0, error))

#注册新卡
class RegCard(webHandler):
	@seller_login
	def post(self):
		cardno = self.get_argument('cardno','')
		cardid = self.get_argument('cardid','')
		cardtype = self.get_argument('cardtype','')
		nickname = self.get_argument('nickname','')
		phone = self.get_argument('phone','')
		password = self.get_argument('password','')
		balance = self.get_argument('balance','')
		valid = validate()
		valid.Add( cardtype,'分类', ['NoEmpty','Isdigit'] )
		valid.Add( cardno,'识别码', ['NoEmpty','Isdigit'] )
		valid.Add( cardid,'卡id', ['NoEmpty','Isdigit'] )
		valid.Add( phone,'手机', ['NoEmpty','Isdigit'],11,11 )
		valid.Add( nickname,'用户名', ['NoEmpty'] )
		valid.Add( balance,'充值金额', ['NoEmpty','Isdigit'] )
		if not valid._CheckMate():
			self.finish( self.respone_data( 0, apimsg.notice(400) ) )
			return
		user = usermodel(self)
		#唯一电话验证
		onlyphone = user.only_phone( phone )
		if not onlyphone:
			self.finish( self.respone_data( 0, apimsg.notice(228) ) )
			return
		#当前商家信息
		session = self.get_secure_cookie('seller')
		card = cardmodel(self)
		sid = card.get_seller_id( session )
		seller = card.sellerinfo( sid )
		#随机用户名
		username = user.used_name()
		#订单号
		oid = user.build_order()
		#注册新用户，同时绑定当前卡号
		res = user.bind_card(username=username,password=username,cardno=cardno,cardid=cardid,cardtype=cardtype)
		id = user.get_insert_id()
		if res == 1 and id:
			log = logmodel(self)
			#更改相关参数，以及写入日志
			final = log.newcard_infomation( username=username,phone=phone,nickname=nickname,balance=balance,sellerid=sid,sellername=seller['sellername'],password=password,user_id=id,oid=oid )
			if final == 1:
				self.finish( self.respone_data( 1 ) )
			else:
				self.finish( self.respone_data( 0, final ) )
		else:
			self.finish( self.respone_data( 0, res ) )


	def write_error(self, status_code, **kwargs):
		self.finish(str(status_code))

#更改卡信息
class EditCard(webHandler):
	@seller_login
	def post(self):
		cardno = self.get_argument('cardno','')
		cardid = self.get_argument('cardid','')
		cardtype = self.get_argument('cardtype','')
		phone = self.get_argument('phone','')
		nickname = self.get_argument('nickname','')
		password = self.get_argument('password','')
		valid = validate()
		valid.Add( cardno,'识别码', ['NoEmpty','Isdigit'] )
		valid.Add( cardtype,'分类', ['NoEmpty','Isdigit'] )
		valid.Add( cardid,'卡id', ['NoEmpty','Isdigit'] )
		valid.Add( phone,'手机', ['NoEmpty','Isdigit'],11,11 )
		if not valid._CheckMate():
			self.finish( self.respone_data( 0, apimsg.notice(400) ) )
			return
		user = usermodel(self)
		userid = user.carduser(cardno,cardtype,cardid)
		if userid:
			onlyphone = user.only_phone( phone, userid['user_id'] )
			if not onlyphone:
				self.finish( self.respone_data( 0, apimsg.notice(228) ) )
				return
			res = user.uinfo_edit(nickname=nickname,phone=phone,mail='',sex=1,id=userid['user_id'])
			if password:
				card = cardmodel(self)
				card.editinfo('pwd',self.md5(password),userid['user_id'])
			if res:
				self.finish( self.respone_data( 1 ) )
			else:
				self.finish( self.respone_data( 0, apimsg.notice(307) ) )
		else:
			self.finish( self.respone_data( 0, apimsg.notice(222) ) )

	def write_error(self, status_code, **kwargs):
		self.finish(str(status_code))



#充值
class ChangeBalance(webHandler):
	@seller_login
	def post(self):
		cardno = self.get_argument('cardno','')
		cardid = self.get_argument('cardid','')
		cardtype = self.get_argument('cardtype','')
		money = self.get_argument('money',0)
		valid = validate()
		valid.Add( cardno,'识别码', ['NoEmpty','Isdigit'] )
		valid.Add( cardtype,'分类', ['NoEmpty','Isdigit'] )
		valid.Add( cardid,'卡id', ['NoEmpty','Isdigit'] )
		valid.Add( money,'钱数', ['NoEmpty','Isdigit'] )
		if not valid._CheckMate():
			self.finish( self.respone_data( 0, valid._Message() ) )
			return
		#当前商家信息
		session = self.get_secure_cookie('seller')
		card = cardmodel(self)
		sid = card.get_seller_id( session )
		seller = card.sellerinfo( sid )
		#用户信息
		user = usermodel(self)
		userid = user.carduser(cardno,cardtype,cardid)
		if userid:
			uid = userid['user_id']
			uinfo = user.trueinfo( '', uid )
			charge = chargemodel(self)
			balance = charge.getpackage( uid )
			#金额计算
			fakemoney = int(money)*100
			newmoney = ( float(balance)*100+fakemoney ) / 100
			#当前时间
			nowtime = int(time.time())
			#订单号
			oid = user.build_order()
			#描述组合
			descript = seller['sellername']+u'用户'+uinfo['username']+'('+uinfo['nickname']+u')充值'+money
			log = logmodel(self)
			try:
				log.change_purse( newmoney, uid )
				log.save_order( oid, uid, money, nowtime, 'point', seller['sellername'] )
				log.save_payments( oid, sid, money, uid, descript, nowtime )
				log.commit_submit()
				self.finish( self.respone_data( 1 ) )
			except:
				self.finish( self.respone_data( 0, apimsg.notice(307) ) )
		else:
			self.finish( self.respone_data( 0, apimsg.notice(222) ) )


	def write_error(self, status_code, **kwargs):
		if status_code == 500:
			error = apimsg.notice(400)
		else:
			error = apimsg.notice(status_code)
		self.finish(self.respone_data( 0, error ))



#查询充值记录
class DepositList(webHandler):
	@seller_login
	def get(self):
		cardno = self.get_argument('cardno','')
		cardid = self.get_argument('cardid','')
		cardtype = self.get_argument('cardtype','')
		page = self.get_argument('page','1')
		per_page = self.get_argument('per_page','10')
		valid = validate()
		valid.Add( cardno,'识别码', ['Isdigit'] )
		valid.Add( cardid,'卡号', ['NoEmpty','Isdigit'] )
		valid.Add( cardtype,'卡分类', ['NoEmpty','Isdigit'] )
		valid.Add( page,'当前页', ['NoEmpty','Isdigit'] )
		valid.Add( per_page,'每页显示', ['NoEmpty','Isdigit'] )
		if not valid._CheckMate(): 
			self.finish( self.respone_data( 0, valid._Message() ) )
			return
		user = usermodel(self)
		userid = user.carduser(cardno,cardtype,cardid)
		charge = chargemodel(self)
		#查询条件
		if userid:
			where = {'user_id =':userid['user_id']}
			dlist = charge.savelist(where,int(page),int(per_page))
			if dlist:
				pinfo = charge.page_bar(2)
			else:
				dlist = []
				pinfo = {'this_page':1,'all_page':0,'all_num':0,'per_page':per_page}
			self.finish( self.respone_list( dlist, pinfo ) )
		else:
			self.finish( self.respone_data( 0, apimsg.notice(222) ) )

	def write_error(self, status_code, **kwargs):
		error = apimsg.notice(status_code)
		self.finish(self.respone_data( 0, error))



#我的充电列表
class RechargeList(webHandler):
	@seller_login
	def get(self):
		cardno = self.get_argument('cardno','')
		cardid = self.get_argument('cardid','')
		cardtype = self.get_argument('cardtype','')
		page = self.get_argument('page','1')
		per_page = self.get_argument('per_page','20')
		valid = validate()
		valid.Add( cardno,'识别码', ['NoEmpty','Isdigit'] )
		valid.Add( cardid,'卡号', ['NoEmpty','Isdigit'] )
		valid.Add( cardtype,'卡分类', ['NoEmpty','Isdigit'] )
		valid.Add( page,'当前页', ['NoEmpty','Isdigit'] )
		valid.Add( per_page,'每页显示', ['NoEmpty','Isdigit'] )
		if not valid._CheckMate():
			self.finish( self.respone_data( 0, valid._Message() ) )
			return
		user = usermodel(self)
		userid = user.carduser(cardno,cardtype,cardid)
		charge = chargemodel(self)
		#查询条件
		if userid:
			where = {'o.user_id =':userid['user_id'],'o.finish >':0}
			clist = charge.chargelist(where,int(page),int(per_page))
			if clist:
				pinfo = charge.page_bar(2)
			else:
				clist = []
				pinfo = {'this_page':1,'all_page':0,'all_num':0,'per_page':per_page}
			self.finish( self.respone_list( clist, pinfo ) )
		else:
			self.finish( self.respone_data( 0, apimsg.notice(222) ) )

	def write_error(self, status_code, **kwargs):
		error = apimsg.notice(status_code)
		self.finish(self.respone_data( 0, error))

#白卡
class BlankCard(webHandler):
	@seller_login
	def post(self):
		cardno = self.get_argument('cardno','')
		if cardno:
			card = cardmodel(self)
			#验证是否录入过
			cardinfo = card.show_card( cardno )
			if not cardinfo:
				#未录入则新加入
				cardinfo = card.blank_card( cardno )
			if cardinfo:
				self.finish(self.respone_data( 1, cardinfo))
			else:
				self.finish(self.respone_data( 0, apimsg.notice(307)))
		else:
			self.finish(self.respone_data( 0, apimsg.notice(400)))

	def write_error(self, status_code, **kwargs):
		error = apimsg.notice(status_code)
		self.finish(self.respone_data( 0, error))
