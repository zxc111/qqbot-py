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
import ConfigParser
import logging
import traceback
import random
import eve_mod
from cookielib import CookieJar


class pwd_encrypt():
    def __init__(self, uin, pw, verify):
        self.pw1 = ""
        self.pw2 = ""
        self.uin = uin
        self.pw = pw
        self.verify = verify

    def to_bin(self, str):
        arr = []
        for i in range(0, len(str), 2):
            arr.append("\\x" + str[i:i+2])
        arr = "".join(arr)
        exec ("arr = '%s'" % arr)
        return arr

    def md(self):
        self.pw1 = self.to_bin(hashlib.md5(self.pw).hexdigest().upper())
        return self.pw1

    def md2(self):
        self.pw2 = hashlib.md5(self.pw1+self.uin).hexdigest().upper()
        return self.pw2

    def md3(self):
        return hashlib.md5(self.pw2 + self.verify).hexdigest().upper()


class Config():
    @staticmethod
    def set_config():
        config = ConfigParser.RawConfigParser()
        path = os.path.split(os.path.realpath(__file__))[0] 
        config.read(path + "/config" )
        if config.get("qq_info", "qq") != "":
            qq = int(config.get("qq_info", "qq"))
        else:
            qq = raw_input("please input qq:\n")
        if config.get("qq_info", "password") != "":
            password = config.get("qq_info", "password")
        else:
            password = raw_input("please input password:\n")
        if config.get("qq_info", "verify_path") != "":
            verify_path = config.get("qq_info", "verify_path")
        else:
            raise "can not output verify img"
        if config.get("debug", "log") == "":
            log = path + "/log"
        else:
            log = config.get("debug", "log")
        return qq, password, verify_path, log


