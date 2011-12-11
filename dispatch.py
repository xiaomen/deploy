#coding:utf-8

import web
import json
import logging

from alloc import load_app_option

logger = logging.getLogger(__name__)

urls = (
    '/(.*)', 'dispatch',
)

class dispatch(object):
    def GET(self, appname = None):
        if not appname:
            return 'Hello Visitor.'
        if appname:
            ret = load_app_option(appname, 'deploy_servers')
            if ret:
                return json.dumps(ret.split(','))
        return json.dumps(['deploy'])

app_dispatch = web.application(urls, locals())
