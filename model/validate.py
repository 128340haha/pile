# -*- coding: utf-8 -*-
import types
import re
from model.language import lang

"""
验证数据         把判断数据原样返回，把结果存储起来，最后一次性返回结果  就能够达到连等的效果
"""
class validate(): 
    def __init__(self):
        self.data = ''          #参数
        self.name = ''          #提示名
        self.token = True       #判断标示
        self.res = ''           #判断结果
        self.doll = ''          #函数出错标示
        self.message = []       #错误提示列表
        self.apimsg = lang()    #中文
    #    self._func = {'aw':self.aw,'ae':self.ae}
    def Add(self, data=None, name=None, condition=None, min=4, max=16):
        if data == None or name == None or condition == None:
            self.token = False
            self.message.append( self._Respone(10) )
            return 
        self.data = data
        self.name = str(name)
        self.max = max
        self.min = min
        if not self.IsList(condition, 2):
            self.token = False
            self.message.append( self._Respone(11) )
            return 
        for x in condition:
            if hasattr(self, x):
                func = getattr(self, x)
                func()
            else:
                self.token = False
                self.doll = x
                self.message.append( self._Respone(12,2) )

    def Same(self, newdata=None,name=None):
        self.name = str(name)
        if self.data == newdata:
            pass
        else:
            self.token = False
            self.message.append( self._Respone(207) )

    #强制字符数组
    def Isdigit(self):
        self.res = self.data.isdigit()
        if not self.res:
            self.token = False
            self.message.append( self._Respone(13) )

    #判断是否为整数 15
    def IsNumber(self):
        self.res =  type(self.data) is types.IntType
        if not self.res:
            self.token = False
            self.message.append( self._Respone(13) )
     
    #判断是否为字符串 string
    def IsString(self):
        self.res = type(self.data) is types.StringType
        if not self.res:
            self.token = False
            self.message.append(self._Respone(14))
     
    #判断是否为浮点数 1.324
    def IsFloat(self):
        self.res = type(self.data) is types.FloatType
        if not self.res:
            self.token = False
            self.message.append(self._Respone(15))
     
    #判断是否为字典 {'a1':'1','a2':'2'}
    def IsDict(self):
        self.res = type(self.data) is types.DictType
        if not self.res:
            self.token = False
            self.message.append(self._Respone(16))
     
    #判断是否为tuple元组 [1,2,3]
    def IsTuple(self):
        self.res = type(self.data) is types.TupleType
        if not self.res:
            self.token = False
            self.message.append(self._Respone(17))
     
    #判断是否为List列表 [1,3,4]
    def IsList(self, condition=None, model=1):
        if model == 1:
            self.res =  type(self.data) is types.ListType
            if not self.res:
                self.token = False
                self.message.append(self._Respone(18))
        elif model == 2:
            return type(condition) is types.ListType
        
    #判断是否为布尔值 True
    def IsBoolean(self):
        self.res = type(self.data) is types.BooleanType
        if not self.res:
            self.token = False
            self.message.append(self._Respone(19))
     
    #判断是否为货币型 1.32
    def IsCurrency(self):
        #数字是否为整数或浮点数
        self.IsFloat()
        self.Isdigit()
     
    #判断某个变量不为空 x
    def NoEmpty(self):
        if len( self.data ) == 0:
            self.token = False
            self.message.append(self._Respone(22))
    
    #判断变量是否为None None
    def IsNone(self):
        self.res = type(self.data) is types.NoneType
        if not self.res:
            self.token = False
            self.message.append(self._Respone(23))
            # == "None" or self.data == "none":
     
    #判断是否为日期格式,并且是否符合日历规则 2010-01-31
    def IsDate(self):
        if len(self.data) == 10:
            rule = '(([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8]))))|((([0-9]{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))-02-29)$/'
            match = re.match( rule , self.data )
            if match:
                return
        self.token = False
        self.message.append(self._Respone(24))
     
    #判断是否为邮件地址
    def IsEmail(self):
     
        rule = '[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$'
        match = re.match( rule , self.data )
     
        if match:
            pass
        else:
            self.token = False
            self.message.append(self._Respone(25))
     
    #判断是否为中文字符串
    def IsChineseCharString(self):
     
        for x in self.data:
            if (x >= u"\u4e00" and x<=u"\u9fa5") or (x >= u'\u0041' and x<=u'\u005a') or (x >= u'\u0061' and x<=u'\u007a'):
               continue
            else:
               self.token = False
               self.message.append(self._Respone(26))
               break
     
     
    #判断是否为中文字符
    def IsChineseChar(self):
     
        if self.data[0] > chr(127):
           return
        self.token = False
        self.message.append(self._Respone(27))
     
    #判断帐号是否合法 字母开头，允许4-16字节，允许字母数字下划线
    def IsLegalAccounts(self):
        #[a-zA-Z][a-zA-Z0-9_]
        rule = '[a-zA-Z0-9_]{'+str(self.min)+','+str(self.max)+'}$'
        match = re.match( rule , self.data )
        if match:
            return
        self.token = False
        self.message.append( self._Respone(29,3,self.min,self.max) )
     
    #字符长度限制
    def IsAccessLen(self):
        length = len( str(self.data) )
        if length >= self.min and length <= self.max:
            return
        self.token = False
        self.message.append( self._Respone(29,4,self.min) )
     
     
    #匹配IP地址
    def IsIpAddr(self):
     
        rule = '\d+\.\d+\.\d+\.\d+'
        match = re.match( rule , self.data )
     
        if match:
            return
        self.token = False
        self.message.append(self._Respone(28))
    
    def _Respone(self,code=999,model=1,min=0,max=0):
        if model == 1: 
            str = self.name+self.apimsg.notice(code)
        elif model == 2:
            str = self.doll+self.apimsg.notice(code)
        elif model == 3:
            str = "%s%s,必须%d-%d字符" %(self.name, self.apimsg.notice(code), min, max)#self.name+self.apimsg.notice(code)+'允许'+str(min)+'-'+str(max)+'字符'
        elif model == 4:
            str = "%s%s,必须%d字符" %(self.name, self.apimsg.notice(code), min)
        return str
    #统计结果
    def _CheckMate(self):
        return self.token
            
    #错误提示
    def _Message(self):
        respone = ','.join( self.message )
        return respone
