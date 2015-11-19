# -*- coding: utf-8 -*-
from public import *
from model.validate import validate
from model.cardmodel import *
from model.usermodel import *
from model.chargemodel import *
import time
from config import setting
from model.language import lang

apimsg = lang()        #文字类

#新卡
class NewCard(apiHandler):
	@seller_token
	def post(self):
		cardtype = self.get_argument('cardtype','')
		cardno = self.get_argument('cardno','')
		nickname = self.get_argument('nickname','')
		phone = self.get_argument('phone','')
		balance = self.get_argument('balance','')
		valid = validate()
		valid.Add( cardtype,'分类', ['NoEmpty','Isdigit'] )
		valid.Add( cardno,'识别码', ['NoEmpty','Isdigit'] )
		valid.Add( phone,'手机', ['NoEmpty','Isdigit'],11,11 )
		if not valid._CheckMate():
			self.finish( self.respone_data( 0, valid._Message() ) )
			return
		user = usermodel(self)
		username = user.used_name()
		res = user.register(username=username,password=username,cardno=cardno,cardtype=cardtype)
		id = user.get_insert_id()
		if res and id:
			#更改电话
			user.editinfo('phone',phone,username)
			if nickname:
				user.editinfo('nickname',nickname,username)
			card = cardmodel(self)
			where = "where c.user_id = %s" %id
			info = card.card_infomation( where ) 
			#新卡充值
			ser.purse_edit( id=id, balance=balance )
			#返回数据
			self.finish( self.respone_data( 1, info ) )
		else:
			self.finish( self.respone_data( 0, apimsg.notice(307) ) )

	def write_error(self, status_code, **kwargs):
		error = apimsg.notice(status_code)
		self.finish(self.respone_data( 0, error))

#更改信息
class ChangeInfo(apiHandler):
	@seller_token
	def post(self):
		cardno = self.get_argument('cardno','')
		cardnumber = self.get_argument('cardnumber','')
		nickname = self.get_argument('cardnumber','')
		phone = self.get_argument('phone','')
		idcard = self.get_argument('idcard','')
		valid = validate()
		valid.Add( cardno,'识别码', ['NoEmpty','Isdigit'] )
		valid.Add( cardnumber,'卡号', ['NoEmpty','Isdigit','IsAccessLen'], 12, 12 )
		user = usermodel(self)
		cardtype = int(cardnumber[0:4])
		cardid = int(cardnumber[4:])
		userid = user.carduser(cardno,cardtype,cardid)
		res = user.uinfo_edit(nickname=nickname,phone=phone,idcard=idcard,mail='',sex=1,id=userid['user_id'])
		if res:
			self.finish( self.respone_data( 1, ) )
		else:
			self.finish( self.respone_data( 0, apimsg.notice(307) ) )

#改变钱
class ChangeBalance(apiHandler):
	@seller_token
	def post(self):
		cardno = self.get_argument('cardno','')
		cardnumber = self.get_argument('cardnumber','')
		money = self.get_argument('money',0)
		valid = validate()
		valid.Add( cardno,'识别码', ['NoEmpty','Isdigit'] )
		valid.Add( cardnumber,'卡号', ['NoEmpty','Isdigit','IsAccessLen'], 12, 12 )
		valid.Add( float(money),'钱数', ['NoEmpty','IsFloat'] )
		if not valid._CheckMate():
			self.finish( self.respone_data( 0, valid._Message() ) )
			return
		user = usermodel(self)
		cardtype = int(cardnumber[0:4])
		cardid = int(cardnumber[4:])
		userid = user.carduser(cardno,cardtype,cardid)
		charge = chargemodel(self)
		balance = charge.getpackage( userid['user_id'] )
		money = int(float(money)*100)
		newmoney = float(balance)*100+float(money)
		res = user.purse_edit( id=userid['user_id'], balance=newmoney/100 )
		if res == '1':
			self.finish( self.respone_data( 1 ) )
		else:
			self.finish( self.respone_data( 0, apimsg.notice(307) ) )

	def write_error(self, status_code, **kwargs):
		if status_code == 500:
			error = apimsg.notice(400)
		else:
			error = apimsg.notice(status_code)
		self.finish(self.respone_data( 0, error ))


