# -*- coding: utf-8 -*-
from public import *
from model.validate import validate
from model.mapmodel import *
from model.language import lang
import json
apimsg = lang()        #文字类

class MapHandler(webHandler):
	@access_token
	def get(self):
		openid = self.get_secure_cookie('openid')
		if not openid or openid == 'None':
			code = self.get_argument('code','')
			openid = self.rd.get('code:'+code)
			if not openid or openid == 'None':
				#redis依然无法获取openid
				self.write_error(2)

		access_token = self.get_access_token()
		param = self.get_signature( access_token )
		self.render("wechat/map.html",param=param)

	def write_error(self, status_code, **kwargs):
		error = apimsg.notice(status_code)
		self.render("wechat/error.html", code=status_code, error=error)

class NearbyDevice(webHandler):
	@access_token
	def post(self):
		openid = self.get_secure_cookie('openid')
		if not openid or openid == 'None':
			code = self.get_argument('code','')
			openid = self.rd.get('code:'+code)
			if not openid or openid == 'None':
				#redis依然无法获取openid
				self.write( 'openid丢失,查询失败' )
				return
		latitude = self.get_argument('latitude','')
		longitude = self.get_argument('longitude','')
		model = self.get_argument('range','1')
		maps = mapmodel(self)
		dlist = {}
		if latitude and longitude:
			dlist = maps.area_device( latitude,longitude, model )
			self.write( json.dumps(dlist) )
		else:
			self.write( 0 )