import socket
import logging
import web
import time

from gevsubprocess import GPopen as Popen, PIPE, STDOUT

from syncdb import app_syncdb
from alloc import get_app_uid

web.config.debug = True

urls = (
    '/', 'deploy',
    '/syncdb', app_syncdb,
)

class deploy:
    def GET(self):
        return """\
POST http://deploy.xiaom.co/

Parameters:
    app_name
    app_url
    verbose

"""

    def POST(self):
        # disable nginx buffering
        web.header('X-Accel-Buffering', 'no')

        i = web.input(verbose=False)

        #get app config if not exist will create it
        app_uid = get_app_uid(i.app_name)

        #cmd = ['sudo', '-u', 'sheep', '/var/sheep-farm/farm/server/bin/farm-deploy', i.app_name,
        #       i.app_url, str(app_uid)]
        cmd = ['/var/sheep-farm/farm/server/bin/farm-deploy', i.app_name,
               i.app_url, str(app_uid)]
        if i.verbose:
            cmd += ['--verbose']
            yield "%d:%s is serving you\n" % (logging.DEBUG,
                                              socket.gethostname())
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO

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
            yield "%d:Deploy succeeded.\n" % (logging.INFO)
        else:
            yield "%d:Deploy failed.  Logs followed.\n\n\n" % (logging.ERROR)
            for timestamp, line in logs:
                yield "%d:%s %s" % (logging.ERROR,
                                    time.strftime("%H:%M:%S",
                                                  time.localtime(timestamp)),
                                    line)

app = web.application(urls, globals())
wsgi_app = app.wsgifunc()