class QQ(thread.Thread):
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
        self.captcha = random.random()
        self.__psessionid = ""

    def check_(self):
        check_url = "https://ssl.ptlogin2.qq.com/check?uin=%s" % self.qq + "@qq.com&appid=1003903&js_ver=10043&js_type=0&login_sig=dHVFFlsCWR3XrDkWjbVdnghpzVWklG360kX6iJhV7cA2waWaPWCHlnYMZ5G36D9g&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html&r=0.1479938756674528"
        self.data = self.opener.open(check_url).read()
        return self.data

    def get_verify(self, path):
        verify_jpg = "http://captcha.qq.com/getimage?aid=1003903&&uin=%s" % self.qq + "&vc_type=%s" % path
        self.jpg = self.opener.open(verify_jpg).read()
        return self.jpg

    def login(self):
        flag = 1
        count = 0
        while flag:
            try:
                contain = self.opener.open(self.sign_url, timeout = 5).read()
                flag = 0
            except:
                if count > 10: flag = 0
                count += 1
                debugger("timeout1")
        contain = contain[8:-2].split(",")[2]
        contain = contain[1:-1]
        flag = 1
        count = 0
        while flag:
            try:
                self.opener.open(contain, timeout = 5).read()
                flag = 0
            except:
                if count > 10: flag = 0
                count += 1
                debugger("timeout2")
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
        data_ = urllib.quote(login)
        data_ = "r=%s&clientid=52332159&psessionid=null" % data_
        self.opener.addheaders.append(("Content-Type", "application/x-www-form-urlencoded"))
        self.opener.addheaders.append(("Referer", "http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2"))
        self.opener.addheaders.append(("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36"))
        req = urllib2.Request("http://d.web2.qq.com/channel/login2", data_)
        #debugger(self.opener.addheaders)
        flag = 1
        while flag:
            try:
                jsondata = self.opener.open(req, timeout = 5).read()
                flag = 0
                self.__psessionid = json.loads(jsondata).values()[1]["psessionid"]
            except:
                debugger(traceback.print_exc())

    def ret(self):
        self.check_()
        data = self.data
        data = data[13: -2]
        fir, sec, thi = data.split(",")
        if fir[1:-1] == "0":
            return sec[1:-1], thi[1:-1]
        else:
            file_ = open(verify_path, "wb+")
            jpgdata = self.get_verify(thi[1:-1])
            file_.write(jpgdata)
            file_.close()
            verifychar = raw_input("please input verify\n")
            sec = verifychar
            return sec.upper(), thi[1:-1]

    def heartbeat(self):
        debugger("heart begin")
        data = """{"clientid":"%s","psessionid":"%s","key":0,"ids":[]}""" % (self.clientid, self.__psessionid)
        data = "r=%s&clientid=%s&psessionid=%s" % (urllib.quote(data), self.clientid, self.__psessionid)
        req = urllib2.Request("http://d.web2.qq.com/channel/poll2", data)
        flag = 1
        while flag and thread_qq.timeout == 0:
            try:
                return self.opener.open(req).read()
            except:
                debugger("get_server_msg_time_out")

    def post_msg_to_body_or_qun(self, to_id, msg, to_where):
        debugger("send msg")
        url, data = self.set_sent_msg_post_data(to_id, to_where, msg)
        req = urllib2.Request(url, data.encode("utf8"))
        flag = 1
        while flag:
            try:
                debugger(self.opener.open(req, timeout=5).read())
                flag = 0
            except:
                debugger("send error")

    def set_sent_msg_post_data(self, to_id, to_where, msg):
        to_id = "%s" % to_id
        data = "%2C%22content%22%3A%22%5B%5C%22" + "%s" % msg + "%5C%22%2C%5C%22%5C%22%2C%5B%5C%22font%5C%22%2C%7B%5C%22name%5C%22%3A%5C%22%E5%AE%8B%E4%BD%93%5C%22%2C%5C%22size%5C%22%3A%5C%2210%5C%22%2C%5C%22style%5C%22%3A%5B0%2C0%2C0%5D%2C%5C%22color%5C%22%3A%5C%22000000%5C%22%7D%5D%5D%22%2C%22msg_id%22%3A" 
        if to_where == "message":
            self.body_msg_id = self.body_msg_id + 1
            data = "%7B%22to%22%3A" + to_id + "%2C%22face%22%3A540" + data + "%s" % self.body_msg_id + "%2C%22clientid%22%3A%22" + ("%s" % self.clientid) + "%22%2C%22psessionid%22%3A%22" + ("%s" % self.__psessionid) + "%22%7D"
            url = "http://d.web2.qq.com/channel/send_buddy_msg2"
        else:
            self.qun_msg_id = self.qun_msg_id + 1
            data = "%7B%22group_uin%22%3A" + to_id + data + "%s" % self.qun_msg_id + "%2C%22clientid%22%3A%22" + ("%s" % self.clientid) + "%22%2C%22psessionid%22%3A%22" + ("%s" % self.__psessionid) + "%22%7D"
            url = "http://d.web2.qq.com/channel/send_qun_msg2" 
        data = "r=%s&clientid=%s&psessionid=%s" % (data, self.clientid, self.__psessionid)
        return url, data

    def run(self):
        captcha = self.captcha
        while 1:
            try:
                if self.timeout == 1 or self.captcha != captcha:
                    debugger("heart end")
                    break
                request_msg = self.heartbeat()
                debugger(request_msg)
                request_msg_to_json = json.loads(request_msg)
                msg().return_from_tencent(request_msg_to_json)
            except:
                debugger(traceback.print_exc())


