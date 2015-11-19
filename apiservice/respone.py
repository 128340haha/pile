# -*- coding: utf-8 -*-
from public import *
from model.validate import validate
from model.chargemodel import *
from model.language import lang
import time
apimsg = lang()        #文字类

#生成订单
class ChargOrder(apiHandler):
	@api_token
	def post(self):
		code = self.get_argument('code','')
		cardno = self.get_argument('cardno','')
		cardid = self.get_argument('cardid','')
		cardtype = self.get_argument('cardtype','')
		price = self.get_argument('price','')
		post_data = {}
		# for key in self.request.arguments:
		#     post_data[key] = self.get_arguments(key)
		# print post_data
		if not price or float(price) < 0.5:
			self.finish('2')
			return
		charge = chargemodel(self)
		#验证电桩是否存在
		device = charge.device_info( code )
		if device:
			#设备存在 则验证卡
			uinfo = charge.user_card( cardno,cardtype,cardid )
			if uinfo:
				#订单唯一性
				only = charge.only_order(uinfo['id'])
				if not only:
					self.finish('3')
					return
				#卡也存在
				thistime = int(time.time())
				order = charge.make_order(uinfo['id'],code,thistime,price)
				if order:
					self.finish('1')
					return
		self.finish('0')

	def write_error(self, status_code, **kwargs):
		self.finish('403')


#充电完成返回页面
class ChargEnd(apiHandler):
	@api_token
	def post(self):
		code = self.get_argument('code','')
		cardno = self.get_argument('cardno','')
		cardid = self.get_argument('cardid','')
		cardtype = self.get_argument('cardtype','')
		pay = self.get_argument('pay','')			#冻结(消费)金额
		elec = self.get_argument('elec','')			#电量
		finish = self.get_argument('finish','')		#订单完成状态
		acttime = self.get_argument('acttime','')	#耗时
		#检查是否有冻结资金
		if float( pay ) < 0:
			#没冻结资金
			self.finish('2')
			return
		charge = chargemodel(self)
		#电桩找到绑定用户
		user = charge.user_card( cardno,cardtype,cardid )
		#用户等待订单只能有一个
		if user:
			status = charge.once_order( user['id'], code )
			#订单数量异常
			if not status:
				#状态
				self.finish('3')
				return
			#结算
			param = {'code':code,'pay':float(pay),'elec':float(elec),'finish':int(finish),'acttime':int(acttime)}
			res = charge.account( **param )
			if res:
				self.finish('1')
				return
		self.finish('0')

	def write_error(self, status_code, **kwargs):
		self.finish('403')
