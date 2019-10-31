#!/usr/bin/python
#-*-coding:utf-8-*-

from django import forms
from django.conf import settings
import pymysql
import struct
import random

class MailItem():
    def __init__(self):
        self.type1 = 0;
        self.value11 = 0;
        self.value12 = 0;
        self.type2 = 0;
        self.value21 = 0;
        self.value22 = 0;
        self.type3 = 0;
        self.value31 = 0;
        self.value32 = 0;

    def get_strings(self):
        num = 0
        ctype = bytes();
        cvalue1 = bytes();
        cvalue2 = bytes();
        cvalue3 = bytes();
        if self.type1 > 0 and self.value11 > 0 and self.value12 > 0:
            num = num + 1
            ctype += struct.pack("i", self.type1)
            cvalue1 += struct.pack("i", self.value11)
            cvalue2 += struct.pack("i", self.value12)
            cvalue3 += struct.pack("i", 0)
        if self.type2 > 0 and self.value21 > 0 and self.value22 > 0:
            num = num + 1
            ctype += struct.pack("i", self.type2)
            cvalue1 += struct.pack("i", self.value21)
            cvalue2 += struct.pack("i", self.value22)
            cvalue3 += struct.pack("i", 0)
        if self.type3 > 0 and self.value31 > 0 and self.value32 > 0:
            num = num + 1
            ctype += struct.pack("i", self.type3)
            cvalue1 += struct.pack("i", self.value31)
            cvalue2 += struct.pack("i", self.value32)
            cvalue3 += struct.pack("i", 0)
        ctype = struct.pack("i", num) + ctype
        cvalue1 = struct.pack("i", num) + cvalue1
        cvalue2 = struct.pack("i", num) + cvalue2
        cvalue3 = struct.pack("i", num) + cvalue3

        return ctype, cvalue1, cvalue2, cvalue3

class LibaoItem():
    def __init__(self, code, name, num, max_num, gongxiang, types, value1s, value2s, value3s):
        self.code = code
        self.name = name
        self.num = num
        self.max_num = max_num
        self.gongxiang = gongxiang
        self.reward = ""

        l, types = struct.unpack('i%ds' % (len(types) - 4), types)
        type_arr = []
        for i in range(l):
            j, types = struct.unpack('i%ds' % (len(types) - 4), types)
            type_arr.append(j)
        l, value1s = struct.unpack('i%ds' % (len(value1s) - 4), value1s)
        value1_arr = []
        for i in range(l):
            j, value1s = struct.unpack('i%ds' % (len(value1s) - 4), value1s)
            value1_arr.append(j)
        l, value2s = struct.unpack('i%ds' % (len(value2s) - 4), value2s)
        value2_arr = []
        for i in range(l):
            j, value2s = struct.unpack('i%ds' % (len(value2s) - 4), value2s)
            value2_arr.append(j)
        l, value3s = struct.unpack('i%ds' % (len(value3s) - 4), value3s)
        value3_arr = []
        for i in range(l):
            j, value3s = struct.unpack('i%ds' % (len(value3s) - 4), value3s)
            value3_arr.append(j)
        for i in range(len(type_arr)):
            self.reward = self.reward + str(type_arr[i]) + " " + str(value1_arr[i]) + " " + str(value2_arr[i]) + " " + str(value3_arr[i]) + " "

class LibaoItems():
    def __init__(self, index):
        self.index = index
        self.total = 1
        self.libaos = []
        num = 10
        db = None
        try:
            db = pymysql.connect(user='root', passwd='root', db='vrlibao', host='127.0.0.1', charset='utf8')
            db.autocommit(1)
            cur = db.cursor()
            sql = "select count(*) from libao_type"
            cur.execute(sql)
            res = cur.fetchall()
            if len(res) == 1:
                self.total = (res[0][0] + num - 1) / num
                if self.total == 0:
                    self.total = 1

            index = (index - 1) * num
            sql = "select * from libao_type limit %s, %s"
            param = (index, num,)
            cur.execute(sql, param)
            res = cur.fetchall()
            for i in range(len(res)):
                code = res[i][0]
                lnum = 0
                sql = "select count(*) from libao where type = %s and used = 0"
                param = (code,)
                cur.execute(sql, param)
                res1 = cur.fetchall()
                if len(res1) == 1:
                    lnum = res1[0][0]
                litem = LibaoItem(res[i][0], res[i][1], lnum, res[i][2], res[i][3], res[i][4], res[i][5], res[i][6], res[i][7])
                self.libaos.append(litem)
        finally:
            if db:
                db.close()

