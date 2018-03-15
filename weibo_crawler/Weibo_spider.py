#!/usr/bin/env python
#coding=utf-8

import requests
import re
import os
import os.path
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class WeiboSpider():
    def __init__(self, url_info):
        self.cookie = {"Cookie":"SCF=AkFLagzIi9_s42ySgsAB7nCxgr5DqW6KPmX6q5ppPpcWCiGWPo0e8lfS6XXuy9f-AGr97cyf0JBA0RV5M9ZiuPs.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFoP.yF2ZczDSXA3wRE2TVy5JpX5KMhUgL.FozpeoM7e0BpS0B2dJLoI7DjUgv4UgH.IPUf; _T_WM=aead0cb18f61809eb499dc7d43e39dee; TMPTOKEN=OHfOKPu0v4RbOEzmy1ueV3rtAKR7iHVXFFjQM6cbNBhnnRM1re3Gs9Upu6iRoCWc; SUB=_2A253TagqDeRhGeRP6VUR8yrNzDiIHXVUschirDV6PUJbkdBeLWLckW1NUFaWKIH9R5F9wYuCj45aTxBuQ3G2XGdQ; SUHB=0z1x-aimfKQLvO; SSOLoginState=1514788986; H5_INDEX=3; H5_INDEX_TITLE=luoyuediwu; M_WEIBOCN_PARAMS=featurecode%3D20000320%26luicode%3D10000011%26lfid%3D2308692612352067_-_mix"}
        self.name = url_info['name']
        self.homeUrl = url_info['url']
        self.images = []
        if not os.path.exists('./weibo_images'):
            os.mkdir('./weibo_images')
        if not os.path.exists('./weibo_images/'+self.name):
            os.mkdir('./weibo_images/'+self.name)

    def __load_page(self, pageNo):
        """加载html页面"""
        url = self.homeUrl + '?page=' + str(pageNo)
        return requests.get(url=url, cookies=self.cookie).content 

    def __process_data(self, htmlPage):
        """ 从html页面中提取图片的信息 """
        pic_url = re.findall(r'http://ww.\.sinaimg.cn/wap180/\w+.\w{3,4}', htmlPage)
        for url in pic_url:
            url = url.replace('wap180', 'large')
            info = {}
            info['name'] = re.findall(r'\w{32}.\w{3,4}', url)[0]
            info['url'] = url
            self.images.append(info)

    def __save_image(self, imageName, content):
        """ 保存图片 """
        print imageName
        with open(imageName, 'wb') as fp:
            fp.write(content)

    def get_image_info(self, page=1):
        """ 得到图片信息 """
        for i in range(page):
            self.__process_data(self.__load_page(i+1))

    def down_images(self):
        """ 下载图片 """
        print "{} images will be download".format(len(self.images))
        for key, image in enumerate(self.images):
            print 'download {0} ...'.format(key+1)
            try:
                req = requests.get(image["url"])
            except :
                print 'error'
            imageName = os.path.join("./weibo_images/" + self.name + '/', image["name"])
            self.__save_image(imageName, req.content)

if __name__ == '__main__':
    urls_info = [
        {"name":"EXO", "url":"http://weibo.cn/u/2612352067"}
    ]

    print '\n************************开始爬虫************************'
    for url_info in urls_info:
        spider = WeiboSpider(url_info)
        spider.get_image_info(100)
        spider.down_images()
    print '************************爬虫完成************************\n'