#-*- encoding: utf-8 -*-
import hashlib
import sys
import os
import urllib
import urllib2
import json
import threading as thread
import time
import pdb
from cookielib import CookieJar


class pwd_encrypt():
    def __init__(self, uin, pw, verify):
        self.pw1 = ""
        self.pw2 = ""
        self.uin = uin
        self.pw = pw
        self.verify = verify
        #print self.uin
        #print self.pw
        #print verify

    def tobin(self, str):
        arr = []
        for i in range(0, len(str), 2):
            arr.append("\\x" + str[i:i+2])
        arr = "".join(arr)
        exec ("arr = '%s'" % arr)
        return arr

    def md(self):
        self.pw1 = self.tobin(hashlib.md5(self.pw).hexdigest().upper())
        print self.pw1
        return self.pw1

    def md2(self):
        self.pw2 = hashlib.md5(self.pw1+self.uin).hexdigest().upper()
        print self.pw2
        return self.pw2

    def md3(self):
        #print 111111111111111111111111
        #print "pw %s:"%self.pw
        #print "pw1 %s "%self.pw1
        #print "pw2 %s "%self.pw2
        #print "veri %s "%self.verify
        #print hashlib.md5(self.pw2 + self.verify).hexdigest().upper()
        #print 111111111111111111111111111
        return hashlib.md5(self.pw2 + self.verify).hexdigest().upper()


class check(thread.Thread):
    def __init__(self, qq):
        self.msg_id = 5000001
        self.qq = qq
        self.cj = CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.addheaders.pop()
        self.clientid = "52332159"
        thread.Thread.__init__(self)

    def check_(self):
        check = "https://ssl.ptlogin2.qq.com/check?uin=%s" % self.qq + "@qq.com&appid=1003903&js_ver=10043&js_type=0&login_sig=dHVFFlsCWR3XrDkWjbVdnghpzVWklG360kX6iJhV7cA2waWaPWCHlnYMZ5G36D9g&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html&r=0.1479938756674528"
        self.data = self.opener.open(check).read()
        return self.data

    def get_verify(self, path):
        verify_jpg = "http://captcha.qq.com/getimage?aid=1003903&&uin=%s" % self.qq + "&vc_type=%s" % path
        self.jpg = self.opener.open(verify_jpg).read()
        return self.jpg

    def get_(self):
        contain = self.opener.open(self.sign_url).read()
        #print contain
        contain = contain[8:-2].split(",")[2]
        contain = contain[1:-1]
        #print contain
        print self.opener.open(contain).read()
        cook_ = self.cj._cookies.values()[1]
        cook_2 = self.cj
        temp = []
        coo = ""
        for index, cookie in enumerate(cook_2):
            if cookie.name == "ptwebqq":
                ptweb = cookie.value
            if cookie.name == "skey":
                skey = cookie.value
            if cookie.name == "uin":
                uin = cookie.value
            coo = "%s %s=%s;" % (coo, cookie.name, cookie.value)
        login = """{
            "status":"online",
            "ptwebqq":"%s",
            "passwd_sig":"",
            "clientid":"52332159",
            "psessionid":null}""" % (ptweb)
        print "cookie:  %s" % coo
        print ptweb
        data_ = urllib.quote(login)
        data_ = "r=%s&clientid=52332159&psessionid=null" % data_
        print data_
        self.opener.addheaders.append(("Content-Type", "application/x-www-form-urlencoded"))
        self.opener.addheaders.append(("Referer", "http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2"))
        self.opener.addheaders.append(("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36"))
        req = urllib2.Request("http://d.web2.qq.com/channel/login2", data_)
        print self.opener.addheaders
        self.jsondata = self.opener.open(req).read()
        print self.jsondata
        #headers = {
        #    "Content-Type": "application/x-www-form-urlencoded",
        #    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36",
        #    }
        #req = urllib2.Request("https://d.web2.qq.com/channel/login2", data_, headers)
        #print req.headers
        #print req.data
        #res = urllib2.urlopen(req)
        #print res.read()

    def json_to_data(self, str):
        #self.retcode = json.loads(str).values[0]
        #print self.jsondata.__class__
        #print json.loads(self.jsondata).values()
        #import debug
        self.result = json.loads(self.jsondata).values()[1]
        return self.result

    def ret(self):
        self.check_()
        data = self.data
        data = data[13: -2]
        fir, sec, thi = data.split(",")
        #print fir[1:-1], sec[1:-1], thi[1:-1]
        if fir[1:-1] == "0":
            return sec[1:-1], thi[1:-1]
        else:
            verify_jpg = "/home/gho/verify.jpg"
            file_ = open(verify_jpg, "wb+")
            jpgdata = self.get_verify(thi[1:-1])
            file_.write(jpgdata)
            file_.close()
            verifychar = raw_input("please input verify\n")
            sec = verifychar
            return sec.upper(), thi[1:-1]

    def heartbeat(self):
        str = self.json_to_data(self.jsondata)
        data = """{"clientid":"%s","psessionid":"%s","key":0,"ids":[]}""" % (self.clientid, str["psessionid"])
        data = "r=%s&clientid=%s&psessionid=%s" % (urllib.quote(data), self.clientid, str["psessionid"])
        #print data
        #print self.opener.addheaders
        req = urllib2.Request("http://d.web2.qq.com/channel/poll2", data)
        print "hearrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrt"
        return self.opener.open(req).read()

    def post_msg_to_body(self, to_id, msg):
        self.msg_id = self.msg_id + 1
        print self.msg_id
        str = self.json_to_data(self.jsondata)
        to_id = "%s" % to_id
        #data = """{"to":%s,"face":540,,"content":"["334",["font",{"name":"\\u5b8b\\u4f53","size":"10","style":[0,0,0],"color":"993366"}]]","msg_id":123223456,"clientid":"%s","psessionid":"%s"}""" % (to_id, self.clientid, str["psessionid"])
        #print data
        data = "%7B%22to%22%3A"+to_id+"%2C%22face%22%3A540%2C%22content%22%3A%22%5B%5C%22" + "%s" % msg + "%5C%22%2C%5C%22%5C%22%2C%5B%5C%22font%5C%22%2C%7B%5C%22name%5C%22%3A%5C%22%E5%AE%8B%E4%BD%93%5C%22%2C%5C%22size%5C%22%3A%5C%2210%5C%22%2C%5C%22style%5C%22%3A%5B0%2C0%2C0%5D%2C%5C%22color%5C%22%3A%5C%22000000%5C%22%7D%5D%5D%22%2C%22msg_id%22%3A" + "%s" % self.msg_id + "%2C%22clientid%22%3A%22"+ ("%s" % self.clientid) +"%22%2C%22psessionid%22%3A%22" + ("%s" % str["psessionid"]) + "%22%7D"
        #data = "%7B%22to%22%3A"+to_id+"%2C%22face%22%3A540%2C%22content%22%3A%22%5B%5C%22"+"123"+"%5C%22%2C%5C%22%5C%22%2C%5B%5C%22font%5C%22%2C%7B%5C%22name%5C%22%3A%5C%22%E5%AE%8B%E4%BD%93%5C%22%2C%5C%22size%5C%22%3A%5C%2210%5C%22%2C%5C%22style%5C%22%3A%5B0%2C0%2C0%5D%2C%5C%22color%5C%22%3A%5C%22000000%5C%22%7D%5D%5D%22%2C%22msg_id%22%3A5150001%2C%22clientid%22%3A%22"+ ("%s" % self.clientid) +"%22%2C%22psessionid%22%3A%22" + ("%s" % str["psessionid"]) + "%22%7D"
        data = "r=%s&clientid=%s&psessionid=%s" % (data, self.clientid, str["psessionid"])
        req = urllib2.Request("http://d.web2.qq.com/channel/send_buddy_msg2", data.encode("utf8"))
        print "msggggggggggggggggggggggggggggg"
        return self.opener.open(req).read()

    def run(self):
        while 1:
            try:
                #print 123
                request_msg = self.heartbeat()
                print request_msg
                request_msg_to_json = json.loads(request_msg)
                msg().return_from_tencent(request_msg_to_json)
            except:
                pass

