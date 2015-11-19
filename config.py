# -*- coding: utf-8 -*-
setting = {
    'secretkey'             :   'myhome_so',        #加秘钥
    'cookie_secret'         :   '_reloading',       #cookie加密
    'keyexpire'             :   7200,               #token过期时间
    'redisexpire'           :   7200,               #redis过期时间
    'register'              :   True,               #是否开放注册
    'login'                 :   True ,              #开放登录  
    'autojump'              :   3,                  #自动跳转时间(秒) 待定
    
    'host'                  :   "127.0.0.1",        #数据库相关
    'database'              :   "charge", 
    'user'                  :   "root", 
    'password'              :   "123456",

    #注册验证码功能
    'BASE_URL'              :   "api.geetest.com/get.php?gt=",
    'captcha_id'            :   "99a64132ba91123df60df0f8e9092dba",
    'private_key'           :   "4e3c22d452e2af1a2296170e4e32b922",
    'product'               :   "popup&popupbtnid=submit-button",

    #微信
    'appid'                 :   "wx8aba6b9463a6e2b3",
    'appsecret'             :   "aa3f69ef8a4b31ed60b0bc2c45de9d8a",

    #内部API通信秘钥
    'apikey'                :   "56cfd1f161e08b8be92f4f7e46d72825",

    #电桩数据获取地址
    'from_address'          :   "mdznbs.com",
    'from_port'             :   9999,

    #支付宝相关
    'ALIPAY_KEY'            :   'au4sp5k99dx2r2gu4pt5icvj0auekml1',   # 安全检验码，以数字和字母组成的32位字符
    'ALIPAY_INPUT_CHARSET'  :   'utf-8',             #编码  
    'ALIPAY_PARTNER'        :   '2088021732117541',  # 合作身份者ID，以2088开头的16位纯数字
    'ALIPAY_SELLER_EMAIL'   :   '517890171@qq.com',  # 签约支付宝账号或卖家支付宝帐户
    'ALIPAY_SIGN_TYPE'      :   'MD5',               #加密方式
    # 付完款后跳转的页面（同步通知） 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
    'ALIPAY_RETURN_URL'     :   'http://www.mdznbs.com/respone/alipay_return',
    # 交易过程中服务器异步通知的页面 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
    'ALIPAY_NOTIFY_URL'     :   'http://www.mdznbs.com/respone/alipay_notify'

}