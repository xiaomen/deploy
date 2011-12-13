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
            cmd = ['sudo', '-u', 'sheep', '/usr/local/bin/farm-statics', appname, json.dumps(configs)]
            if verbose:
                cmd += ['--verbose']
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=open('/dev/null'))

            for line in p.stdout:
                line = line.strip()
                logger.debug(line)
                yield line

            ret = p.communicate()
            print ret
        except:
            logger.exception('error occured.')
            yield 'Mirror failed'

app_statics = web.application(urls, locals())
