# -*- coding: utf-8 -*-
import apiservice.handlers as apihand
import apiservice.user as apiuser
import apiservice.respone as respone
import apiservice.webserver as websv
import apiservice.card as apicard

#import apiservice.webserver as webserver
import webservice.wechat.index as wechatindex
import webservice.wechat.user as wechatuser
import webservice.wechat.recharge as recharge
import webservice.wechat.map as maps

import webservice.home.index as homeindex
import webservice.home.respone as homerespone
import webservice.point.index as point

import webservice.admin.administrator as adm
import webservice.admin.user as aduser
import webservice.admin.card as card
import webservice.admin.device as dev

url = [(r'/api/index', apihand.IndexHandler),
       (r'/api/access_token', websv.AccessToken), 
       #站点接口
       (r'/api/user_login', apiuser.UserLoginHandler),
       (r'/api/card_list', apicard.CardList),
       (r'/api/card_type', apicard.CardType),
       (r'/api/card_info', apicard.CardInfo),
       (r'/api/charge_list', apicard.ChargeList),
       (r'/api/deposit_list', apicard.DepositList),
       (r'/api/new_card', apicard.NewCard),
       (r'/api/change_balance', apicard.ChangeBalance),

       #结算
       (r'/charg_order', respone.ChargOrder),
       (r'/charg_end', respone.ChargEnd),  


       #微信
       (r'/token', wechatindex.TokenHandler),
       (r'/share', wechatindex.ShareHandler),
       (r'/clear', wechatindex.Clear),
       (r'/test', wechatindex.Test),         #test

       #(r'/', wechatindex.IndexHandler),
       (r'/wechat', wechatindex.IndexHandler),
       (r'/login', wechatuser.LoginHandler),
       (r'/act_login', wechatuser.ActLogin),
       (r'/act_cancel', wechatuser.ActCancel),
       (r'/act_onebind', wechatuser.ActOnebind),
       (r'/register', wechatuser.RegisterHandler),
       (r'/act_reg', wechatuser.ActRegister),
       (r'/ucenter', wechatuser.UcenterHandler),
       (r'/act_info', wechatuser.ActUinfo),
       (r'/deposit', recharge.DepositHandler),
       (r'/recharge', recharge.RechargeHandler),
       (r'/act_pile', recharge.ActSelectPile),
       (r'/combo', recharge.ComboHandler),
       (r'/act_charge', recharge.ActRecharge),
       (r'/map', maps.MapHandler),
       (r'/near_dev', maps.NearbyDevice),
       (r'/charge_detail', recharge.DetailHandler),
       (r'/device_notice', recharge.DeviceNotice),
       (r'/charging', recharge.ChargingHandler),
       (r'/charg_socket', recharge.ChargeSocket),
       (r'/stop_charge', recharge.StopCharging),

       (r'/deposit_list', recharge.DepositLogHandler),
       (r'/recharge_list', recharge.RechargeLogHandler),
       (r'/more_charge', recharge.MoreRecharge),

       #后台列表
       (r'/admin', adm.LoginHandler),
       (r'/admin/', adm.LoginHandler),
       (r'/admin/login', adm.LoginHandler),
       (r'/admin/act_login', adm.ActLogin),
       (r'/admin/layout', adm.Layout),
       (r'/admin/index', adm.IndexHandler),
       (r'/admin/welcome', adm.WelcomeHandler),
       (r'/admin/newadmin', adm.NewadminHandler),
       (r'/admin/admin_list', adm.AdminListHandler),
       (r'/admin/edit_admin', adm.EditAdminHandler),
       (r'/admin/delete_admin', adm.DeleteAdmin),
       (r'/admin/act_admin', adm.ActAdmin),
       (r'/admin/ac_nickname', adm.AdminChangeNickname),

       (r'/admin/setting', adm.SettingHandler),
       (r'/admin/act_set', adm.ActSetting),
       (r'/admin/user_list', aduser.UserListHandler),
       (r'/admin/user_status', aduser.UserStatus),
       (r'/admin/user_delete', aduser.UserDelete),
       (r'/admin/user_reset', aduser.UserResetHandler),
       (r'/admin/act_reset', aduser.ActReset),
       (r'/admin/user_details', aduser.UserDetailsHandler),
       (r'/admin/act_property', aduser.ActProperty),
       (r'/admin/add_user', aduser.AddUserHandler),
       (r'/admin/act_newuser', aduser.ActNewUser),
       (r'/admin/recharge_list', aduser.RechargeHandler),
       (r'/admin/deposit_list', aduser.DepositHandler),
       (r'/admin/recharge_delete', aduser.ActDelRecharge),
       (r'/admin/recharging', aduser.WorkOrderHandler),
       (r'/admin/recycle', aduser.RecycleHandler),
       (r'/admin/kill_live', aduser.KillLive),
       (r'/admin/order_end', aduser.OrderEnd),

       (r'/admin/card_list', card.CardListHandler),
       (r'/admin/card_type', card.CardTypeHandler),
       (r'/admin/new_type', card.NewTypeHandler),
       (r'/admin/edit_type', card.EditTypeHandler),
       (r'/admin/change_asc', card.ChangeAsc),
       (r'/admin/act_type', card.TypeAction),
       (r'/admin/delete_type', card.DeleteType),
       (r'/admin/new_card', card.NewCardHandler),
       (r'/admin/add_card', card.AddCard),
       (r'/admin/delete_card', card.DeleteCard),
       (r'/admin/card_seller', card.CardSeller),
       (r'/admin/seller_status', card.SellerStatus),
       (r'/admin/delete_seller', card.DeleteSeller),
       (r'/admin/new_seller', card.NewSellerHandler),
       (r'/admin/edit_seller', card.EditSellerHandler),
       (r'/admin/act_seller', card.ActSeller),
       (r'/admin/ac_duty', card.ActDuty),
       (r'/admin/seller_records', card.SellerRecord),

       (r'/admin/device_list', dev.DeviceListHandler),
       (r'/admin/new_device', dev.NewDeviceHandler),
       (r'/admin/edit_device', dev.EditDeviceHandler),
       (r'/admin/open_device', dev.OpenDevice),
       (r'/admin/act_device', dev.ActDevice),
       (r'/admin/delete_device', dev.DeleteDevice),   
       (r'/admin/error_device', dev.DeviceErrorHandler),

       #前台
       (r'/', homeindex.IndexHandler),
       (r'/user', homeindex.IndexHandler),
       (r'/user/', homeindex.IndexHandler),
       (r'/user/index', homeindex.IndexHandler),
       (r'/user/about', homeindex.AboutHandler),
       (r'/user/partner', homeindex.PartnerHandler),
       (r'/user/ucenter', homeindex.UsercenterHandler),
       (r'/user/cardlogin', homeindex.CardLogin),
       (r'/user/charge_list', homeindex.ChargeList),
       (r'/user/save_list', homeindex.SaveList),
       (r'/user/update_info', homeindex.UpdateInfo),
       (r'/user/order_info', homeindex.OrderInfo),
       (r'/user/use_alipay', homeindex.UseAlipay),

       #支付宝访问
       (r'/respone/alipay_return', homerespone.AlipayReturn),
       (r'/respone/alipay_notify', homerespone.AlipayNotify),
       (r'/respone/welcome', homerespone.Welcome),
                     
       #嵌套
       (r'/point/login', point.LoginHandler),
       (r'/point/ac_login', point.ActLogin),
       (r'/point/index', point.IndexHandler),
       (r'/point/card', point.CardInfo),
       (r'/point/edit_card', point.EditCard),
       (r'/point/recharge_list', point.RechargeList),
       (r'/point/deposit_list', point.DepositList),
       (r'/point/blank_card', point.BlankCard),
       (r'/point/reg_card', point.RegCard),
       (r'/point/change_balance', point.ChangeBalance),
       (r'/point/print', point.Print),

       #公共函数列表
       (r'/tips', wechatindex.TipsHandler),
       (r'/notice', adm.NoticeHandler),
       (r'/validcode', wechatuser.ValidCode),
       (r".*", apihand.ErrorHandler)]

uimodules={
       'Hello': wechatindex.HelloModule,
       'admin_head': adm.AdminHeadModule,
       'admin_foot': adm.AdminFootModule,

       }