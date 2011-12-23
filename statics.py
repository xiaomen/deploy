#!/opt/local/bin/python2.7
#coding:utf-8

import web
import json
import time
import logging
from gevsubprocess import GPopen as Popen, PIPE, STDOUT

from alloc import get_app_uid, save_app_option, load_app_option

urls = (
    '/', 'statics',
)

class statics(object):
    def GET(self):
        return """\
POST http://deploy.xiaom.co/statics/
"""

    def POST(self):
        try:
            data = json.loads(web.data())
            appname = data['application']
            configs = data['configs']

            #get app config if not exist will create it
            get_app_uid(appname)
        except:
            yield 'Mirror error occured.'
            return

        cmd = ['sudo', '-u', 'sheep', '/usr/local/bin/farm-statics', appname, json.dumps(configs)]

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
            yield "%d:Mirror succeeded.\n" % (logging.INFO)
        else:
            yield "%d:Mirror failed.  Logs followed.\n\n\n" % (logging.ERROR)
            for timestamp, line in logs:
                yield "%d:%s %s" % (logging.ERROR,
                                    time.strftime("%H:%M:%S",
                                                  time.localtime(timestamp)),
                                    line)

app_statics = web.application(urls, locals())
