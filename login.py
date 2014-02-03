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


class Config():
    @staticmethod
    def set_config():
        config = ConfigParser.RawConfigParser()
        path = os.path.split(os.path.realpath(__file__))[0]
        config.read(path + "/config")
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
        self.timeout = 0
        self.cookie = CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        self.opener.addheaders.pop()
        self.clientid = "52332159"
        thread.Thread.__init__(self)
        self.captcha = random.random()
        self.__psessionid = ""

    def check_(self):
        try:
            check_url = "https://ssl.ptlogin2.qq.com/check?uin=%s" % self.qq + "@qq.com&appid=1003903&js_ver=10043&js_type=0&login_sig=dHVFFlsCWR3XrDkWjbVdnghpzVWklG360kX6iJhV7cA2waWaPWCHlnYMZ5G36D9g&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html&r=0.1479938756674528"
            data = self.opener.open(check_url).read()
            return data
        except:
            save_log(catch_error())

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
                save_log(catch_error())
                if count > 10: flag = 0
                count += 1
        contain = contain[8:-2].split(",")[2]
        contain = contain[1:-1]
        flag = 1
        count = 0
        while flag:
            try:
                self.opener.open(contain, timeout = 5).read()
                flag = 0
            except:
                save_log(catch_error())
                if count > 10: flag = 0
                count += 1
        cook_2 = self.cookie
        save_log("init cookie: %s" % cook_2)
        for index, cookie in enumerate(cook_2):
            if cookie.name == "ptwebqq":
                ptweb = cookie.value
            if cookie.name == "skey":
                skey = cookie.value
            if cookie.name == "uin":
                uin = cookie.value
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
        flag = 1
        while flag:
            try:
                jsondata = self.opener.open(req, timeout = 5).read()
                flag = 0
                self.__psessionid = json.loads(jsondata).values()[1]["psessionid"]
            except:
                save_log(catch_error())

    def ret(self):
        data = self.check_()[13:-2]
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

    def keep_live(self):
        print "send_to_keep_live begin"
        data = """{"clientid":"%s","psessionid":"%s","key":0,"ids":[]}""" % (self.clientid, self.__psessionid)
        data = "r=%s&clientid=%s&psessionid=%s" % (urllib.quote(data), self.clientid, self.__psessionid)
        req = urllib2.Request("http://d.web2.qq.com/channel/poll2", data)
        flag = 1
        while flag and thread_qq.timeout == 0:
            try:
                return self.opener.open(req).read()
            except:
                save_log(catch_error())

    def post_msg_to_body_or_qun(self, to_id, msg_data, to_where):
        save_log("send msg")
        url, data = self.set_sent_msg_post_data(to_id, to_where, msg_data)
        req = urllib2.Request(url, data.encode("utf8"))
        flag = 1
        i = 0
        while flag:
            try:
                request_msg = self.opener.open(req, timeout=10).read()
                save_log(request_msg)
                save_log(msg_data)
                if request_msg.__class__ == "".__class__:
                    request_msg_to_json = json.loads(request_msg)
                    if msg().should_set_to_restart(request_msg_to_json["retcode"]):
                        thread_qq.timeout = 1
                        save_log("now cookie: %s" % self.cookie)
                        print "send error (code timeout)"
                    flag = 0
            except:
                i += 1
                if i > 10: flag = 0
                save_log(catch_error())

    def set_sent_msg_post_data(self, to_id, to_where, msg):
        to_id = "%s" % to_id
        data = "%2C%22content%22%3A%22%5B%5C%22" + "%s" % msg + "%5C%22%2C%5C%22%5C%22%2C%5B%5C%22font%5C%22%2C%7B%5C%22name%5C%22%3A%5C%22%E5%AE%8B%E4%BD%93%5C%22%2C%5C%22size%5C%22%3A%5C%2210%5C%22%2C%5C%22style%5C%22%3A%5B0%2C0%2C0%5D%2C%5C%22color%5C%22%3A%5C%22000000%5C%22%7D%5D%5D%22%2C%22msg_id%22%3A"

        if to_where == "message":
            self.body_msg_id += 1
            data = "%7B%22to%22%3A" + to_id + "%2C%22face%22%3A540" + data + "%s" % self.body_msg_id + "%2C%22clientid%22%3A%22" + ("%s" % self.clientid) + "%22%2C%22psessionid%22%3A%22" + ("%s" % self.__psessionid) + "%22%7D"
            url = "http://d.web2.qq.com/channel/send_buddy_msg2"
        else:
            self.qun_msg_id += 1
            data = "%7B%22group_uin%22%3A" + to_id + data + "%s" % self.qun_msg_id + "%2C%22clientid%22%3A%22" + ("%s" % self.clientid) + "%22%2C%22psessionid%22%3A%22" + ("%s" % self.__psessionid) + "%22%7D"
            url = "http://d.web2.qq.com/channel/send_qun_msg2"

        data = "r=%s&clientid=%s&psessionid=%s" % (data, self.clientid, self.__psessionid)
        return url, data

    def run(self):
        captcha = self.captcha
        while 1:
            flag = 0
            try:
                if thread_qq.timeout == 1 or self.captcha != captcha:
                    save_log("keep_live end and ready restart")
                    thread_qq.timeout = 1
                    break
                else:
                    request_msg = self.keep_live()
                    if request_msg.__class__ == "".__class__:
                        request_msg_to_json = json.loads(request_msg)
                        msg().return_from_tencent(request_msg_to_json)
                    else:
                        flag += 1
                        if flag > 15: thread_qq.timeout = 1
                        save_log("msg_get_error")
            except:
                if flag > 15: thread_qq.timeout = 1
                save_log(catch_error())