#卡列表
class CardList(apiHandler):
	@seller_token
	def get(self):
		cardtype = self.get_argument('cardtype','')
		page = self.get_argument('page','1')
		per_page = self.get_argument('per_page','10')
		where = ' where u.status < 2 '
		valid = validate()
		valid.Add( page,'当前页', ['NoEmpty','Isdigit'] )
		valid.Add( per_page,'每页显示', ['NoEmpty','Isdigit'] )
		if not valid._CheckMate():
			self.finish( self.respone_data( 0, '分页参数异常' ) )
			return
		if cardtype:
			valid.Add( cardtype,'分类', ['Isdigit'] )
			if not valid._CheckMate():
				self.finish( self.respone_data( 0, valid._Message() ) )
				return
			where += " AND c.cardtype = %d" %int(cardtype)
		card = cardmodel(self)
		clist = card.card_list( where, int(page), int(per_page) )
		if clist:
			pinfo = card.page_bar(2)
		else:
			clist = []
			pinfo = {'this_page':1,'all_page':0,'all_num':0,'per_page':per_page}
		self.finish( self.respone_list( clist, pinfo ) )


	def write_error(self, status_code, **kwargs):
		error = apimsg.notice(status_code)
		self.finish(self.respone_data( 0, error))

#查询卡片信息
class CardInfo(apiHandler):
	@seller_token
	def get(self):
		cardno = self.get_argument('cardno','')
		cardnumber = self.get_argument('cardnumber','')
		where = ' where u.status < 2 '
		valid = validate()
		valid.Add( cardno,'识别码', ['NoEmpty','Isdigit'] )
		valid.Add( cardnumber,'卡号', ['NoEmpty','Isdigit','IsAccessLen'], 12, 12 )
		if not valid._CheckMate():
			self.finish( self.respone_data( 0, valid._Message() ) )
			return
		#识别码
		where += " AND c.cardno = %d" %int(cardno)
		cardtype = int(cardnumber[0:4])
		cardid = int(cardnumber[4:])
		#卡号
		where += " AND c.cardtype = %d AND c.cardid = %d" %(cardtype,cardid)
		card = cardmodel(self)
		info = card.card_infomation( where ) 
		self.finish( self.respone_data( 1, info ) )

	def write_error(self, status_code, **kwargs):
		error = apimsg.notice(status_code)
		self.finish(self.respone_data( 0, error))

#查询充电记录
class ChargeList(apiHandler):
	@seller_token
	def get(self):
		cardno = self.get_argument('cardno','')
		cardnumber = self.get_argument('cardnumber','')
		start = self.get_argument('start','')
		end = self.get_argument('end','')
		page = self.get_argument('page','1')
		per_page = self.get_argument('per_page','10')
		valid = validate()
		valid.Add( cardno,'识别码', ['Isdigit'] )
		valid.Add( cardnumber,'卡号', ['Isdigit','IsAccessLen'], 12, 12 )
		valid.Add( page,'当前页', ['NoEmpty','Isdigit'] )
		valid.Add( per_page,'每页显示', ['NoEmpty','Isdigit'] )
		if not valid._CheckMate():
			self.finish( self.respone_data( 0, valid._Message() ) )
			return
		user = usermodel(self)
		cardtype = int(cardnumber[0:4])
		cardid = int(cardnumber[4:])
		userid = user.carduser(cardno,cardtype,cardid)
		charge = chargemodel(self)
		#查询条件
		if userid:
			where = {'o.user_id =':userid['user_id'],'o.finish >':0}
			if start and start.isdigit():
				where['o.creatime >='] = start
			if end and end.isdigit():
				where['o.creatime <='] = end
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


#查询充值记录
class DepositList(apiHandler):
	@seller_token
	def get(self):
		cardno = self.get_argument('cardno','')
		cardnumber = self.get_argument('cardnumber','')
		start = self.get_argument('start','')
		end = self.get_argument('end','')
		page = self.get_argument('page','1')
		per_page = self.get_argument('per_page','10')
		valid = validate()
		valid.Add( cardno,'识别码', ['Isdigit'] )
		valid.Add( cardnumber,'卡号', ['Isdigit','IsAccessLen'], 12, 12 )
		valid.Add( page,'当前页', ['NoEmpty','Isdigit'] )
		valid.Add( per_page,'每页显示', ['NoEmpty','Isdigit'] )
		if not valid._CheckMate():
			self.finish( self.respone_data( 0, valid._Message() ) )
			return
		user = usermodel(self)
		cardtype = int(cardnumber[0:4])
		cardid = int(cardnumber[4:])
		userid = user.carduser(cardno,cardtype,cardid)
		charge = chargemodel(self)
		#查询条件
		if userid:
			where = {'user_id =':userid['user_id']}
			if start and start.isdigit():
				where['acttime >='] = start
			if end and end.isdigit():
				where['acttime <='] = end
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


#分类
class CardType(apiHandler):
	@seller_token
	def get(self):
		card = cardmodel(self)
		type_list = card.card_type()
		if not type_list:
			type_list = []
		pinfo = {}
		self.finish( self.respone_list( type_list, pinfo ) )