# -*- coding: utf-8 -*-
import socket,struct,binascii
import asyncore

class SOCKETClient():   #asyncore.dispatcher
    def __init__(self, host, port=80,asyn=True):
        timeout = 5
        '''
        if asyn:
            asyncore.dispatcher.__init__(self)
        '''
        socket.setdefaulttimeout(timeout)
        self._sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self._sock.connect( (host, port) )

    def handle_send(self,data=''):
        sent = self._sock.sendall(data)
        respone = self._sock.recv(1024)
    #    return binascii.hexlify( respone )
        if self.check_buff( respone ):
            return respone
        return False

    def find_ip(self,data):
        #s.struct.Struct('<19I' %)
        rc = ord(data[9])
        if rc == 0x81:
            ip = str(ord(data[14]))+'.'+str(ord(data[13]))+'.'+str(ord(data[12]))+'.'+str(ord(data[11]))
            port = (ord(data[16])<<8)+ord(data[15])
            return ip,port
        return None,None

    #验证返回的数据码合法性
    def check_buff(self,buff):
        #print buff,len(buff)
        _len = len(buff)
        #s = struct.Struct('<%dB' %_len)
        arr = [ord(x) for x in buff]#s.unpack(buff)
        if arr[0] == 0x68 and arr[_len - 1]==0x16:
            _lenstat = (arr[2]<<8) + arr[1]
            if _lenstat + 5 == _len:
                return True
        return False

    def handle_close(self):
        self._sock.close()

    #获取信息
    def get_data(self,kind=0x1,no=0x1,control=0x1,di=0x1):
        values = [0x68, 0x08, kind, no, control, di]
        s = struct.Struct('<BHHIBB')
        packed_data = s.pack(*values)
    #    print 'has:',s.size,':',binascii.hexlify(packed_data)
        ns = struct.Struct('%dB' %s.size)
        new_data = ns.unpack(packed_data)    
        cs = 0x0
        for b in new_data:
            cs +=b
        ps = struct.Struct('<BHHIBBBB')
        values.append(cs%256)
        values.append(0x16)
        datas = ps.pack(*values)
        return datas

    #kind设备分类  code设备编号  control控制码  di数据码  datas数据域
    def set_data(self,kind=0x1,no=0x1,control=0x1,di=1,datas=[]):
        leng = 8 + len(datas) 
        values = [0x68, leng, kind, no, control, di]
        sendbuff = values + datas
        s = struct.Struct('<BHHIBB%dB' %len(datas))
        packed_data = s.pack(*sendbuff)
    #    print 'has:',s.size,':',binascii.hexlify(packed_data)
        ns = struct.Struct('%dB' %s.size)
        new_data = ns.unpack(packed_data)    
        cs = 0x0
        for b in new_data:
            cs +=b
        ps = struct.Struct('<BHHIBB%dBBB' %len(datas))
        sendbuff.append(cs%256)
        sendbuff.append(0x16)
        datas = ps.pack(*sendbuff)
    #    print [hex(ord(x)) for x in datas] 
        return datas


    def __del__(self):
        self.handle_close()

    def write_error(self, status_code, **kwargs):
        title = 'error'
        self.render("hello.html", title='error')

