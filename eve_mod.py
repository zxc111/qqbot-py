#-*- encoding: utf-8 -*-
import urllib
import os, sys
import traceback
import traceback
import logging
import MySQLdb as sql
import re
import pdb


class Eve_Jump():
    def __init__(self):
        self.url = "http://evemaps.dotlan.net/route/"
        self.db = sql.connect(host = "127.0.0.1", user = "root", db = "eve", use_unicode=True, charset="utf8")
        self.cur = self.db.cursor()

    def translation_cn_to_en(self, cn):
        only = re.compile(ur"[\u4e00-\u9fa5a-z0-9A-Z/-]+")
        cn = only.findall(cn)
        self.cur.execute("select * from map where cn = '%s'" % cn[0])
        data = self.cur.fetchall()
        data = data[0][1].strip(" ")
        data = data.replace(" ", "_", data.count(" "))
        return data

    def get_data(self, where):
        try:
            self.data = urllib.urlopen(self.url + where).read()
        except:
            print traceback.print_exc()
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
        for id in res:
            i += 1
            self.cur.execute("select * from map where id = %s" % int(id[7:]))
            data = self.cur.fetchall()
            #print data[0]
            current = "%s:%s" % (i, data[0][2])
            result = "%s %s" % (result, current)
        #print result
        return result

    ###NOTE: category 0: route, 1: jump_count. 
    ###      mode: 1:fast route, 2:highSec, 3:low/0.0 Sec
    def find_solarSystem_jump_or_route(self, start, end, mode, category):
        try:
            #pdb.set_trace()
            print start, end
            start_en = self.translation_cn_to_en(start.upper())
            end_en = self.translation_cn_to_en(end.upper())
            self.get_data("%s:%s:%s" % (mode, start_en, end_en))
            path = self.parser_html()
            print path
            if category == 0:
                return self.find_path(path[0])
            else:
                return u"%s 至 %s 共经过 %s 次跳跃。" % (start, end, path[1])
        except:
            print traceback.print_exc()
            return ""

    def find_hole(self, id):
        try:
            id = id.upper()
            only = re.compile(ur"[\u4e00-\u9fa5a-z0-9A-Z/-]+")
            id = only.findall(id)
            if len(id[0]) == 7:
                id = id[0][1:]
            else:
                id = id[0]
            self.cur.execute("select * from wormhole where id = '%s'" % ("J" + id))
            data = self.cur.fetchall()
            if data:
                print u"虫洞: %s, 等级: %s, 天象: %s, 永连洞口: %s" % (data[0][0], data[0][1], data[0][2], data[0][3])
                return u"虫洞: %s, 等级: %s, 天象: %s, 永连洞口: %s" % (data[0][0], data[0][1], data[0][2], data[0][3])
            else:
                return u"无该洞资料"
        except:
            print traceback.print_exc()
            return u"无该洞资料."
