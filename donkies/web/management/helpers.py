import os
import psycopg2
from django.conf import settings


def get_local_pg_root_password():
    passwd = os.getenv('LOCAL_PG_PASSWD', None)
    if passwd is None:
        raise Exception('Local pg password is not set.')
    return passwd.strip()


def get_remote_pg_root_password():
    passwd = os.getenv('DONKIES_PG_PASSWD', None)
    if passwd is None:
        raise Exception('Inet pg password is not set.')
    return passwd.strip()


def get_local_root_connection():
    cs = "host='127.0.0.1' user='postgres' password='{}'".format(
        get_local_pg_root_password())

    con = psycopg2.connect(cs)
    con.autocommit = True
    cur = con.cursor()
    return con, cur


def get_remote_root_connection():
    cs = "host='{}' user='postgres' password='{}'".format(
        settings.SERVER_IP, get_remote_pg_root_password())

    con = psycopg2.connect(cs)
    con.autocommit = True
    cur = con.cursor()
    return con, cur


def get_local_db_connection():
    cs = "host='127.0.0.1' dbname='{}' user='{}' password='{}'".format(
        settings.DB_NAME,
        settings.DB_USER,
        settings.DB_PASSWORD,
    )
    con = psycopg2.connect(cs)
    con.autocommit = True
    cur = con.cursor()
    return con, cur


def get_remote_db_connection():
    cs = "host='{}' dbname='{}' user='{}' password='{}'".format(
        settings.SERVER_IP,
        settings.DB_NAME,
        settings.DB_USER,
        settings.DB_PASSWORD,
    )
    con = psycopg2.connect(cs)
    con.autocommit = True
    cur = con.cursor()
    return con, cur
