import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
import torndb
from routes import url,uimodules
from config import setting
import redis

sys.executable = './bin/python'
reload(sys)
sys.setdefaultencoding("utf-8")
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        self.db = torndb.Connection(host=setting['host'], database=setting['database'], user=setting['user'], password=setting['password'], auto_commit=False)
        self.rd = redis.Redis(host='localhost',port=6379,db=0)    #password='mdznbs_com'
        cookies = {
            "cookie_secret": setting['cookie_secret'],
            "xsrf_cookies": True
        }
        template_path = os.path.join(os.path.dirname(__file__), "templates")
        static_path = os.path.join(os.path.dirname(__file__), "static")
        tornado.web.Application.__init__(self, handlers=url,ui_modules=uimodules, template_path=template_path, static_path=static_path, debug=True, **cookies)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application(),xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()