#!/usr/bin/env python  
#coding=utf-8

import os

def replace(fin, s):
    f = open(fin, 'r', encoding="utf-8", errors='ignore')
    a = f.read()
    f.close()

    index = a.find(s + '?')
    if index == -1:
        return
    index1 = a.find('"', index)
    if index1 == -1:
        return
    index = index + len(s) + 1
    ss = a[index:index1]
    sss = str(int(ss) + 1)

    a = a.replace(s + '?' + ss, s + '?' + sss)

    f = open(fin, 'w', encoding="utf-8")
    f.write(a)
    f.close()

def main():
    replace('static/js/mail.js', '.txt')
    replace('static/js/libao.js', '.txt')

    files = os.listdir ('templates')
    for f in files:
        if os.path.splitext (f)[1] == '.html':
            print(f)
            replace('templates/' + f, 'mail.js')
            replace('templates/' + f, 'libao.js')
    
if __name__ == '__main__':
    main()
