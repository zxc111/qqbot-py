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
import smtplib
from cookielib import CookieJar
try:
    from spidermonkey import Runtime
except:
    raise Exception(u"""Please install spidermonkey.\nhttps://github.com/davisp/python-spidermonkey""")
    


# Get options from config and return.
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
        if config.get("email", "receiver") != "":
            receiver = config.get("email", "receiver")
            if config.get("email", "send") == "true":
                send = True
            else:
                send = False
        else:
            send = False
        return qq, password, verify_path, log, receiver, send


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
        self.get_captcha_time = 0

    def check_(self):
        try:
            check_url = "https://ssl.ptlogin2.qq.com/check?pt_tea=1&uin={}&appid=1003903&js_ver=10116&js_type=0&login_sig=KpLck-z9xhDg60W6EW30eJ5e4-s2k2bfqyq*-IGwrxJhAVuo5XuinLfMHb4HNSq9&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html&r=0.5435769769828767".format(self.qq)
            data = self.opener.open(check_url, timeout = 30).read()
            return data
        except:
            save_log(catch_error())

    def get_verify(self, path):
        verify_jpg = "http://captcha.qq.com/getimage?aid=1003903&&uin=%s" % self.qq + "&vc_type=%s" % path
        jpg = self.opener.open(verify_jpg).read()
        verify_session = self.cookie._cookies[".qq.com"]["/"]["verifysession"].value
        return jpg, verify_session

    def login(self):
        flag = 1
        count = 0
        while flag:
            try:
                contain = self.opener.open(self.sign_url, timeout = 5).read()
                # print contain
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
                jsondata = self.opener.open(req, timeout = 15).read()
                flag = 0
                self.__psessionid = json.loads(jsondata).values()[1]["psessionid"]
            except:
                save_log(catch_error())

    # Try get captcha from Tencent 3 times.
    def ret(self):
        global first_login
        # pdb.set_trace()
        data = self.check_()[13:-2]
        #TODO tencent add a new value
        # fir, sec, thi, temp = data.split(",")
        params = data.split(",")
        if params[0][1:-1] == "0":
            # ptui_checkVC('0','!ACX','\x00\x00\x00\x00\x10\xbf\x27\x4d','c36cc2c619afb9','0');
            self.get_captcha_time = 9
            # captcha, verify_session, uin
            return params[1][1:-1], params[3][1: -1], params[2][1:-1]
        elif self.get_captcha_time < 3 and first_login == False:
            save_log("Try get captcha after 120 sec.This is %s times to try to get." % thread_qq.get_captcha_time)
            self.get_captcha_time += 1
            time.sleep(120)
            return ["", "", ""]
        else:
            # ptui_checkVC('1','70H_vQjupVFiU','\x00\x00\x00\x00\xa4\x15\x99\x5a','','0');
            self.get_captcha_time = 9
            file_ = open(verify_path, "wb+")
            jpgdata, verify_session = self.get_verify(params[2][1:-1])
            file_.write(jpgdata)
            file_.close()
            send_email("The application need input captcha to run.")
            captcha = raw_input("please input verify\n")
            # captcha, verify_session, uin
            return captcha.upper(), verify_session, params[2]

    def keep_live(self):
        global alive
        print "send_to_keep_live begin"
        data = """{"clientid":"%s","psessionid":"%s","key":0,"ids":[]}""" % (self.clientid, self.__psessionid)
        data = "r=%s&clientid=%s&psessionid=%s" % (urllib.quote(data), self.clientid, self.__psessionid)
        req = urllib2.Request("http://d.web2.qq.com/channel/poll2", data)
        flag = 1
        while flag and thread_qq.timeout == 0:
            try:
                res = self.opener.open(req).read()
                alive = 10
                return res
            except:
                save_log(catch_error())
                time.sleep(2)

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
                            if msg_context != "":
                                thread.Thread(target=thread_qq.post_msg_to_body_or_qun, args=[msg_from, msg_add_border(msg_context), to_where]).start()
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
              msg_context = u"1.-route 地点1 地点2  查询地点1至地点2路线\\\\n2.-jump 地点1 地点2  查询地点1至地点2跳数\\\\n3.-hole 虫洞编号  查询该虫洞信息\\\\n4.-range 起点 终点 旗舰跃迁距离\\\\n"
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
                    #print path
                    msg_context = EVE.find_hole(path[1])
            elif msg_context[:7] == "-range ":
                    path = msg_context.split(" ")
                    # print path
                    msg_context = EVE.jump_range(path[1], path[2])
            else:
                msg_context = ""
        except:
            msg_context = ""
        return msg_context


