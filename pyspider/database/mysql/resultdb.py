#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2014-10-13 22:02:57

import re
import six
import time
import json
import mysql.connector

from pyspider.libs import utils
from pyspider.database.base.resultdb import ResultDB as BaseResultDB
from pyspider.database.basedb import BaseDB
from .mysqlbase import MySQLMixin, SplitTableMixin


class ResultDB(MySQLMixin, SplitTableMixin, BaseResultDB, BaseDB):
    __tablename__ = "resultdb"

    def __init__(self, host='localhost', port=3306, database='resultdb',
                 user='root', passwd=None):
        self.database_name = database
        self.conn = mysql.connector.connect(user=user, password=passwd,
                                            host=host, port=port, autocommit=True)
        if database not in [x[0] for x in self._execute('show databases')]:
            self._execute('CREATE DATABASE %s' % self.escape(database))
        self.conn.database = database
        self._list_project()

    def _create_project(self, project):
        assert re.match(r'^\w+$', project) is not None
        tablename = self.__tablename__
        if tablename in [x[0] for x in self._execute('show tables')]:
            return
        self._execute('''CREATE TABLE %s (
            `taskid` varchar(64),
            `project` varchar(64),
            `url` varchar(1024),
            `result` MEDIUMBLOB,
            `updatetime` double(16, 4),
            PRIMARY KEY `uniq_taskid` (`project`, `taskid`)
            ) ENGINE=InnoDB CHARSET=utf8''' % self.escape(tablename))

    def _parse(self, data):
        for key, value in list(six.iteritems(data)):
            if isinstance(value, (bytearray, six.binary_type)):
                data[key] = utils.text(value)
        if 'result' in data:
            data['result'] = json.loads(data['result'])
        return data

    def _stringify(self, data):
        if 'result' in data:
            data['result'] = json.dumps(data['result'])
        return data

    def save(self, project, taskid, url, result):
        tablename = self.__tablename__
        if project not in self.projects:
            self._create_project(project)
            self._list_project()
        obj = {
            'taskid': taskid,
            'project': project,
            'url': url,
            'result': result,
            'updatetime': time.time(),
        }
        return self._replace(tablename, **self._stringify(obj))

    def select(self, project, fields=None, offset=0, limit=None):
        if project not in self.projects:
            self._list_project()
        if project not in self.projects:
            return
        tablename = self.__tablename__
        where = "`project` = %s" % self.placeholder
        for task in self._select2dic(tablename, what=fields, order='updatetime DESC',
                                    where=where, where_values=(project, ),
                                     offset=offset, limit=limit):
            yield self._parse(task)

    def count(self, project):
        if project not in self.projects:
            self._list_project()
        if project not in self.projects:
            return 0
        tablename = self.__tablename__
        sql_query = "SELECT count(1) FROM %s " % self.escape(tablename)
        sql_query = sql_query + "WHERE `project` = %s"
        for count, in self._execute(sql_query, (project,)):
            return count

    def get(self, project, taskid, fields=None):
        if project not in self.projects:
            self._list_project()
        if project not in self.projects:
            return
        tablename = self.__tablename__
        where = "`taskid` = %s and `project` = %s" % (self.placeholder, self.placeholder)
        for task in self._select2dic(tablename, what=fields,
                                     where=where, where_values=(taskid, project, )):
            return self._parse(task)
