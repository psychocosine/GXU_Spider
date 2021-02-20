import requests
from lxml import etree
import time
from hex2b64 import HB64
import RSAJS
import json
import getpass
import sys
import rsa
import base64
import bs4
import re


class Login:

    def __init__(self, user, pwd):

        self.session = requests.session()
        self.user = user
        self.pwd = pwd
        self.headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        }
        self.time = int(time.time() * 1000)
        self.xkkz_id = 'BA1FF77CF45ED1FCE053020410AC6CFA'
    # def get_time(self):
    #     return int(time.time()*1000)

    def get_public(self):
        url = 'http://jwxt2018.gxu.edu.cn/jwglxt/xtgl/login_getPublicKey.html'
        r = self.session.get(url)
        self.pub = r.json()

    def get_csrftoken(self):
        url = 'http://jwxt2018.gxu.edu.cn/jwglxt/xtgl/login_slogin.html'
        r = self.session.get(url)
        htm = bs4.BeautifulSoup(r.text, "html.parser")
        self.csrftoken = htm.select("#csrftoken")[0]["value"]

    def process_public(self, pwd):
        self.exponent = HB64().b642hex(self.pub['exponent'])
        self.modulus = HB64().b642hex(self.pub['modulus'])
        rsa = RSAJS.RSAKey()
        rsa.setPublic(self.modulus, self.exponent)
        cry_data = rsa.encrypt(pwd)
        return HB64().hex2b64(cry_data)

    def post_data(self):
        ras_pw = self.process_public(self.pwd)
        url = 'http://jwxt2018.gxu.edu.cn/jwglxt/xtgl/login_slogin.html'
        data = {
            'csrftoken': self.csrftoken,
            'language': "zh_CN",
            'yhm': self.user,
            'mm': ras_pw,
            'mm': ras_pw,
        }

        # print(en_pwd)

        r = self.session.post(url, headers=self.headers, data=data)
        # print(r.text)
    def login_zzxk(self):
        # 获取头部的一些信息
        url = 'http://jwxt2018.gxu.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default&su='+self.user
        r = self.session.post(url, data={
            'gndm':"N253512"
        }, headers=self.headers)
        # {
        #     "rwlx": "2",
        #     "xkly": "0",
        #     "bklx_id": "0",
        #     "xqh_id": "1",!!!
        #     "jg_id": "30700",!!!
        #     "zyh_id": "0731",!!!
        #     "zyfx_id": "wfx",!!!
        #     "njdm_id": "2019",!!!
        #     "bh_id": "19073105",!!!
        #     "xbm": "1",!!!
        #     "xslbdm": "421",!!!
        #     "ccdm": "21",!!!
        #     "xsbj": "4294967296",!!!
        #     "sfkknj": "0",
        #     "sfkkzy": "0",
        #     "sfznkx": "0",
        #     "zdkxms": "0",
        #     "sfkxq": "0",
        #     "sfkcfx": "0",
        #     "kkbk": "0",
        #     "kkbkdj": "0",
        #     "xkxnm": "2020",!!!
        #     "xkxqm": "12",!!!
        #     "rlkz": "0",
        #     "kklxdm": "05",  05是体育课代码

        #     "kch_id": "1411112",
        #     "xkkz_id": "BA1FF77CF45ED1FCE053020410AC6CFA",
        #     "cxbj": "0",
        #     "fxbj": "0"
        # }
        htm = bs4.BeautifulSoup(r.text, "html.parser")
        a = ['xqh_id', 'jg_id_1', 'zyh_id', 'zyfx_id', 'njdm_id', 'bh_id', 'xbm', 'xslbdm', 'ccdm', 'xsbj', 'xkxnm', 'xkxqm', ]
        
        dic ={}
        for i in a:
            select_i = '#' + i
            dic[i] = htm.select(select_i)[0]['value']
        return dic

    def prepare_form(self):
        #
        # 神秘的xkkz_id
        # 体育课 :"BA1FF77CF45ED1FCE053020410AC6CFA"
        # 主修课程 xkkz_id:"BA1FAE592422B2B4E053020410ACF2FE"
        # 通识选修课 xkkz_id:"BADF378C0C89FC5BE053030410AC7C59"
        # 特殊课程 BA1F4A5AEB009336E053030410ACE26E
        # 其他特殊课程 BA1D5E1515DA4941E053030410ACA7D9
        #
        form = self.login_zzxk() 

        url = 'http://jwxt2018.gxu.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbDisplay.html?gnmkdm=N253512&su='+self.user
        query = input('请问需要什么类型的课？1：主修，2：体育，3：校选课')
        if query == '1':
            form['kklxdm'] = '01'
            form['xkkz_id'] = 'BA1FAE592422B2B4E053020410ACF2FE'
            self.xkkz_id = 'BA1FAE592422B2B4E053020410ACF2FE'
        elif query == '2':
            form['kklxdm'] = '05'
            form['xkkz_id'] = 'BA1FF77CF45ED1FCE053020410AC6CFA'
            self.xkkz_id = 'BA1FF77CF45ED1FCE053020410AC6CFA'
        elif query == '3':
            form['kklxdm'] = '10'
            form['xkkz_id'] = 'BBA0DCA9E236261BE053020410ACCC5C'
            self.xkkz_id = 'BBA0DCA9E236261BE053020410ACCC5C'
        data = {
            "xkkz_id": self.xkkz_id,
            "xszxzt": "1",
            "kspage": "0",
            "jspage": "0"
        }

        r = self.session.post(url=url, data=data, headers=self.headers)
        # {
        #     "rwlx": "2",
        #     "xkly": "0",
        #     "bklx_id": "0",
        #     "xqh_id": "1",!!!
        #     "jg_id": "30700",!!!
        #     "zyh_id": "0731",!!!
        #     "zyfx_id": "wfx",!!!
        #     "njdm_id": "2019",!!!
        #     "bh_id": "19073105",!!!
        #     "xbm": "1",!!!
        #     "xslbdm": "421",!!!
        #     "ccdm": "21",!!!
        #     "xsbj": "4294967296",!!!
        #     "sfkknj": "0",
        #     "sfkkzy": "0",
        #     "sfznkx": "0",
        #     "zdkxms": "0",
        #     "sfkxq": "0",
        #     "sfkcfx": "0",
        #     "kkbk": "0",
        #     "kkbkdj": "0",
        #     "xkxnm": "2020",!!!
        #     "xkxqm": "12",!!!
        #     "rlkz": "0",
        #     "kklxdm": "05",  05是体育课代码

        #     "kch_id": "1411112",
        #     "xkkz_id": "BA1FF77CF45ED1FCE053020410AC6CFA",
        #     "cxbj": "0",
        #     "fxbj": "0"
        # }
        htm = bs4.BeautifulSoup(r.text, 'html.parser')
        form.setdefault('rwlx',htm.select('#rwlx')[0]['value'])
        form.setdefault('xkly', htm.select('#xkly')[0]['value'])
        form.setdefault('bklx_id', htm.select('#bklx_id')[0]['value'])
        form.setdefault('sfkknj', htm.select('#sfkknj')[0]['value'])
        form.setdefault('sfkkzy', htm.select('#sfkkzy')[0]['value'])
        form.setdefault('sfznkx', htm.select('#sfznkx')[0]['value'])
        form.setdefault('zdkxms', htm.select('#zdkxms')[0]['value'])
        form.setdefault('sfkxq', htm.select('#sfkxq')[0]['value'])
        form.setdefault('sfkcfx', htm.select('#sfkcfx')[0]['value'])
        form.setdefault('kkbk', htm.select('#kkbk')[0]['value'])
        form.setdefault('kkbkdj', htm.select('#kkbkdj')[0]['value'])
        form.setdefault('rlkz', htm.select('#rlkz')[0]['value'])
        form.setdefault('rlzlkz', htm.select('#rlzlkz')[0]['value'])
        form.setdefault('sfkgbcx', htm.select('#sfkgbcx')[0]['value'])
        form.setdefault('sfrxtgkcxd', htm.select('#sfrxtgkcxd')[0]['value'])
        form.setdefault('tykczgxdcs', htm.select('#tykczgxdcs')[0]['value'])
        form.setdefault('xkzgbj', htm.select('#xkzgbj')[0]['value'])
        form.setdefault('xklc', htm.select('#xklc')[0]['value'])
        self.form = form
        
        return form
        
    def get_CourseList(self):
        

        form = self.prepare_form()
        
        form['kspage'] = '1'
        form['jspage'] = '1000'
        form['jxbzb'] = ''
        course_url = 'http://jwxt2018.gxu.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512&su=' + self.user
        course_list = self.session.post(course_url, data=form)
        # print(form)
        # print(course_list.json())
        # fp = open('tmp.json', 'w',encoding='utf-8')
        # fp.write(course_list.text)
        # fp.close()

        return json.loads(course_list.text)['tmpList']




    def get_target_info(self):
        tmp_list = self.get_CourseList()
        print('获取到如下课程')
        course_dic = {}
        for item in tmp_list:
            name = item['kcmc']
            if name not in course_dic.keys():
                course_dic.setdefault(name, 1)
            else:
                course_dic[name] += 1
        # for k,v in course_dic.items():
        #     print(k, '教学班数量'+str(v))


        names = []
        course_info = []
        for item in tmp_list:
            # if item['kcmc'] == target_course_name:
            #     return {
            #         'kch_id': item['kch_id'],
            #         'cxbj': item['cxbj'],
            #         'fxbj':item['fxbj']
            #     }
            if int(item['yxzrs']) <= 100:
                course_info.append({
                        'kch_id': item['kch_id'],
                        'cxbj': item['cxbj'],
                        'fxbj': item['fxbj']
                })
                names.append(item['kcmc'])
        return course_info, names
        

    def run(self):
        url = 'http://jwxt2018.gxu.edu.cn/jwglxt/xsxk/zzxkyzbjk_cxJxbWithKchZzxkYzb.html?gnmkdm=N253512&su=' + self.user
        url_xuanke = 'http://jwxt2018.gxu.edu.cn/jwglxt/xsxk/zzxkyzbjk_xkBcZyZzxkYzb.html?gnmkdm=N253512&su=' +self.user
        cnt = 0

        course_info, names = self.get_target_info()
        while True:
            for id, item_info in enumerate(course_info):
                flag = 1
                form = {**item_info, **self.form}
                print('正在尝试选 ' + names[id] + ' ...')
                course = self.session.post(url=url, data=form, headers=self.headers)
                course = json.loads(course.text)
                if course[0]['kcxzmc'] not in['海洋课','东盟课','民族课']:
                    print('不是东盟或者海洋课')
                    continue
                form['qz'] = '0'

                for item in course:
                    form['jxb_ids'] = item['do_jxb_id']
                    r = self.session.post(url=url_xuanke, data=form, headers=self.headers)
                    print(r.text)
                    if r.text.find('msg')==-1:
                        cnt += 1
                        print('成功选上%d门 ，是否继续？' %(cnt))
                        mode = input('1:继续,2:取消')
                        if mode == '2':
                            exit(0)




test = Login(user='1924110237', pwd='123456jk')
test.get_public()
test.get_csrftoken()
test.post_data()

while True:
    op = input('操作?').strip()
    if op == '1':
        test.run()