def translate_passwd(uin, pw, verify):
    # import pdb
    # pdb.set_trace()
    # pw1 = (hashlib.md5(pw).hexdigest().upper()).decode("hex")
    # pw2 = hashlib.md5(pw1 + uin).hexdigest().upper()
    # return hashlib.md5(pw2 + verify).hexdigest().upper()
    cx = Runtime().new_context()
    cx.execute(open("encrypt.js").read())
    res = cx.execute('Encryption.getEncryption("{password}","{qq_number}",\
        "{verify_code}")'.format(password=pw, qq_number=uin, verify_code=verify))
    return res


def login(qq, pw):
    global thread_qq, alive
    global first_login
    thread_qq = None
    thread_qq = QQ(qq)
    thread_qq.setDaemon(True)

    # Get Captcha from what u c and input
    while thread_qq.get_captcha_time != 9:
        verify, verify_session, uin = thread_qq.ret()
    exec("uin = '%s'" % uin[1: -1])

    # Encrypt password
    # password = translate_passwd(uin, pw, verify)
    password = translate_passwd(qq, pw, verify)

    # sign_url = "https://ssl.ptlogin2.qq.com/login?u=%s" % qq + "&p=%s" % password + "&verifycode=%s" % verify.lower() + "&webqq_type=10&remember_uin=1&login2qq=1&aid=1003903&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=8-14-19231&mibao_css=m_webqq&t=1&g=1&js_type=0&js_ver=10043&login_sig=1UQ3PnIwxYaa*Yx3R*IQ*rROvhGURkHXPitqoWEQ7q2FJ2R18cI6m25Gl9JZeap8&pt_verifysession_v1=" + verify_session[1: -1]
    sign_url = "https://ssl.ptlogin2.qq.com/login?u={qq}&p={p}&verifycode={verify}&webqq_type=10&remember_uin=1&login2qq=1&aid=1003903&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=6-17-52584&mibao_css=m_webqq&t=1&g=1&js_type=0&js_ver=10116&login_sig=z5TsTQO3ICe2U93qkzg-ENYMoIxNcELz*yQ-a*xQ8HETegD73ZuO8*LWD0yQSPkU&pt_uistyle=5&pt_randsalt=0&pt_vcode_v1=0&pt_verifysession_v1={verifysession}".format(qq=qq, p=password, verify=verify.lower(), verifysession=verify_session)
    thread_qq.sign_url = sign_url
    thread_qq.login()

    for i in range(0, 5):
        exec("thread%s = thread.Thread(target=thread_qq.run)" % i)
        exec("thread%s.setDaemon(True)" % i)
        exec("thread%s.start()" % i)
        save_log("thread %s start \n" % i)
        time.sleep(5)

    first_login = False

    # Restart everyday
    timer_ = thread.Thread(target = timer, args = [time.time(), thread_qq.captcha])
    timer_.setDaemon(True)
    timer_.start()

    # Default value is 10, every keep_live while set value to 10. If check_thread return False means it should be restart.
    alive = 10

    while 1:
        if thread_qq.timeout == 1:
            save_log("session close")
            break
        time.sleep(100)
        if check_thread():
            alive -= 4
        else:
            break


def save_log(msg):
    try:
        # print msg
        logging.basicConfig(filename = log, level = logging.DEBUG)
        logging.debug(msg + "  " + time.asctime())
    except:
        save_log(catch_error())


def catch_error():
    exc_info = traceback.format_exc()
    return exc_info

def timer(start_time, captcha):
    while time.time() - start_time < 24*60*60:
        time.sleep(60)
        save_log("running: %smin" % ((time.time()-start_time)/60))
        if thread_qq.timeout == 1 or thread_qq.captcha != captcha:
            break
    thread_qq.timeout = 1

def check_thread():
    global alive
    if alive <= 0 :
        return False
    else:
        return True

def msg_add_border(msg):
    new_msg = u""
    data = msg.split(u"\\\\n")
    #pdb.set_trace()
    for i in data:
        temp = ""
        for j in i:
            temp += u"%s\u0489" % j
        if temp != "":
            new_msg += "[%s]\\\\n" % temp
    return new_msg
    
def send_email(msg):
    global receiver, send
    sender = "QQ_Bot@localhost"
    if send == True:
        try:
            send_mail = smtplib.SMTP('localhost')
            send_mail.sendmail(sender, [receiver], msg)
        except:
            save_log(catch_error())


if __name__ == "__main__":
    # set utc +8
    os.environ["TZ"] =  "Asia/Shanghai"
    time.tzset()

    global verify_path, log, EVE
    EVE = eve_mod.Eve_Jump()

    # First login input captcha without waiting.
    global first_login
    first_login = True

    # If send == True, send email to receiver when meet error or need captcha.But the email maybe in trash...
    global receiver, send
    qq, password, verify_path, log, receiver, send = Config.set_config()

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
            save_log(catch_error())
            if flag >= 5:
                break
                send_email("The application has encountered an unexpected error and needs to close.")
