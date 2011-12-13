#!/opt/local/bin/python2.7
#coding:utf-8

import web
import json
import time
import logging
from gevsubprocess import GPopen as Popen, PIPE, STDOUT

from alloc import get_app_uid, save_app_option, load_app_option

logger = logging.getLogger(__name__)

urls = (
    '/', 'syncdb',
)

class syncdb(object):
    def GET(self):
        return """\
POST http://deploy.xiaom.co/syncdb/
"""

    def POST(self):
        try:
            data = json.loads(web.data())
            appname = data['application']
            verbose = data['verbose']

            #get app config if not exist will create it
            get_app_uid(appname)
            is_exist = load_app_option(appname, 'mysql')

            if data.get('passwd'):
                del data['passwd']

            if is_exist:
                data['passwd'] = is_exist

            data = json.dumps(data)
            if verbose:
                loglevel = logging.DEBUG
            else:
                loglevel = logging.INFO

            cmd = ['sudo', '-u', 'sheep', '/usr/local/bin/farm-syncdb', data]
            p = Popen(cmd, stdout=PIPE, stderr=STDOUT, stdin=open('/dev/null'))
            logs = []
            for line in p.stdout:
                try:
                    levelno, line = line.split(':', 1)
                    levelno = int(levelno)
                except ValueError:
                    levelno = logging.DEBUG
                logs.append((time.time(), line))
                if levelno >= loglevel:
                    yield "%d:%s" % (levelno, line)

            if p.wait() == 0:
                yield "%d:Syncdb succeeded.\n" % (logging.INFO)
            else:
                yield "%d:Syncdb failed.  Logs followed.\n\n\n" % (logging.ERROR)
                for timestamp, line in logs:
                    yield "%d:%s %s" % (logging.ERROR,
                                        time.strftime("%H:%M:%S",
                                                      time.localtime(timestamp)),
                                        line)
        except:
            logger.exception('error occured.')
            yield 'Syncdb failed'

app_syncdb = web.application(urls, locals())
