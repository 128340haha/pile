# -*- coding: utf-8 -*-
from model.language import lang
from config import setting
import time
from decimal import *

class mapmodel():
	def __init__(self,obj):
		self.obj = obj
		self.apimsg = lang()

	def mygps(self,openid):
		#待定
		return None

		if openid:
			sql = "SELECT latitude,longitude,`precision` FROM wechat_user WHERE openid = %s"
			res = self.obj.db.get( sql, openid )
			return res
		else:
			return None


	def area_device(self,latitude,longitude, model='1'):
		getcontext().prec = 6
		if model == '1':
			constant = 0.05
		elif model == '2':
			constant = 0.1
		elif model == '3':
			constant = 0.15
		elif model == '4':
			constant = 0.2
		n = Decimal(latitude) + Decimal(constant)
		s = Decimal(latitude) - Decimal(constant)
		w = Decimal(longitude) - Decimal(constant)
		e = Decimal(longitude) + Decimal(constant)  
		limit = int(time.time()) - 120
		sql = "SELECT name,status,latitude,longitude FROM device WHERE isopen = 1 AND heart_time > %s AND latitude <= %s AND latitude >= %s AND longitude <= %s AND longitude >= %s "
		res = self.obj.db.query( sql %( limit, n, s, e, w ) )
		for v in res:
			v['latitude'] = '%.6f' %v['latitude']
			v['longitude'] = '%.6f' %v['longitude']
		return res


	def __del__(self):
		self.obj.db.close()