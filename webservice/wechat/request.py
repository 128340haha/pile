# -*- coding: utf-8 -*-
from public import *
from model.validate import validate
from model.chargemodel import *
from model.usermodel import *
import time,re
from model.language import lang

apimsg = lang()        #文字类

class wechat_respone(webHandler):
	def get(self):
		token = ''
		pass

	def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error) 

class alipay_respone(webHandler):
	def get(self):
		pass

	def write_error(self, status_code, **kwargs):
        error = apimsg.notice(status_code)
        self.render("wechat/error.html", code=status_code, error=error) 


