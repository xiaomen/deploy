#!/opt/local/bin/python2.7
#coding:utf-8

import MySQLdb

def generate_app_uid(appname):
    conn = MySQLdb.connect()
    cur = conn.cursor()
    sql = r'''INSERT INTO `apps` (`app_name`) VALUES (%s);'''
    cur.execute(sql, (appname,))
    conn.commit()
    cur.close()
    conn.close()
    return get_app_uid(appname)

def get_app_uid(appname):
    conn = MySQLdb.connect()
    cur = conn.cursor()
    sql = r'''SELECT `app_uid` FROM `apps` WHERE `app_name` = %s;'''
    cur.execute(sql, (appname,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    if len(result) > 0:
        return result[0][0]
    return generate_app_uid(appname)

def save(appname, option_name, value):
    conn = MySQLdb.connect()
    cur = conn.cursor()
    sql = r'''UPDATE `apps` SET `%s`='%s' WHERE `app_name` = '%s';'''
    cur.execute(sql % (option_name, value, appname,))
    conn.commit()
    cur.close()
    conn.close()
    return True

def load(appname, option_name):
    conn = MySQLdb.connect()
    cur = conn.cursor()
    sql = r'''SELECT %s FROM `apps` WHERE `app_name` = '%s';'''
    cur.execute(sql % (option_name, appname,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    if len(result) > 0 and result[0][0]:
        return result[0][0]
    return None
