#coding:utf-8

import socket
import logging
import re
import web
import time

from gevsubprocess import GPopen as Popen, PIPE, STDOUT

from syncdb import app_syncdb
from statics import app_statics
from alloc import get_app_uid, load_app_option

web.config.debug = True

urls = (
    '/', 'deploy',
    '/syncdb', app_syncdb,
    '/statics', app_statics,
)

domain_re = r'http://(.*).xiaom.*'
RED = '\x1b[01;31m'
GREEN = '\x1b[01;32m'
NORMAL = '\x1b[0m'

def render_ok(msg):
    return GREEN + msg + NORMAL

def render_err(msg):
    return RED + msg + NORMAL


class deploy:
    def GET(self):
        return """\
POST http://deploy.xiaom.co/
"""

    def POST(self):
        # disable nginx buffering
        web.header('X-Accel-Buffering', 'no')

        i = web.input(fast=False)

        #get app config if not exist will create it
        app_uid = get_app_uid(i.app_name)
        servers = get_servers(i.app_name)

        yield "%d:%s" % (logging.INFO, render_ok(','.join(servers)))
        print web.ctx
        servers.remove(get_this(web.ctx['homedomain']))

        yield "%d:%s is serving you\n" % (logging.DEBUG, socket.gethostname())
        cmd = ['sudo', '-u', 'sheep', '/usr/local/bin/farm-deploy', i.app_name,
               i.app_url, str(app_uid), ]

        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, stdin=open('/dev/null'))
        logs = []
        for line in p.stdout:
            try:
                levelno, line = line.split(':', 1)
                levelno = int(levelno)
            except ValueError:
                levelno = logging.DEBUG
            logs.append((time.time(), line))
            yield "%d:%s" % (levelno, line)

        if p.wait() == 0:
            yield "%d:Deploy succeeded.\n" % (logging.INFO)
        else:
            yield "%d:Deploy failed.  Logs followed.\n\n\n" % (logging.ERROR)
            for timestamp, line in logs:
                yield "%d:%s %s" % (logging.ERROR,
                                    time.strftime("%H:%M:%S",
                                                  time.localtime(timestamp)),
                                    line)

def get_this(domain):
    print domain_re
    print domain
    m = re.match(domain_re, domain).groups()
    return m[0]

def get_servers(appname):
    ret = load_app_option(appname, 'deploy_servers')
    if ret:
        ret = ret.split(',')
    return []

app = web.application(urls, globals())
wsgi_app = app.wsgifunc()
