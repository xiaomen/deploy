#!/opt/local/bin/python2.7
#coding:utf-8

import web
import logging
from gevsubprocess import GPopen as Popen, PIPE, STDOUT

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
        data = web.data()
        #cmd = ['sudo', '-u', 'sheep', '/var/sheep-farm/farm/server/bin/farm-syncdb', data]
        cmd = ['/var/sheep-farm/farm/server/bin/farm-syncdb', data]
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, stdin=open('/dev/null'))
        for line in p.stdout:
            logger.debug(line)
        ret = p.communicate()
        if ret[1]:
            yield ret[1]
        yield 'Syncdb succeeded.'

app_syncdb = web.application(urls, locals())
