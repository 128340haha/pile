# -*- coding: utf-8 -*-
setting = {
    'secretkey'             :   'so',        #加秘钥
    'cookie_secret'         :   'reload',       #cookie加密
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
    'captcha_id'            :   "",
    'private_key'           :   "",
    'product'               :   "popup&popupbtnid=submit-button",

    #微信
    'appid'                 :   "",
    'appsecret'             :   "",

    #内部API通信秘钥
    'apikey'                :   "",

    #电桩数据获取地址
    'from_address'          :   "xxxxxx.com",
    'from_port'             :   9999,

    #支付宝相关
    'ALIPAY_KEY'            :   '',   # 安全检验码，以数字和字母组成的32位字符
    'ALIPAY_INPUT_CHARSET'  :   'utf-8',             #编码  
    'ALIPAY_PARTNER'        :   '',  # 合作身份者ID，以2088开头的16位纯数字
    'ALIPAY_SELLER_EMAIL'   :   '',  # 签约支付宝账号或卖家支付宝帐户
    'ALIPAY_SIGN_TYPE'      :   'MD5',               #加密方式
    # 付完款后跳转的页面（同步通知） 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
    'ALIPAY_RETURN_URL'     :   'http://www.xxxxxx.com/alipay_return',
    # 交易过程中服务器异步通知的页面 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
    'ALIPAY_NOTIFY_URL'     :   'http://www.xxxxxx.com/alipay_notify'

}