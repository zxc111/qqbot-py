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

    def tobin(self, str):
        arr = []
        for i in range(0, len(str), 2):
            arr.append("\\x" + str[i:i+2])
        arr = "".join(arr)
        exec ("arr = '%s'" % arr)
        return arr

    def md(self):
        self.pw1 = self.tobin(hashlib.md5(self.pw).hexdigest().upper())
        #print self.pw1
        return self.pw1

    def md2(self):
        self.pw2 = hashlib.md5(self.pw1+self.uin).hexdigest().upper()
        #print self.pw2
        return self.pw2

    def md3(self):
        return hashlib.md5(self.pw2 + self.verify).hexdigest().upper()


class check(thread.Thread):
    def __init__(self, qq):
        self.body_msg_id = 5000001
        self.qun_msg_id = 9000001
        self.qq = qq
        self.cj = CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.addheaders.pop()
        self.clientid = "52332159"
        thread.Thread.__init__(self)
        self.timeout = 0

    def check_(self):
        check = "https://ssl.ptlogin2.qq.com/check?uin=%s" % self.qq + "@qq.com&appid=1003903&js_ver=10043&js_type=0&login_sig=dHVFFlsCWR3XrDkWjbVdnghpzVWklG360kX6iJhV7cA2waWaPWCHlnYMZ5G36D9g&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html&r=0.1479938756674528"
        self.data = self.opener.open(check).read()
        return self.data

    def get_verify(self, path):
        verify_jpg = "http://captcha.qq.com/getimage?aid=1003903&&uin=%s" % self.qq + "&vc_type=%s" % path
        self.jpg = self.opener.open(verify_jpg).read()
        return self.jpg

    def login(self):
        flag = 1
        while flag:
            try:
                contain = self.opener.open(self.sign_url, timeout = 5).read()
                flag = 0
            except:
                print "timeout1"
        #print contain
        contain = contain[8:-2].split(",")[2]
        contain = contain[1:-1]
        #print contain
        flag = 1
        while flag:
            try:
                self.opener.open(contain, timeout = 5).read()
                flag = 0
            except:
                print "timeout2"
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
        #print "cookie:  %s" % coo
        #print ptweb
        data_ = urllib.quote(login)
        data_ = "r=%s&clientid=52332159&psessionid=null" % data_
        #print data_
        self.opener.addheaders.append(("Content-Type", "application/x-www-form-urlencoded"))
        self.opener.addheaders.append(("Referer", "http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2"))
        self.opener.addheaders.append(("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36"))
        req = urllib2.Request("http://d.web2.qq.com/channel/login2", data_)
        print self.opener.addheaders
        flag = 1
        while flag:
            try:
                self.jsondata = self.opener.open(req, timeout = 5).read()
                flag = 0
            except:
                pass
        print self.jsondata

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
        print "heart begin"
        str = self.json_to_data(self.jsondata)
        data = """{"clientid":"%s","psessionid":"%s","key":0,"ids":[]}""" % (self.clientid, str["psessionid"])
        data = "r=%s&clientid=%s&psessionid=%s" % (urllib.quote(data), self.clientid, str["psessionid"])
        #print data
        #print self.opener.addheaders
        req = urllib2.Request("http://d.web2.qq.com/channel/poll2", data)
        flag = 1
        while flag:
            try:
                return self.opener.open(req).read()
            except:
                print "get_server_msg_time_out"

    def post_msg_to_body_or_qun(self, to_id, msg, to_where):
        #data = """{"to":%s,"face":540,,"content":"["334",["font",{"name":"\\u5b8b\\u4f53","size":"10","style":[0,0,0],"color":"993366"}]]","msg_id":123223456,"clientid":"%s","psessionid":"%s"}""" % (to_id, self.clientid, str["psessionid"])
        #print data
        #data = "%2C%22content%22%3A%22%5B%5C%22" + "%s" % msg + "%5C%22%2C%5C%22%5C%22%2C%5B%5C%22font%5C%22%2C%7B%5C%22name%5C%22%3A%5C%22%E5%AE%8B%E4%BD%93%5C%22%2C%5C%22size%5C%22%3A%5C%2210%5C%22%2C%5C%22style%5C%22%3A%5B0%2C0%2C0%5D%2C%5C%22color%5C%22%3A%5C%22000000%5C%22%7D%5D%5D%22%2C%22msg_id%22%3A" + "%s" % self.msg_id + "%2C%22clientid%22%3A%22" + ("%s" % self.clientid) + "%22%2C%22psessionid%22%3A%22" + ("%s" % str["psessionid"]) + "%22%7D"
        #data = "%7B%22to%22%3A"+to_id+"%2C%22face%22%3A540%2C%22content%22%3A%22%5B%5C%22"+"123"+"%5C%22%2C%5C%22%5C%22%2C%5B%5C%22font%5C%22%2C%7B%5C%22name%5C%22%3A%5C%22%E5%AE%8B%E4%BD%93%5C%22%2C%5C%22size%5C%22%3A%5C%2210%5C%22%2C%5C%22style%5C%22%3A%5B0%2C0%2C0%5D%2C%5C%22color%5C%22%3A%5C%22000000%5C%22%7D%5D%5D%22%2C%22msg_id%22%3A5150001%2C%22clientid%22%3A%22"+ ("%s" % self.clientid) +"%22%2C%22psessionid%22%3A%22" + ("%s" % str["psessionid"]) + "%22%7D"
        #pdb.set_trace()
        print "send msg"
        url, data = self.set_sent_msg_post_data(to_id, to_where, msg)
        req = urllib2.Request(url, data.encode("utf8"))
        #print data
        flag = 1
        while flag:
            try:
                print self.opener.open(req, timeout=5).read()
                flag = 0
            except:
                print "send error"

    def set_sent_msg_post_data(self, to_id, to_where, msg):
        str = self.json_to_data(self.jsondata)
        to_id = "%s" % to_id
        data = "%2C%22content%22%3A%22%5B%5C%22" + "%s" % msg + "%5C%22%2C%5C%22%5C%22%2C%5B%5C%22font%5C%22%2C%7B%5C%22name%5C%22%3A%5C%22%E5%AE%8B%E4%BD%93%5C%22%2C%5C%22size%5C%22%3A%5C%2210%5C%22%2C%5C%22style%5C%22%3A%5B0%2C0%2C0%5D%2C%5C%22color%5C%22%3A%5C%22000000%5C%22%7D%5D%5D%22%2C%22msg_id%22%3A" 
        if to_where == "message":
            self.body_msg_id = self.body_msg_id + 1
            data = "%7B%22to%22%3A" + to_id + "%2C%22face%22%3A540" + data + "%s" % self.body_msg_id + "%2C%22clientid%22%3A%22" + ("%s" % self.clientid) + "%22%2C%22psessionid%22%3A%22" + ("%s" % str["psessionid"]) + "%22%7D"
            url = "http://d.web2.qq.com/channel/send_buddy_msg2"
        else:
            self.qun_msg_id = self.qun_msg_id + 1
            data = "%7B%22group_uin%22%3A" + to_id + data + "%s" % self.qun_msg_id + "%2C%22clientid%22%3A%22" + ("%s" % self.clientid) + "%22%2C%22psessionid%22%3A%22" + ("%s" % str["psessionid"]) + "%22%7D"
            url = "http://d.web2.qq.com/channel/send_qun_msg2" 
        data = "r=%s&clientid=%s&psessionid=%s" % (data, self.clientid, str["psessionid"])
        return url, data
            

    def run(self):
        while 1:
            try:
                if self.timeout == 1:
                    print "heart end"
                    break
                request_msg = self.heartbeat()
                print request_msg
                request_msg_to_json = json.loads(request_msg)
                msg().return_from_tencent(request_msg_to_json)
            except:
                pass


