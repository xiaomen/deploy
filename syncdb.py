#!/opt/local/bin/python2.7
#coding:utf-8

import web
import json
import logging
from gevsubprocess import GPopen as Popen, PIPE, STDOUT

from alloc import get_app_uid, save, load

logger = logging.getLogger(__name__)

urls = (
    '/', 'syncdb',
)

class syncdb(object):
    def GET(self):
        return """\
POST http://deploy.xiaom.co/syncdb/

Parameters:
{
    table1: [addition1, addition2, ..., {column1: define, ...}],
    table2: [addition1, addition2, ..., {column1: define, ...}],
    ...
}
"""

    def POST(self):
        data = json.loads(web.data())
        appname = data['application']

        #get app config if not exist will create it
        get_app_uid(appname)
        is_exist = load(appname, 'mysql')

        if is_exist:
            data['passwd'] = is_exist

        data = json.dumps(data)

        cmd = ['sudo', '-u', 'sheep', '/usr/local/bin/farm-syncdb', data]
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, stdin=open('/dev/null'))
        for line in p.stdout:
            logger.debug(line)
        ret = p.communicate()
        if ret[1]:
            yield ret[1]
        else:
            if not is_exist and line:
                save(appname, 'mysql', line)
            yield 'Syncdb succeeded.'

app_syncdb = web.application(urls, locals())
