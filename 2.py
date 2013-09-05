 
# -*- coding: UTF-8 -*-
import httplib2,urllib
import os,sys,re,hashlib

class QQ(object):
    #appid = "1003903"
    appid = "8000203"
    def __init__(self,uin,pwd):
        self.uin = uin
        self.pwd = pwd
        self.http = httplib2.Http()
        self.loginStatus = False
        self.loginMsg = "未登录"

    def __initVerifyCode(self):
        '''
                    初始化验证码
        '''
        checkUrl = "http://check.ptlogin2.qq.com/check?uin="+self.uin+"&appid="+self.appid+"&r=0.6315117976338621"
        headers = {"Cookie":"chkuin="+self.uin}
        response,content = self.http.request(checkUrl,headers=headers)
        pm = re.search(r"ptvfsession=(\\w+?);",response["set-cookie"])
        if pm and pm.group(1):
            self.ptvfsession = pm.group(1)
        #print content
        m = re.search(r"'(\\d)','(.+)','(.+)'", content)
        self.verifyCode1 = m.group(2)
        self.verifyCode2 = m.group(3)
        if m.group(1)=="0":
            print u"免验证码！"
        else:
            print u"需要输入验证码！"
            imgUrl = "http://captcha.qq.com/getimage?aid="+self.appid+"&r=0.3268821237981411&uin="+self.uin
            response,content = self.http.request(imgUrl)
            #print response["set-cookie"]
            mt = re.search(r"verifysession=(\\w+?);",response["set-cookie"])
            if mt and mt.group(1):
                self.verifysession = mt.group(1)
                with open("code.jpg","wb") as img:
                    img.write(content)
                self.verifyCode1 = raw_input(u"验证码下载完毕("+os.path.split(os.path.realpath(sys.argv[0]))[0]+os.sep+"code.jpg)，请输入：")
            else:
                print u"获取验证码出错！"
     
    def __encodePwd(self):
        '''
                    对密码加密
        '''
        def hex_md5hash(myStr):
            return hashlib.md5(myStr).hexdigest().upper()
        def hexchar2bin(uin):
            uin_final = ''
            uin = uin.split('\\\\x')
            for i in uin[1:]:
                uin_final += chr(int(i, 16))
            return uin_final
        password_1 = hashlib.md5(self.pwd).digest()
        password_2 = hex_md5hash(password_1 + hexchar2bin(self.verifyCode2))
        password_final = hex_md5hash(password_2 + self.verifyCode1.upper()) 
        self.pwdEncoded = password_final
         
    def __postLogin(self):
        '''
                    提交登录请求
        '''
        data = {"u":self.uin}
        data["p"] = self.pwdEncoded
        data["verifycode"] = self.verifyCode1
        data["webqq_type"] = "10"
        data["remember_uin"] = "1"
        data["login2qq"] = "1"
        data["aid"] = self.appid
        data["h"] = "1"
        data["u1"] = "http://imgcache.qq.com/club/portal_new/redirect.html?jump_url="
        data["ptredirect"] = "0"
        data["ptlang"] = "2052"
        data["from_ui"] = "1"
        data["pttype"] = "1"
        data["t"] = "1"
        data["g"] = "1"
        body = urllib.urlencode(data)
        loginUrl = "http://ptlogin2.qq.com/login?"+body
        headers = {"Cookie":"chkuin="+self.uin+"; confirmuin="+self.uin}
        try:
            headers["Cookie"] += "; verifysession="+self.verifysession
        except AttributeError:
            pass
        try:
            headers["Cookie"] += "; ptvfsession="+self.ptvfsession
        except AttributeError:
            pass
        #headers["Referer"] = "http://ui.ptlogin2.qq.com/cgi-bin/login?link_target=blank&target=self&appid=8000203&f_url=loginerroralert&s_url=http%3A//imgcache.qq.com/club/portal_new/redirect.html%3Fjump_url%3D"
        response,content = self.http.request(loginUrl,headers=headers)
        #print content
        m = re.search(r"'(\\d)','(.+)','(.+)','(.+)','(.+)', '(.+)'", content)
        if m:
            if m.group(1)!="0": #登录失败
                self.loginMsg = m.group(5)
            else:   #登录成功
                self.loginStatus = True
                self.loginMsg = m.group(5)
                self.cookie = response["set-cookie"]
        else:   #登录失败，不知道为什么，Fiddler拦截出来的失败结果和上面的格式一样的，程序却不是，只能暂时这样判断
            m = re.search(r"<span style=\\"font-size:13px; line-height:17px;\\">(.+?)</span></td>",content,re.DOTALL)
            self.loginMsg = m.group(1).strip()
             
    def login(self):
        self.__initVerifyCode()
        self.__encodePwd()
        self.__postLogin()

if __name__ == "__main__":
    qqApp = QQ("2752878938", "asqfsd1")
    qqApp.login()
    print qqApp.loginMsg
    #sys.exit(0)
#该片段来自于http://www.codesnippet.cn/detail/060620133843.html
