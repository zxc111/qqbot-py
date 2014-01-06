#-*- encoding: utf-8 -*-
import urllib
import os, sys
import traceback
import MySQLdb as sql
import re
import pdb

class Eve_Jump():
    def __init__(self):
        self.url = "http://evemaps.dotlan.net/route/"

    def trans(self, cn):
        print cn
        #pdb.set_trace()
        only = re.compile(ur"[\u4e00-\u9fa5a-z0-9A-Z/-]+")
        cn = only.findall(cn)
        db = sql.connect(host = "127.0.0.1",user = "root", db = "eve", use_unicode=True, charset="utf8")
        cur = db.cursor()
        cur.execute("select * from map where cn = '%s'" % cn[0])
        data = cur.fetchall()
        db.close()
        data = data[0][1].strip(" ")
        data = data.replace(" ", "_", data.count(" "))
        return data

    def get_data(self, where):
        try:
            self.data = urllib.urlopen(self.url + where).read()
        except:
            return "error"

    def parser_html(self):
        begin_path = self.data.find('<table cellpadding="3" cellspacing="1" border="0" width="100%" class="tablelist table-tooltip">')
        end_path = self.data.find('<div align="right" style="padding-top: 10px;">Kills/Jumps in the last 3 hours</div>')
        self.data = self.data[ begin_path : end_path ]
        count = self.data.count("link-5")
        p = re.compile(r'link-5-\d+')
        res = p.findall(self.data)
        print res
        return res, count

    def find_path(self, res):
        result = ""
        i = 0
        db = sql.connect(host = "127.0.0.1",user = "root", db = "eve", use_unicode=True, charset="utf8")
        cur = db.cursor()
        for id in res:
            i += 1
            cur.execute("select * from map where id = %s" % int(id[7:]))
            data = cur.fetchall()
            #print data[0]
            current = "%s:%s" % (i, data[0][2])
            result = "%s %s" % (result, current)
        #print result
        db.close()
        return result

    def main(self, start, end, mode, category):
        try:
            #pdb.set_trace()
            start_en = self.trans(start)
            print start_en
            end_en = self.trans(end)
            print end_en
            self.get_data("%s:%s:%s" % (mode, start_en, end_en))
            path = self.parser_html()
            print path
            if category == 0:
                return self.find_path(path[0])
            else:
                return u"%s 至 %s 共经过 %s 次跳跃。" % (start, end, path[1])
        except:
            return ""

