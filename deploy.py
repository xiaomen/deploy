#coding:utf-8

import socket
import logging
import web
import time
from urllib import FancyURLopener, urlencode
from gevsubprocess import GPopen as Popen, PIPE, STDOUT

from syncdb import app_syncdb
from statics import app_statics
from alloc import get_app_uid, load_app_option

web.config.debug = True

urls = (
    '/', 'deploy',
    '/syncdb', app_syncdb,
    '/statics', app_statics,
    '/dispatch', 'dispatch',
)

RED = '\x1b[01;31m'
GREEN = '\x1b[01;32m'
NORMAL = '\x1b[0m'
SUFFIX = 'http://%s.xiaom.co/dispatch'

def render_ok(msg):
    return GREEN + msg + NORMAL + '\n'

def render_err(msg):
    return RED + msg + NORMAL + '\n'

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
        servers = get_servers(i.app_name)
        servers = ['deploy']
        yield "%d:%s" % (logging.INFO, render_ok("Application allowed to deploy those servers"))
        yield "%d:%s" % (logging.INFO, render_ok(','.join(servers)))

        result = {}
        data = {'app_name': i.app_name, 'app_url': i.app_url}
        for server in servers:
            url = SUFFIX % server
            opener = FancyURLopener()
            f = opener.open(url, urlencode(data))
            line = ''  # to avoid NameError for line if f has no output at all.
            for line in iter(f.readline, ''):
                yield line
            if not any(word in line for word in ['succeeded', 'failed']):
                result[server] = 'Failed'
            else:
                result[server] = 'Succeeded'

        yield "%d:==========RESULT==========\n" % logging.INFO
        for k, v in result.iteritems():
            if v == 'Failed':
                yield "%d:%s" % (logging.INFO, render_err("%s %s" % (k, v)))
            else:
                yield "%d:%s" % (logging.INFO, render_ok("%s %s" % (k, v)))
        yield "%d:Deploy succeeded.\n" % (logging.INFO)

class dispatch:
    def POST(self):
        web.header('X-Accel-Buffering', 'no')
        i = web.input()
        app_uid = get_app_uid(i.app_name)

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

def get_servers(appname):
    ret = load_app_option(appname, 'deploy_servers')
    if ret:
        ret = ret.split(',')
        return ret
    return []

app = web.application(urls, globals())
wsgi_app = app.wsgifunc()
