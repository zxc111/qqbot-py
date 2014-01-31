#-*- encoding: utf-8 -*-
import urllib
import os, sys
import traceback
import logging
import MySQLdb as sql
import re
from xpinyin import Pinyin
import pdb


class Eve_Jump():
    def __init__(self):
        self.url_route = "http://evemaps.dotlan.net/"

    def connect_sql(self):
        try:
            self.db = sql.connect(host = "127.0.0.1", user = "root", db = "eve", use_unicode=True, charset="utf8")
            self.cur = self.db.cursor()
        except:
            traceback.print_exc()

    def translation_cn_to_en(self, cn):
        p = Pinyin()
        only = re.compile(ur"[\u4e00-\u9fa5a-z0-9A-Z/-]+")
        cn = only.findall(cn)
        pinyin = p.get_pinyin(cn[0], '')
        self.cur.execute("select * from map where pinyin like '%s%%'" % pinyin)
        data = self.cur.fetchall()
        print data
        en = data[0][1].strip(" ")
        en = en.replace(" ", "_", data.count(" "))
        cn = data[0][2].strip(" ")
        number = data[0][0]
        return en , cn, number

    def get_data(self, where):
        try:
            self.data = urllib.urlopen(self.url_route + where).read()
        except:
            traceback.print_exc()
            return "error"

    def parser_html(self):
        begin_path = self.data.find('<table cellpadding="3" cellspacing="1" border="0" width="100%" class="table')
        end_path = self.data.find('<div align="right" style="padding-top: 10px;">Kills/Jumps in the last 3 hours</div>')
        self.data = self.data[ begin_path : end_path ]
        count = self.data.count("link-5")
        p = re.compile(r'link-5-\d+')
        res = p.findall(self.data)
        return res, count

    def find_path(self, res):
        result = ""
        i = 0
        for id in res:
            i += 1
            self.cur.execute("select * from map where id = %s" % int(id[7:]))
            data = self.cur.fetchall()
            current = "%s:%s" % (i, data[0][2])
            result = "%s %s" % (result, current)
        return result

    ###NOTE: category 0: route, 1: jump_count. 
    ###      mode: 1:fast route, 2:highSec, 3:low/0.0 Sec
    def find_solarSystem_jump_or_route(self, start, end, mode, category):
        self.connect_sql()
        try:
            start_en, start_cn, start_number = self.translation_cn_to_en(start.lower())
            end_en, end_cn, end_number = self.translation_cn_to_en(end.lower())
            #NOTE: url options
            self.get_data("route/%s:%s:%s" % (mode, start_en, end_en))
            path = self.parser_html()
            print path
            if category == 0:
                return self.find_path(path[0])
            else:
                return u"%s 至 %s 共经过 %s 次跳跃。" % (start_cn, end_cn, path[1] - 1)
        except:
            self.db.close()
            traceback.print_exc()
            return ""

    def find_hole(self, id):
        self.connect_sql()
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
            self.db.close()
            traceback.print_exc()
            return u"无该洞资料."

    def jump_range(self, place, target):
        self.connect_sql()
        try:
            place_en, place_cn, place_number = self.translation_cn_to_en(place.lower())
            target_en, target_cn, target_number  = self.translation_cn_to_en(target.lower())
            self.get_data("range/Thanatos,5/%s" % place_en )
            path = self.parser_html()
            p = re.compile(r'\s\d+\.\d+\sly')
            warp_distance = p.findall(self.data)
            res = []
            for i in path[0]:
                res.append(long(i[7:]))
            res.remove(res[0])
            if target_number in res:
                number = res.index(target_number)
                print u"%s 至 %s 跳跃距离: %s" % (place_cn, target_cn, warp_distance[number])
                return u"%s 至 %s 跳跃距离: %s" % (place_cn, target_cn, warp_distance[number])
            else:
                print u"%s不再跳跃范围内" % target_cn
                return u"%s不在跳跃范围内" % target_cn
            #self.find_path(path[0])
        except:
            self.db.close()
            traceback.print_exc()
            return ""