class msg:
    def return_from_tencent(self, msg_data):
        if msg_data["retcode"] == 0:
            for msg in msg_data["result"]:
                res = msg
                if res["poll_type"] == "message" or res["poll_type"] == "group_message":
                    msg_context = res["value"]["content"][1]
                    msg_from = res["value"]["from_uin"]
                    to_where = res["poll_type"]
                    print "from %s" % msg_from
                    print "context %s" % msg_context
                    #pdb.set_trace()
                    try:
                        if a.timeout == 0:
                            thread.Thread(target=a.post_msg_to_body_or_qun, args=[msg_from, msg_context, to_where]).start()
                    except:
                        print "errrrrrrrrrrrrrrrrrrrrrrrror"
        elif msg_data["retcode"] == 121 or msg_data["retcode"] == 100006:
            a.timeout = 1
         

def login(qq, pw):
    global a
    a = check(qq)
    a.setDaemon(True)
    verify, uin = a.ret()
    exec("uin = '%s'" % uin)
    #print uin
    pwd = pwd_encrypt(uin, pw, verify)
    pwd.md()
    pwd.md2()
    fin_pw = pwd.md3()
    sign_url = "https://ssl.ptlogin2.qq.com/login?u=%s" % qq + "&p=%s" % fin_pw + "&verifycode=%s" % verify.lower() + "&webqq_type=10&remember_uin=1&login2qq=1&aid=1003903&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=8-14-19231&mibao_css=m_webqq&t=1&g=1&js_type=0&js_ver=10043&login_sig=1UQ3PnIwxYaa*Yx3R*IQ*rROvhGURkHXPitqoWEQ7q2FJ2R18cI6m25Gl9JZeap8"
    a.sign_url = sign_url
    a.login()
    for i in range(0,3):
        exec("thread%s = thread.Thread(target=a.run)" % i )
        exec("thread%s.setDaemon(True)" % i)
        exec("thread%s.start()" % i)
        print "thread %s start \n" % i
        time.sleep(5) 
    while 1:
        if a.timeout == 1:
            break
        time.sleep(100)
    
if __name__ == "__main__":
    print 2752878938
    qq = raw_input("please input qq:\n")
    pw = raw_input("please input password:\n")
    while 1:
        #verifychar = raw_input()
        #print verifychar
        login(qq, pw)
        print "timeout so login again"
