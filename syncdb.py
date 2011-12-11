#!/opt/local/bin/python2.7
#coding:utf-8

import web
import json
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

            cmd = ['sudo', '-u', 'sheep', '/usr/local/bin/farm-syncdb', data]
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
                if not is_exist and line:
                    save_app_option(appname, 'mysql', line)
                logs = logs[:-1]
                for log in logs:
                    yield '%s\n' % log
                yield 'Syncdb succeeded.'
        except:
            logger.exception('error occured.')
            yield 'Syncdb failed'

app_syncdb = web.application(urls, locals())
