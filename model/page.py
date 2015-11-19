# -*- coding: utf-8 -*-
from config import setting
import urllib,types,math
 
class pagemodel():
	def __init__(self):
		self.all_num = 0
		self.per_page = 10
		self.all_page = 0
		self.this_page = 1

	def make_page(self,number,page=1,per_page=False):
		if number <= 0:
			return 0

		page = int(page) if page else 1

		#当前页最小值
		if page < 0 or type(page) is not types.IntType:
			page = 1

		self.all_num = int(number)
		self.per_page = int(per_page) if per_page else self.per_page

		#一共多少页
		self.all_page = int( math.ceil( float(number) / self.per_page ) )
		if page > self.all_page:
			page = self.all_page

		#当前页
		self.this_page = page
		return per_page * ( page - 1 )

	def make_bar(self,url='',number=2,key='page' ):
		if self.all_page <= 1:
			return []
		left_bar = []
		right_bar = []
		#url判断
		if "?" not in url:
			url = url+'?'
		else:
			#替换key的分页参数
			start = url.find('?')
			host = url[0:start]
			param = url[start+1:]
			param_list = self.urldecode( param )
			try:
				del param_list[key]
			except KeyError:
				pass
			url = host+'?'+urllib.urlencode( param_list )
			
		#左边
		if self.this_page == 1:
			#第一页强制无左
			left = 0
		elif self.this_page > number:
			#当前页大于显示页,按number全显
			left = number
		else:
			#当前页小于显示页面,按本页-1全显
			left = self.this_page - 1
		#右边
		if self.all_page <= self.this_page:
			#最大页面左边不写
			right = 0
		elif self.all_page - self.this_page > number:
			#右边的页数有多的
			right = number
		else:
			#右边页数不够多
			right = self.all_page - self.this_page
		#顶头显示则填充
		if left < number:
			#最大增值
			maxright = self.all_page - self.this_page
			right += number - left
			if right > maxright:
				right = maxright
		elif right < number:
			maxleft = self.this_page - 1
			left += number - right
			if left > maxleft:
				left = maxleft

		#综合参数
		#if param:
		#	param = urllib.urlencode( param )

		#循环输出左边
		sign = {'first':str(url)+'&'+key+'=1','last':str(url)+'&'+key+'='+str(self.all_page)}
		for i in range(left,0,-1):
			l = self.this_page - i
			if i == 1:
				sign['prev'] = str(url)+'&'+key+'='+str(l)
			left_bar.append( {'page':l,'url':str(url)+'&'+key+'='+str(l)} )

		#当前页
		_this = {'page':self.this_page,'url':'javascript:void(0)'}
		#输出右边
		next = ''
		for c in range(1,right+1):
			r = self.this_page + c
			if c == 1:
				sign['next'] = str(url)+'&'+key+'='+str(r)
			right_bar.append( {'page':r,'url':str(url)+'&'+key+'='+str(r)} )

		return {'left_bar':left_bar,'this_page':_this,'right_bar':right_bar,'sign':sign}


	def urldecode(self,query):
		d = {}
		a = query.split('&')
		for s in a:
			if s and s.find('='):
				k,v = map(urllib.unquote, s.split('='))
				#try:
				#	d[k].append(v)
				#except KeyError:
				d[k] = v
		return d

	def page_info(self):
		res = {
			'all_num'	:	self.all_num,
			'per_page'	:	self.per_page,
			'all_page'	:	self.all_page,
			'this_page'	:	self.this_page
		}
		return res


	def write_error(self, status_code, **kwargs):
	    title = 'error'
	    self.render("hello.html", title='error')
