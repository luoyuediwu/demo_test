#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""
#-*-coding:utf8-*-

import re
import string
import sys
import os
import urllib
import urllib2
from bs4 import BeautifulSoup
import requests
import shutil
import time
from lxml import etree

reload(sys)
sys.setdefaultencoding('utf-8')
user_id = 2612352067
cookie = {"Cookie": "SCF=AkFLagzIi9_s42ySgsAB7nCxgr5DqW6KPmX6q5ppPpcWCiGWPo0e8lfS6XXuy9f-AGr97cyf0JBA0RV5M9ZiuPs.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFoP.yF2ZczDSXA3wRE2TVy5JpX5KMhUgL.FozpeoM7e0BpS0B2dJLoI7DjUgv4UgH.IPUf; _T_WM=aead0cb18f61809eb499dc7d43e39dee; TMPTOKEN=OHfOKPu0v4RbOEzmy1ueV3rtAKR7iHVXFFjQM6cbNBhnnRM1re3Gs9Upu6iRoCWc; SUB=_2A253TagqDeRhGeRP6VUR8yrNzDiIHXVUschirDV6PUJbkdBeLWLckW1NUFaWKIH9R5F9wYuCj45aTxBuQ3G2XGdQ; SUHB=0z1x-aimfKQLvO; SSOLoginState=1514788986; H5_INDEX=3; H5_INDEX_TITLE=luoyuediwu; M_WEIBOCN_PARAMS=featurecode%3D20000320%26luicode%3D10000011%26lfid%3D2308692612352067_-_mix"}
url = 'http://weibo.cn/u/%d?filter=1&page=1'%user_id
html = requests.get(url, cookies = cookie).content
selector = etree.HTML(html)
pageNum = (int)(selector.xpath('//input[@name="mp"]')[0].attrib['value'])

result = ""
urllist_set = set()
word_count = 1
image_count = 1

print u'ready'
print pageNum
sys.stdout.flush()
times = 5
one_step = pageNum/times
for step in range(times):
    if step < times - 1:
        i = step * one_step + 1
        j =(step + 1) * one_step + 1
    else:
        i = step * one_step + 1
        j =pageNum + 1
    for page in range(i, j):
        #获取lxml页面
        try:
            url = 'http://weibo.cn/u/%d?filter=1&page=%d'%(user_id,page)
            lxml = requests.get(url, cookies = cookie).content
            #文字爬取
            selector = etree.HTML(lxml)
            content = selector.xpath('//span[@class="ctt"]')
            for each in content:
                text = each.xpath('string(.)')
                if word_count >= 3:
                    text = "%d: "%(word_count - 2) +text+"\n"
                else :
                    text = text+"\n\n"
                result = result + text
                word_count += 1
            print page,'word ok'
            sys.stdout.flush()
            soup = BeautifulSoup(lxml, "lxml")
            urllist = soup.find_all('a',href=re.compile(r'^http://weibo.cn/mblog/oripic',re.I))
            urllist1 = soup.find_all('a',href=re.compile(r'^http://weibo.cn/mblog/picAll',re.I))
            for imgurl in urllist:
                imgurl['href'] = re.sub(r"amp;", '', imgurl['href'])
        #       print imgurl['href']
                urllist_set.add(requests.get(imgurl['href'], cookies = cookie).url)
                image_count +=1
            for imgurl_all in urllist1:
                html_content = requests.get(imgurl_all['href'], cookies = cookie).content
                soup = BeautifulSoup(html_content, "lxml")
                urllist2 = soup.find_all('a',href=re.compile(r'^/mblog/oripic',re.I))
                for imgurl in urllist2:
                    imgurl['href'] = 'http://weibo.cn' + re.sub(r"amp;", '', imgurl['href'])
                    urllist_set.add(requests.get(imgurl['href'], cookies = cookie).url)
                    image_count +=1
                image_count -= 1
            print page,'picurl ok'
        except:
            print page,'error'
        print page, 'sleep'
        sys.stdout.flush()
        time.sleep(60)
    print u'正在进行第', step + 1, u'次停顿，防止访问次数过多'
    time.sleep(300)

try:
    fo = open(os.getcwd()+"/%d"%user_id, "wb")
    fo.write(result)
    word_path=os.getcwd()+'/%d'%user_id
    print u'文字微博爬取完毕'
    link = ""
    fo2 = open(os.getcwd()+"/%s_image"%user_id, "wb")
    for eachlink in urllist_set:
        link = link + eachlink +"\n"
    fo2.write(link)
    print u'图片链接爬取完毕'
except:
    print u'存放数据地址有误'
sys.stdout.flush()

if not urllist_set:
    print u'该用户原创微博中不存在图片'
else:
    #下载图片,保存在当前目录的pythonimg文件夹下
    image_path=os.getcwd()+'/weibo_image'
    if os.path.exists(image_path) is False:
        os.mkdir(image_path)
    x = 1
    for imgurl in urllist_set:
        temp= image_path + '/%s.jpg' % x
        print u'正在下载第%s张图片' % x
        try:
        # urllib.urlretrieve(urllib2.urlopen(imgurl).geturl(),temp)
            r = requests.get(imgurl, stream=True)
            if r.status_code == 200:
                with open(temp, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
        except:
            print u"该图片下载失败:%s"%imgurl
        x += 1
print u'原创微博爬取完毕，共%d条，保存路径%s'%(word_count - 3,word_path)
print u'微博图片爬取完毕，共%d张，保存路径%s'%(image_count - 1,image_path)