class msg():
    @staticmethod
    def should_set_to_restart(retcode):
        error_code = [121, 100006, 120, 103]
        if retcode in error_code:
            return True
        else:
            return False

    def return_from_tencent(self, msg_data):
        if msg_data["retcode"] == 0:
            for res in msg_data["result"]:
                if res["poll_type"] == "message" or res["poll_type"] == "group_message":
                    msg_context = res["value"]["content"][1]
                    msg_from = res["value"]["from_uin"]
                    to_where = res["poll_type"]
                    save_log("from %s" % msg_from)
                    save_log("context %s" % msg_context)

                    try:
                        if thread_qq.timeout == 0:
                            msg_context = self.choice_option(msg_context)
                            print msg_context
                            if msg_context != "":
                                thread.Thread(target=thread_qq.post_msg_to_body_or_qun, args=[msg_from, msg_context, to_where]).start()
                    except:
                        save_log(catch_error())

        elif msg().should_set_to_restart(msg_data["retcode"]):
            thread_qq.timeout = 1

    def choice_option(self, msg_context):
        if msg_context.__class__ == u"".__class__:
            msg_context = msg_context.strip()
        else:
            return ""

        try:
            if msg_context == "-h":
                msg_context = u"-route 地点1 地点2  查询地点1至地点2路线\\\\n-jump 地点1 地点2  查询地点1至地点2跳数\\\\n-hole 虫洞编号  查询该虫洞信息"
            elif msg_context[:7] == "-route1" or msg_context[:7] == "-route ":
                    path = msg_context.split(" ")
                    msg_context = EVE.find_solarSystem_jump_or_route(path[1], path[2], 1, 0)
            elif msg_context[:7] == "-route2":
                    path = msg_context.split(" ")
                    msg_context = EVE.find_solarSystem_jump_or_route(path[1], path[2], 2, 0)
            elif msg_context[:7] == "-route3":
                    path = msg_context.split(" ")
                    msg_context = EVE.find_solarSystem_jump_or_route(path[1], path[2], 3, 0)
            elif msg_context[:6] == "-jump " or msg_context[:6] == "-jump1":
                    path = msg_context.split(" ")
                    msg_context = EVE.find_solarSystem_jump_or_route(path[1], path[2], 1, 1)
            elif msg_context[:6] == "-jump2":
                    path = msg_context.split(" ")
                    msg_context = EVE.find_solarSystem_jump_or_route(path[1], path[2], 2, 1)
            elif msg_context[:6] == "-jump3":
                    path = msg_context.split(" ")
                    msg_context = EVE.find_solarSystem_jump_or_route(path[1], path[2], 3, 1)
            elif msg_context[:5] == "-hole":
                    path = msg_context.split(" ")
                    print path
                    msg_context = EVE.find_hole(path[1])
            elif msg_context[:7] == "-range ":
                    path = msg_context.split(" ")
                    print path
                    msg_context = EVE.jump_range(path[1], path[2])
            else:
                msg_context = ""
        except:
            msg_context = ""
        return msg_context


def translate_passwd(uin, pw, verify):
    pw1 = (hashlib.md5(pw).hexdigest().upper()).decode("hex")
    pw2 = hashlib.md5(pw1 + uin).hexdigest().upper()
    return hashlib.md5(pw2 + verify).hexdigest().upper()


def login(qq, pw):
    time_now = time.localtime().tm_yday
    global thread_qq
    thread_qq = QQ(qq)
    thread_qq.setDaemon(True)
    verify, uin = thread_qq.ret()
    exec("uin = '%s'" % uin)
    password = translate_passwd(uin, pw, verify)
    sign_url = "https://ssl.ptlogin2.qq.com/login?u=%s" % qq + "&p=%s" % password + "&verifycode=%s" % verify.lower() + "&webqq_type=10&remember_uin=1&login2qq=1&aid=1003903&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=8-14-19231&mibao_css=m_webqq&t=1&g=1&js_type=0&js_ver=10043&login_sig=1UQ3PnIwxYaa*Yx3R*IQ*rROvhGURkHXPitqoWEQ7q2FJ2R18cI6m25Gl9JZeap8"
    thread_qq.sign_url = sign_url
    thread_qq.login()

    for i in range(0, 5):
        exec("thread%s = thread.Thread(target=thread_qq.run)" % i)
        exec("thread%s.setDaemon(True)" % i)
        exec("thread%s.start()" % i)
        save_log("thread %s start \n" % i)
        time.sleep(5)

    while 1:
        if thread_qq.timeout == 1 or time_now != time.localtime().tm_yday:
            save_log("session close")
            break
        time.sleep(100)


def save_log(msg):
    try:
        print msg
        logging.basicConfig(filename = log, level = logging.DEBUG)
        logging.debug(msg + "  " + time.asctime())
    except:
        save_log(catch_error())


def catch_error():
    exc_info = traceback.format_exc()
    return exc_info


if __name__ == "__main__":
    global verify_path, log, EVE
    EVE = eve_mod.Eve_Jump()
    qq, password, verify_path, log = Config.set_config()
    flag = 0
    while 1:
        try:
            login(qq, password)
            save_log("connected timeout, so login again")
            time.sleep(100)
        except KeyboardInterrupt:
            break
        except:
            flag += 1
            if flag >= 5: break
