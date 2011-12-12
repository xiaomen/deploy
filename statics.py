#!/opt/local/bin/python2.7
#coding:utf-8

import web
import json
import logging
from gevsubprocess import GPopen as Popen, PIPE, STDOUT

from alloc import get_app_uid, save_app_option, load_app_option

logger = logging.getLogger(__name__)

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
            verbose = data['verbose']

            #get app config if not exist will create it
            get_app_uid(appname)
            data = json.dumps(data)

            cmd = ['sudo', '-u', 'sheep', '/usr/local/bin/farm-statics', data, configs]
            p = Popen(cmd, stdout=PIPE, stderr=STDOUT, stdin=open('/dev/null'))
            logs = []
            for line in p.stdout:
                line = line.strip()
                logger.debug(line)
                if verbose:
                    logs.append(line)
            ret = p.communicate()
            if ret[1]:
                yield ret[1]
            else:
                for log in logs:
                    yield '%s\n' % log
                yield 'Mirror succeeded.'
        except:
            logger.exception('error occured.')
            yield 'Mirror failed'

app_statics = web.application(urls, locals())
