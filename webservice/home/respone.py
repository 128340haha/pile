# -*- coding: utf-8 -*-
from public import *
from model.logmodel import *
from libraries.alipay import *
import time

#确认支付
class pay(webHandler):
    def get(request):
        cbid=request.POST.get('id')
        try:
            cb=cBill.objects.get(id=cbid)
        except ObjectDoesNotExist:
            return self.redirect("/respone/error")
        
        #如果网关是支付宝
        if cb.cbank.gateway=='alipay':
                tn=cb.id
                subject=''
                body=''
                bank=cb.cbank.id
                tf='%.2f' % cb.amount
                url=create_direct_pay_by_user (tn,subject,body,bank,tf)

        #如果网关是财付通
        elif cb.cbank.gateway=='tenpay':
            pass
        
        #去支付页面
        return self.redirect (url)

#alipay异步通知
class AlipayNotify(apiHandler):
    def post (self):
        post = data_format( self.request.body_arguments )
        log = logmodel(self)
        #清除过期单据
        log.expire_alipay()
        if notify_verify (post):
            #商户网站订单号
            tn = self.get_body_argument('out_trade_no')
            #支付宝单号
            trade_no = self.get_body_argument('trade_no')
            #返回支付状态
            trade_status = self.get_body_argument('trade_status')
            #返回状态判断
            if trade_status == 'TRADE_SUCCESS' or trade_status == 'TRADE_FINISHED':
                log = logmodel(self)
                info = log.log_info( 'log_alipay', tn )
                if info and info['ispay'] == 0:
                    #修改状态并且生成完整订单
                    try:
                        nowtime = int(time.time())
                        log.success_alipay( tn, nowtime, trade_no )
                        log.save_order( tn, info['user_id'], info['amount'], nowtime, 'alipay', '用户中心' )
                        #更改钱数
                        log.change_purse( info['balance']+info['amount'], info['user_id'] )
                        log.commit_submit()
                        self.finish("success")
                    except:
                        return self.finish("fail")
                elif info and info['ispay'] == 1:
                    self.finish("success")
                else:
                    self.finish("fail")
            else:
                #写入日志
                #log=Log(operation='notify2_'+trade_status+'_'+trade_no)
                #log.save()
                print 'fail'
                self.finish("fail")
        else:
            #黑客攻击
            #log=Log(operation='hack_notify_'+trade_status+'_'+trade_no+'_'+'out_trade_no')
            #log.save()
            self.finish ("fail")

    def write_error(self, status_code, **kwargs):
        return self.finish ("fail")

#同步通知
class AlipayReturn(webHandler):
    def get (self):
        #print self.request.query_arguments      
        #self.get_body_arguments('abc')\
        get = data_format( self.request.query_arguments )
        if notify_verify (get):
            tn = self.get_query_argument('out_trade_no')
            trade_no = self.get_query_argument('trade_no')
            trade_status = self.get_query_argument('trade_status')
            #获取订单状态
            log = logmodel(self)
            info = log.log_info( 'log_alipay', tn )
            if info and info['ispay'] == 0:
                #修改状态并且生成完整订单
                try:
                    nowtime = int(time.time())
                    #更改记录信息
                    log.success_alipay( tn, nowtime, trade_no )
                    #存储订单记录
                    log.save_order( tn, info['user_id'], info['amount'], nowtime, 'alipay', '用户中心' )
                    #更改钱数
                    log.change_purse( info['balance']+info['amount'], info['user_id'] )
                    log.commit_submit()
                    self.render("home/welcome.html",oid=tn,amount=info['amount'])
                except:
                    self.finish("fail")
            elif info and info['ispay'] == 1:
                self.render("home/welcome.html",oid=tn,amount=info['amount'])
            else:
                self.finish("fail")
        else:
            #错误或者黑客攻击
            #log=Log(operation='err_return_'+trade_status+'_'+trade_no)
            #log.save()
            self.finish("fail")

    def write_error(self, status_code, **kwargs):
        self.finish("fail")

class Welcome(webHandler):
    def get(self):
        self.render("home/welcome.html",oid=21511101400019,amount=30)


#外部跳转回来的链接session可能丢失，无法再进入系统。
#客户可能通过xxx.com操作，但是支付宝只能返回www.xxx.com，域名不同，session丢失。
def verify(request,cbid):
    try:
        cb=cBill.objects.get(id=cbid)
        #如果订单时间距现在超过1天，跳转到错误页面！
        #避免网站信息流失
        
        return render_to_response('public_verify.html',{'cb':cb},RequestContext(request))
    except ObjectDoesNotExist:
        return self.redirect("/respone/error")