class ClibaoForm(forms.Form):
    libao_type = forms.CharField(
        required=True,
        label='礼包类型',
        min_length=4,
        max_length=4,
        error_messages={'required':'必选项'}
    )
    libao_name = forms.CharField(
        required=True,
        label='礼包描述',
        max_length=256,
        error_messages={'required':'必选项'}
    )
    libao_num = forms.IntegerField(
        required=True,
        label='礼包数量',
        min_value = 1,
        max_value = 50000,
        error_messages={'required':'必选项'}
    )
    libao_gx = forms.ChoiceField(
        required=True,
        label='是否是共享礼包',
        choices=(
            ("0", "否"),
            ("1", "是"),
        ),
        error_messages={'required':'必选项'},
        )

    def __init__(self, *args, **kwargs):
        self.items = None
        self.suc = False
        self.type = "";
        super(ClibaoForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError('无效字段')
        else:
            ctype, cvalue1, cvalue2, cvalue3 = self.items.get_strings()
            self.cleaned_data = super(ClibaoForm, self).clean()
            if self.cleaned_data['libao_gx'] == '1':
                self.cleaned_data['libao_num'] = 1
            db = None
            error = ''
            try:
                db = pymysql.connect(user='root', passwd='root', db='vrlibao', host='127.0.0.1', charset='utf8')
                db.autocommit(1)
                cur = db.cursor()
                sql = "select code from libao_type where code = %s"
                param = (self.cleaned_data['libao_type'],)
                cur.execute(sql, param)
                res = cur.fetchall()
                if len(res) > 0:
                    error = '存在该类型的礼包'
                else:
                    sql = "insert into libao_type (code, name, num, gongxiang, type, value1, value2, value3, dt) values (%s, %s, %s, %s, %s, %s, %s, %s, now())"
                    param = (self.cleaned_data['libao_type'], self.cleaned_data['libao_name'], self.cleaned_data['libao_num'], self.cleaned_data['libao_gx'], ctype, cvalue1, cvalue2, cvalue3,)
                    cur.execute(sql, param)

                    zm = "23456789ABCDEFGHGKLMNPQRSTUVWXYZ"
                    codes = []
                    t = 0
                    while t < self.cleaned_data['libao_num']:
                        s = self.cleaned_data['libao_type']
                        for i in range(11):
                            a = random.randint(0, len(zm) - 1)
                            s = s + zm[a]
                        flag = False
                        for i in range(len(codes)):
                            if codes[i] == s:
                                flag = True
                                break
                        if flag:
                            continue
                        codes.append(s)
                        t = t + 1

                    sql = "insert into libao (code, type, used) values (%s, %s, 0)"
                    params = []
                    for i in range(len(codes)):
                        param = (codes[i], self.cleaned_data['libao_type'],)
                        params.append(param)
                    cur.executemany(sql, params)

                    s = settings.STATIC_ROOT + "/libao/%s.txt" % self.cleaned_data['libao_type']
                    f = open(s, "w")
                    for i in range(len(codes)):
                        f.write(codes[i]);
                        f.write("\n");
                    f.close()

                    self.type = self.cleaned_data['libao_type'];
                    self.suc = True
            except:
                raise forms.ValidationError('内部错误')
            finally:
                if db:
                    db.close()
            if error != '':
                raise forms.ValidationError(error)
        return self.cleaned_data

class DlibaoForm(forms.Form):
    libao_type = forms.CharField(
        required=True,
        label='礼包类型',
        min_length=4,
        max_length=4,
        error_messages={'required':'必选项'}
    )

    def __init__(self, *args, **kwargs):
        self.suc = False
        super(DlibaoForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError('无效字段')
        else:
            self.cleaned_data = super(DlibaoForm, self).clean()
            db = None
            error = ''
            try:
                db = pymysql.connect(user='root', passwd='root', db='vrlibao', host='127.0.0.1', charset='utf8')
                db.autocommit(1) 
                cur = db.cursor()
                sql = "delete from libao_type where code = %s"
                param = (self.cleaned_data['libao_type'],)
                cur.execute(sql, param)
                
                sql = "delete from libao where type = %s"
                param = (self.cleaned_data['libao_type'],)
                cur.execute(sql, param)

                self.suc = True
            except:
                raise forms.ValidationError('内部错误')
            finally:
                if db:
                    db.close()
            if error != '':
                raise forms.ValidationError(error)
        return self.cleaned_data