class msg:
    def return_from_tencent(self, msg_data):
        if msg_data["retcode"] == 0:
            for msg in msg_data["result"]:
                res = msg
                if res["poll_type"] == "message" or res["poll_type"] == "group_message":
                    msg_context = res["value"]["content"][1]
                    msg_from = res["value"]["from_uin"]
                    to_where = res["poll_type"]
                    debugger("from %s" % msg_from)
                    debugger("context %s" % msg_context)
                    try:
                        if thread_qq.timeout == 0:
                            #print msg_context
                            msg_context = self.choice_option(msg_context.strip())
                            #print msg_context
                            if msg_context != "":
                                thread.Thread(target=thread_qq.post_msg_to_body_or_qun, args=[msg_from, msg_context, to_where]).start()
                    except:
                        debugger("error")
        elif msg_data["retcode"] == 121 or msg_data["retcode"] == 100006 or msg_data["retcode"] == 120 or msg_data["retcode"] == 103:
            thread_qq.timeout = 1

    def choice_option(self, msg_context):
        #pdb.set_trace()
        if msg_context == "-h":
            msg_context = u"-route 地点1 地点2  查询地点1至地点2路线.\r-jump 地点1 地点2  查询地点1至地点2跳数\r-hole 虫洞编号  查询该虫洞信息"
        elif msg_context[:7] == "-route1" or msg_context[:7] == "-route ":
            try:
                path = msg_context.split(" ")
                msg_context = EVE.find_solarSystem_jump_or_route(path[1], path[2], 1, 0)
                print msg_context
            except:
                msg_context = ""
        elif msg_context[:7] == "-route2":
            try:
                path = msg_context.split(" ")
                msg_context = EVE.find_solarSystem_jump_or_route(path[1], path[2], 2, 0)
            except:
                msg_context = ""
        elif msg_context[:7] == "-route3":
            try:
                path = msg_context.split(" ")
                msg_context = EVE.find_solarSystem_jump_or_route(path[1], path[2], 3, 0)
            except:
                msg_context = ""
        elif msg_context[:6] == "-jump " or msg_context[:6] == "-jump1":
            try:
                path = msg_context.split(" ")
                msg_context = EVE.find_solarSystem_jump_or_route(path[1], path[2], 1, 1)
            except:
                msg_context = ""
        elif msg_context[:6] == "-jump2":
            try:
                path = msg_context.split(" ")
                msg_context = EVE.find_solarSystem_jump_or_route(path[1], path[2], 2, 1)
            except:
                msg_context = ""
        elif msg_context[:6] == "-jump3":
            try:
                path = msg_context.split(" ")
                msg_context = EVE.find_solarSystem_jump_or_route(path[1], path[2], 3, 1)
            except:
                msg_context = ""
        elif msg_context[:5] == "-hole":
            try:
                path = msg_context.split(" ")
                msg_context = EVE.find_hole(path)
            except:
                msg_context = ""
        else:
            msg_context = ""
        return msg_context
         

def login(qq, pw):
    time_now = time.localtime().tm_yday
    global thread_qq
    thread_qq = QQ(qq)
    thread_qq.setDaemon(True)
    verify, uin = thread_qq.ret()
    exec("uin = '%s'" % uin)
    pwd = pwd_encrypt(uin, pw, verify)
    pwd.md()
    pwd.md2()
    fin_pw = pwd.md3()
    sign_url = "https://ssl.ptlogin2.qq.com/login?u=%s" % qq + "&p=%s" % fin_pw + "&verifycode=%s" % verify.lower() + "&webqq_type=10&remember_uin=1&login2qq=1&aid=1003903&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=8-14-19231&mibao_css=m_webqq&t=1&g=1&js_type=0&js_ver=10043&login_sig=1UQ3PnIwxYaa*Yx3R*IQ*rROvhGURkHXPitqoWEQ7q2FJ2R18cI6m25Gl9JZeap8"
    thread_qq.sign_url = sign_url
    thread_qq.login()
    for i in range(0, 5):
        exec("thread%s = thread.Thread(target=thread_qq.run)" % i )
        exec("thread%s.setDaemon(True)" % i)
        exec("thread%s.start()" % i)
        debugger("thread %s start \n" % i)
        time.sleep(5) 
    while 1:
        if thread_qq.timeout == 1 or time_now != time.localtime().tm_yday:
            break
        time.sleep(100)

def debugger(msg):
    try:
        logging.basicConfig(filename = log, level = logging.DEBUG) 
        logging.debug(msg + "  " + time.asctime())
    except:
        pass
      
if __name__ == "__main__":
    #print 2752878938
    global verify_path, log, EVE
    EVE = eve_mod.Eve_Jump()
    qq, password, verify_path, log = Config.set_config()
    while 1:
        login(qq, password)
        debugger("connected timeout, so login again")