class msg:
    def return_from_tencent(self,msg_data):
        #print 123
        if msg_data["retcode"] == 0:
            #print 321
            for msg in msg_data["result"]:
                res = msg
                if res["poll_type"] == "message":
                    #print 222
                    msg_context = res["value"]["content"][1]
                    msg_from = res["value"]["from_uin"]
                    print "from %s" % msg_from
                    print "context %s" % msg_context
                    try:
                        print "bbbbbbbbbbbbbbbbbegin"
                        thread.Thread(target = a.post_msg_to_body, args=[msg_from,msg_context]).start()
                        print "eeeeeeeeeeeeeeeeeeeeeend"
                    except:
                      print "errrrrrrrrrrrrrrrrrrrrrrrror"
                
if __name__ == "__main__":
    qq = raw_input("please input qq:\n")
    pw = raw_input("please input password:\n")
    a = check(qq)
    a.setDaemon(True)
    verify, uin = a.ret()
    exec("uin = '%s'" % uin)
    print uin
    pwd = pwd_encrypt(uin, pw, verify)
    pwd.md()
    pwd.md2()
    fin_pw = pwd.md3()
    sign_url = "https://ssl.ptlogin2.qq.com/login?u=%s" % qq + "&p=%s" % fin_pw + "&verifycode=%s" % verify.lower() + "&webqq_type=10&remember_uin=1&login2qq=1&aid=1003903&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=8-14-19231&mibao_css=m_webqq&t=1&g=1&js_type=0&js_ver=10043&login_sig=1UQ3PnIwxYaa*Yx3R*IQ*rROvhGURkHXPitqoWEQ7q2FJ2R18cI6m25Gl9JZeap8"
    a.sign_url = sign_url
    a.get_()
    a.start()
    post = a


    while 1:
        verifychar = raw_input()
        print verifychar
        #time.sleep(100)
    #print 1111111111111111111111
    #b = check(qq)
    #verify = "AKVH"
    #uin = "\x00\x00\x00\x00\xa4\x15\x99\x5a"
    #cc = pwd_encrypt(uin, pw, verify)
    #cc.md()
    #print cc.pw1
    #cc.md2()
    #print cc.pw2

    #group_uin
    #http://d.web2.qq.com/channel/send_qun_msg2
