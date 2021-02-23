import requests

import time
from hex2b64 import HB64
import RSAJS
import json
import os
import bs4
from multiprocessing import Pool, Manager
import re


class SpiderOfGxu:

    def __init__(self, user, pwd):

        self.session = requests.session()
        self.user = user
        self.pwd = pwd
        self.headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        }
        self.time = int(time.time() * 1000)
        self.xkkz_id = ''
        self.courses = Manager().list()
        self.host = 'http://jwxt2018.gxu.edu.cn'
        self.selectedCourses = Manager().list()

    def login(self):
        hosts = ['http://210.36.22.54', 'http://210.36.22.57', 'http://210.36.22.59', 'http://210.36.22.219',
                 'http://jwxt2018.gxu.edu.cn', ]
        for i in range(1, 12):
            i = str(i)
            if int(i) < 10:
                i = '0' + i
            hosts.append('http://jwgl2018' + i + '.gxu.edu.cn')
        flag = 0
        for host in hosts:
            self.host = host
            try:
                self._get_public()
                self._get_csrftoken()
                self._post_data()
                flag = 1
                break
            except Exception:
                print('当前服务器 %s 过载 开始尝试下一个...' % host)
        if flag == 1:
            print('登录成功,当前服务器%s' % self.host)

    def _get_public(self):
        url = self.host + '/jwglxt/xtgl/login_getPublicKey.html'
        r = self.session.get(url)
        self.pub = r.json()

    def _get_csrftoken(self):
        url = self.host + '/jwglxt/xtgl/login_slogin.html'
        r = self.session.get(url)
        htm = bs4.BeautifulSoup(r.text, "html.parser")
        self.csrftoken = htm.select("#csrftoken")[0]["value"]

    def _process_public(self, pwd):
        self.exponent = HB64().b642hex(self.pub['exponent'])
        self.modulus = HB64().b642hex(self.pub['modulus'])
        rsa = RSAJS.RSAKey()
        rsa.setPublic(self.modulus, self.exponent)
        cry_data = rsa.encrypt(pwd)
        return HB64().hex2b64(cry_data)

    def _post_data(self):
        ras_pw = self._process_public(self.pwd)
        url = self.host + '/jwglxt/xtgl/login_slogin.html'
        data = {
            'csrftoken': self.csrftoken,
            'language': "zh_CN",
            'yhm': self.user,
            'mm': ras_pw,
            'mm': ras_pw,
        }

        r = self.session.post(url, headers=self.headers, data=data)
        pattern = r'用户名或密码不正确'
        if re.search(pattern, r.text) is not None:
            print('登录不成功')
            raise Exception()

    def _prepare_userinfo(self, ignore_classtype=False):
        #

        #
        form = {}

        url_zzxk = self.host + '/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default&su=' + self.user
        r = self.session.get(url=url_zzxk, headers=self.headers)

        htm = bs4.BeautifulSoup(r.text, "html.parser")
        a = ['xqh_id', 'jg_id_1', 'zyh_id', 'zyfx_id', 'njdm_id', 'bh_id', 'xbm', 'xslbdm', 'ccdm', 'xsbj', 'xkxnm',
             'xkxqm', ]

        for i in a:
            select_i = '#' + i
            form[i] = htm.select(select_i)[0]['value']
        pattern = r'queryCourse.......(\d*)...(\w*).*?>(.*?)<\/a>'
        res = re.findall(pattern, r.text, re.S)
        print()

        url = self.host + '/jwglxt/xsxk/zzxkyzb_cxZzxkYzbDisplay.html?gnmkdm=N253512&su=' + self.user
        if not ignore_classtype:

            print('目前可选课程为:')
            for id, item in enumerate(res):
                print(id, item[2])
            mode = int(input('请输入要选择课程类别，（填数字，编号从0开始）'))
            form['xkkz_id'] = res[mode][1]
            self.xkkz_id = form['xkkz_id']
            form['kklxdm'] = res[mode][0]
            print(form)

        data = {
            "xkkz_id": self.xkkz_id,
            "xszxzt": "1",
            "kspage": "0",
            "jspage": "0"
        }

        r = self.session.post(url=url, data=data, headers=self.headers)
        htm = bs4.BeautifulSoup(r.text, 'html.parser')
        form.setdefault('rwlx', htm.select('#rwlx')[0]['value'])
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

    def _get_TmpList(self):

        form = self._prepare_userinfo()

        form['kspage'] = '1'
        form['jspage'] = '2000'
        form['jxbzb'] = ''
        course_url = self.host + '/jwglxt/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512&su=' + self.user
        course_list = self.session.post(course_url, data=form)
        return json.loads(course_list.text)['tmpList']

    def _get_target_info(self):


        tmp_list = self._get_TmpList()
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
            if item['kcmc'] not in names:
                course_info.append({
                    'kch_id': item['kch_id'],
                    'cxbj': item['cxbj'],
                    'fxbj': item['fxbj']
                })
                names.append(item['kcmc'])
        return course_info, names

    def run(self):
        url = self.host + '/jwglxt/xsxk/zzxkyzbjk_cxJxbWithKchZzxkYzb.html?gnmkdm=N253512&su=' + self.user
        url_xuanke = self.host + '/jwglxt/xsxk/zzxkyzbjk_xkBcZyZzxkYzb.html?gnmkdm=N253512&su=' + self.user

        course_info, names = self._get_target_info()
        # print(course_info)
        print(names)
        pool = Pool(processes=30)  # 30个进程

        for id, item_info in enumerate(course_info):
            form = {**item_info, **self.form}
            form['qz'] = '0'  # 不懂是什么key
            pool.apply_async(self._unfold_courseList,
                             args=(url, form, names[id], item_info['kch_id'],))  # 这里的course就是点击展开的课程，一个课程里面有许多个班

        pool.close()
        pool.join()

        while len(self.selectedCourses) < 1:  # 还没选上课
            pool2 = Pool(processes=3)
            for item in self.courses:
                isTarget = (item['course_name'] in XUANXIUKE_TARGET) or (item['xingzhi'] in PE_TARGET) or item[
                    'xingzhi'] in BIXIU_TARGET
                if isTarget:
                    form = {**self.form, **item}
                    form['qz'] = '0'
                    pool2.apply_async(self._click_xuanke, (url_xuanke, form, item['course_name'],))
            pool2.close()
            pool2.join()

        print('选课成功，已选%d门'% len(self.selectedCourses))

    def _click_xuanke(self, url_xuanke, form, name):
        try:
            if len(self.selectedCourses) < 1:
                print('正在选择 %s ...' % name)

                r = self.session.post(url=url_xuanke, data=form, headers=self.headers)
                print(r.text)
                if r.text.find('msg') == -1:
                    self.selectedCourses.append(name)

        except Exception:
            pass

    def _unfold_courseList(self, url, form, name, kch):

        # print('当前线程' + str(os.getpid()) + '展开 ' + name + ' ...')
        course = self.session.post(url=url, data=form, headers=self.headers)
        course = json.loads(course.text)
        # print(course)
        for item in course:
            tmp = {
                'jxb_ids': item['do_jxb_id'],
                'course_name': name,
                'xingzhi': item['kcxzmc'],
                'kch_id': kch  # 这个只有在tmpList里面有但是选课又需要所以传递回去，同一类课程这个是一样的
            }

            self.courses.append(tmp)

    def display_selected(self):
        url = self.host + '/jwglxt/xsxk/zzxkyzb_cxZzxkYzbChoosedDisplay.html?gnmkdm=N253512&su=' + self.user
        r = self.session.post(url=url, data=self._prepare_userinfo(ignore_classtype=True), headers=self.headers)
        selected_list = json.loads(r.text)
        print()
        for item in selected_list:
            print('课程号', item['kch'])
            print('教学班id', item['jxb_id'])
            print('名称 ', item['jxbmc'])
            print('老师 ', item['jsxx'])
            print()
        print('共计 %d 门' % len(selected_list))
        mode = input('是否要退课,按1确认 按0 取消')
        if mode == '1':
            kch = input('请输入退课的课程号')
            id = input('教学班id')
            self._tuike(id, kch)

    def _tuike(self, jxb_id, kch_id):
        tuike_url = self.host + '/jwglxt/xsxk/tjxkyzb_tuikBcTjxkYzb.html?gnmkdm=N253511&su=' + self.user

        # form = {
        #     'jxb_ids':'BAD25334D3631503E053030410AC8FA5',
        #     'kch_id':'1435543',
        #     'xkkz_id':self.xkkz_id,
        #     'qz':'0',
        # }
        form = {
            'jxb_ids': jxb_id,
            'kch_id': kch_id,
            'xkkz_id': self.xkkz_id,
            'qz': 0
        }
        form = {**form, **self.form}
        r = self.session.post(url=tuike_url, data=form, headers=self.headers)
        if r.text == "1":
            print('退课成功！')


if __name__ == '__main__':
    global XUANXIUKE_TARGET  # 选修课
    global PE_TARGET  # 体育课
    global BIXIU_TARGET  # 必修课

    XUANXIUKE_TARGET = ['走进东盟', '东南亚风情', '东南亚戏剧文化',]  # 只会选择有这些名称的课程
    PE_TARGET = ['游泳']
    BIXIU_TARGET = ['数据库原理','计算机网络原理','	算法设计与分析（全英）']

    test = SpiderOfGxu(user='', pwd='')
    test.login()

    while True:
        op = input('操作1:选课,\n操作2:显示已选课程')
        if op == '1':
            test.run()
        elif op == '2':
            test.display_selected()
