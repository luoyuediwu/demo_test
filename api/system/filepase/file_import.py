#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/14 10:26
# @Author  : luoyuediwu
# @Site    : 
# @File    : file_import.py
# @Software: PyCharm

import eventlet
from eventlet import event
eventlet.monkey_patch()
import uuid
import os
from flask_restful import Resource
from common.restful.restful_utils import RestfulUtilsMixin
from werkzeug.datastructures import FileStorage
from common.confs import COMMON_CONF
from file_operator import FilePaseToJson
from oslo_log import log

__version__ = '1.0.0.0'
FILE_PATH_ROOT = '/opt/%s/download/eventrules' % COMMON_CONF.product
__name__ = globals().get('__name__')
__file__ = os.path.join(os.environ['INSTALL_PATH'], __name__.replace('.', '/') + '.py')
LOG = log.getLogger(__name__)
class FileImport(Resource,RestfulUtilsMixin):
    def post(self):

        return self.rest_execute_action('post')

    def _post_naked(self):
        args = self.load_request_params(
            [self.Param('file_name', FileStorage, required=True, location='files', help_='Must specify file')])
        param_id = uuid.uuid4().get_hex()
        import_file = args.file_name.filename
        file_tokens = args.file_name.filename.split('.')
        file_tokens[-1] = file_tokens[-1].lower()
        ext = file_tokens[-1]
        if ext != '.xls':
            return self.rest_result(self.R.EC.INVALID_PARAM,
                                    extra_text="File extension '%s' not allowed, avaiable extensions are '%s'" % (
                                    ext, ',xls'))
        full_path = '%s/testcase%s.xls' % (FILE_PATH_ROOT, param_id)
        if not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))
        args.file_name.save(full_path)
        evt = event.Event
        args_new = {
                    'full_path': full_path,
                    'evt':evt
                    }
        eventlet.spawn_n(FilePaseToJson.make_pase, args_new)
        data = evt.wait()
        return self.rest_success(data)


