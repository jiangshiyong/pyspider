#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2014-11-05 10:42:24

import time
import mysql.connector


class MySQLMixin(object):
    maxlimit = 18446744073709551615

    @property
    def dbcur(self):
        try:
            if self.conn.unread_result:
                self.conn.get_rows()
            return self.conn.cursor()
        except (mysql.connector.OperationalError, mysql.connector.InterfaceError):
            self.conn.ping(reconnect=True)
            self.conn.database = self.database_name
            return self.conn.cursor()


class SplitTableMixin(object):
    UPDATE_PROJECTS_TIME = 10 * 60

    def _tablename(self, project):
        if self.__tablename__:
            return '%s_%s' % (self.__tablename__, project)
        else:
            return project

    @property
    def projects(self):
        if time.time() - getattr(self, '_last_update_projects', 0) \
                > self.UPDATE_PROJECTS_TIME:
            self._list_project()
        return self._projects

    @projects.setter
    def projects(self, value):
        self._projects = value

    def _list_project(self):
        self._last_update_projects = time.time()
        self.projects = set()
        # comment by shuaijiman
        # if self.__tablename__:
        #     prefix = '%s_' % self.__tablename__
        # else:
        #     prefix = ''
        # for project, in self._execute('show tables;'):
        #     if project.startswith(prefix):
        #         project = project[len(prefix):]
        #         self.projects.add(project)
        tablename = self.__tablename__
        for project, in self._execute('select project from %s group by project' % self.escape(tablename)):
            self.projects.add(project)

    def drop(self, project):
        if project not in self.projects:
            self._list_project()
        if project not in self.projects:
            return
        #EDIT by shuaijiman
        tablename = self.__tablename__
        sql_query = "DELETE FROM %s" % self.escape(tablename)
        sql_query = sql_query + " WHERE `project` = %s"
        self._execute(sql_query, (project,))
        self._list_project()
