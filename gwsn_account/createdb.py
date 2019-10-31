#!/usr/bin/env python  
#coding=utf-8

import sys
import pymysql

def main():
    db = pymysql.connect(user='root', passwd='root', host='')
    db.autocommit(1)
    cur = db.cursor()
    for i in range(20):
        dbname = 'gwsnuser' + str(i)
        sql = 'drop database if exists ' + dbname
        cur.execute(sql)
        sql = 'create database ' + dbname
        cur.execute(sql)
        sql = "use " + dbname
        cur.execute(sql)
        sql = "drop table if exists user"
        cur.execute(sql)
        sql = "create table user (username text not null, password text, data text, primary key(username(8))) engine=InnoDB default charset=utf8"
        cur.execute(sql)
    db.close()

if __name__ == '__main__':
    main()
