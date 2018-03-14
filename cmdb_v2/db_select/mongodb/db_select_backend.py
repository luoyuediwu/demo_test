#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""
import pymongo
import pymongo.collection
from pymongo import ReplaceOne, UpdateOne, ReturnDocument, ASCENDING, DESCENDING
from common.uri_utils import *
from oslo_log import log
from cmdb_v2 import CMDB_CONF
from cmdb_v2.db_select.interface.dbselect_backend_internal import DatabaseBackendInternal
from common.restful.restful_utils import RestfulUtilsMixin
from cmdb_v2.constant_define import *
from common.constant_define import QueryOperation
from cmdb_v2.constant_define import MongoParam

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

__name__ = globals().get('__name__')
__file__ = os.path.join(os.environ['INSTALL_PATH'], __name__.replace('.', '/') + '.py')
LOG = log.getLogger(__name__)

# mongodb 主键名称
_id = '_id'

# mongodb 常用操作
_inc = '$inc'
_dec = '$dec'
_set = '$set'
_or = '$or'
_and = '$and'
_options = '$options'

# 常用 mongo 操作符
op_in = '$in'
op_notin = '$nin'
op_regex = '$regex'
op_lt = '$lt'
op_lte = '$lte'
op_gt = '$gt'
op_gte = '$gte'
op_eq = '$eq'
op_neq = '$ne'
op_exists = '$exists'
op_null = 'null'
op_elemmatch = '$elemMatch'

# 额外的属性（与现有 where 条件进行 $and 操作）
extra_condition = 'extra_condition'


class MongodbConnection(object):
    """
    连接数据库
    """
    __mongo_conn_db = None

    def init(self):
        if self.__mongo_conn_db is None:
            cmdb_ip = CMDB_CONF.mongodb_ip
            cmdb_port = CMDB_CONF.mongodb_port
            cmdb_db = CMDB_CONF.mongodb_db

            try:
                connection = pymongo.MongoClient(cmdb_ip,cmdb_port)
                self.__mongo_conn_db = connection[cmdb_db]

            except Exception as e:
                LOG.error("Can't connect to mongodb server %s")
                raise e
        return self.__mongo_conn_db


class CMDBMongoBackend(DatabaseBackendInternal, RestfulUtilsMixin, CMDBDefineMixin):
    OP = QueryOperation
    OP_MAP = {OP.in_: op_in,
              OP.notin: op_notin,
              OP.like: op_regex,
              OP.lt: op_lt,
              OP.lte: op_lte,
              OP.gt: op_gt,
              OP.gte: op_gte,
              OP.eq: op_eq,
              OP.neq: op_neq,
              OP.regex: op_regex,
              OP.exists: op_exists,
              OP.notexists: op_exists,
              OP.isnull: op_null,
              OP.notnull: op_null,
              OP.elemmatch: op_elemmatch}

    def __init__(self, params=None):
        super(CMDBMongoBackend, self).__init__(params)
        self.db = MongodbConnection().init()
        resources = self.db.resources
        relations = self.db.relations
        versions = self.db.versions
        self.resources = resources
        self.relations = relations
        self.versions = versions

    def name(self):
        return 'mongo'

    def global_init(self):
        pass

    def new_version_for(self, category, count=1):
        count = int(count)
        if count < 1 or count > 1024:
            raise ValueError('New version count must in range [1, 1024]')
        result = self.versions.find_one_and_update({_id: category}, {_inc: {self.A.version: count}}, upsert=True, return_document=ReturnDocument.AFTER)
        end_index = result[self.A.version]
        if count == 1:
            return end_index
        return range(end_index - count + 1, end_index + 1)

    def batch_add_ci(self,items):
        version = self.new_version_for(self.V.CI_VERSION)
        print version
        self.__save_resource(items, version, merge_exists=False)
        self.__save_relations(items, version)
        return self.rest_success({self.A.version: version})

    def __save_resource(self, params, version, merge_exists):
        if not params[self.A.resources]:
            return
        requests = []
        for res in params[self.A.resources]:
            res_id = res[_id] = res[self.A.resource_id]
            print res
            res[self.A.attributes][self.A.resource_id] = res_id
            if merge_exists:
                tmp_res = {self.__attr(attr):value for attr, value in res[self.A.attributes].items()}
                tmp_res.update({self.A.resource_id: res_id,
                 self.A.version: version})
                if res.get(self.A.deleted) is not None:
                    tmp_res[self.A.deleted] = res.get(self.A.deleted)
                res = tmp_res
            requests.append(UpdateOne({_id: res_id}, {_set: res}, upsert=True) if merge_exists else ReplaceOne({_id: res_id}, res, upsert=True))

        self.resources.bulk_write(requests, ordered=False)

    def __save_relations(self, params, version):
        if not params[self.A.relations]:
            return
        requests = []
        for rel in params[self.A.relations]:
            rel[_id] = '%s->%s' % (rel[self.A.resource_id1], rel[self.A.resource_id2])
            rel[self.A.relation_code] = int(rel[self.A.relation_code])
            requests.append(ReplaceOne({_id: rel[_id]}, rel, upsert=True))

        self.relations.bulk_write(requests, ordered=False)

    def __attr(self, f):
        return '%s.%s' % (self.A.attributes, f)

    def query_item(self,params):
        output_list = True if self.A.output_format in params and params[self.A.output_format] == self.A.list_ else False
        skip, limit = self.__build_limit(params)
        filters = self.__build_where(params)
        total = self.resources.count(filter=filters)
        cursor = self.resources.find(filter=filters, projection=self.__build_output(params), sort=self.__build_order(params), skip=skip, limit=limit)
        result = {self.A.resources: [],
         self.A.resource_count: 0,
         self.A.total_count: total}
        for ci in cursor:
            ci[self.A.resource_id] = ci[_id]
            ci[self.A.attributes][self.A.resource_id] = ci[_id]
            del ci[_id]
            result[self.A.resources].append(ci)

        result[self.A.resource_count] = len(result[self.A.resources])
        # self.translate_location(result[self.A.resources], params)
        # self.parent_alarm_masking(result, params)
        # self.translate_path(result[self.A.resources], params)
        if output_list:
            result[self.A.resources] = [ ci[self.A.attributes] for ci in result[self.A.resources] ]
        # self.__normalize_resource_name(result[self.A.resources], encode=False)
        if not output_list:
            return self.rest_success(result)
        return result[self.A.resources]

    def query_item2(self, params):
        output_list = True if self.A.output_format in params and params[self.A.output_format] == self.A.list_ else False
        skip, limit = self.__build_limit(params)
        #filters = self.__build_where(params)
        filters = params['extra_condition']['_id']['$in']
        total = self.resources.count(filter=filters)
        cursor = self.resources.find(filter=filters, projection=self.__build_output(params),
                                     sort=self.__build_order(params), skip=skip, limit=limit)
        result = {self.A.resources: [],
                  self.A.resource_count: 0,
                  self.A.total_count: total}
        for ci in cursor:
            ci[self.A.resource_id] = ci[_id]
            ci[self.A.attributes][self.A.resource_id] = ci[_id]
            del ci[_id]
            result[self.A.resources].append(ci)

        result[self.A.resource_count] = len(result[self.A.resources])
        #self.translate_location(result[self.A.resources], params)
        #self.parent_alarm_masking(result, params)
        #self.translate_path(result[self.A.resources], params)
        if output_list:
            result[self.A.resources] = [ci[self.A.attributes] for ci in result[self.A.resources]]
        #self.__normalize_resource_name(result[self.A.resources], encode=False)
        if not output_list:
            return self.rest_success(result)
        return result[self.A.resources]

    def __build_limit(self, params):
        if not params.get(self.A.page):
            return (0, 0)
        return (int(params[self.A.page][self.A.size]) * (int(params[self.A.page][self.A.number]) - 1), int(params[self.A.page][self.A.size]))

    def __build_where(self, params):
        """
              构建CMDB查询条件参数
        备注：
            除了处理标准的 where 参数以外，还会处理额外的 extra_condition 和 deleted 条件，相关条件的关系为
            deleted and extra_condition and where
        :param params: REST 标准参数格式，其中 where 参数会转化为查询条件
        :return: 适用于 MongoDB 的查询条件
        """
        if not params.get(self.A.where) and not params.get(extra_condition):
            return
        result = None
        if params.get(self.A.where):
            cond = []
            for where in params[self.A.where]:
                and_cond = []
                for term in where[self.A.terms]:
                    and_cond.append(self.__build_op(term[self.A.field], term[self.A.operator], term[self.A.value]))

                if and_cond:
                    cond.append(and_cond[0] if len(and_cond) == 1 else {_and: and_cond})

            result = cond[0] if len(cond) == 1 else {_or: cond}
        return self.__extras_condition(params, result)


    def __extras_condition(self, params, conditions, used_in = DictParam.resources):
        """

        根据额外的因素添加查询条件，额外因素包括：
        deleted: 已删除标识
        extra_condition:     额外条件
        approved_resources: 有权限的设备列表，列表之外的要排除
        :param params:     原始查询参数
        :param conditions: 根据原始参数已组合好的条件
        :param used_in:    查询哪里的数据？默认是资源(resources)，可选值包括关系(relations)
        :return:
        """
        result = [conditions]

    def __build_op(self, field, op, value):
        field = self.__convert_filed(field)
        if op in self.OP_MAP:
            if op in (self.OP.exists, self.OP.notexists):
                value = op == self.OP.exists
            elif op in (self.OP.isnull, self.OP.notnull):
                op = self.OP.eq if op == self.OP.isnull else self.OP.neq
                value = None
            if op == self.OP.like:
                result = {field: {self.OP_MAP[self.OP.like]: self.__regex_addslashes(value),
                         _options: 'is'}}
            elif op == self.OP.in_ and not isinstance(value, (list, tuple)):
                result = {field: {self.OP_MAP[self.OP.eq]: value}}
            elif op == self.OP.elemmatch:
                result = {field: {self.OP_MAP[self.OP.elemmatch]: {self.OP_MAP[self.OP.eq]: value}}}
            else:
                result = {field: {self.OP_MAP[op]: value}}
            if field == 'attributes.alarm_masking':
                result[field].update({'$exists': 'true'})
            return result
        raise KeyError("Invalid operator '%s'", op)


    def __convert_filed(self, field):
        top_fields = (self.A.version,
         self.A.deleted,
         self.A.resource_id,
         self.A.resource_id1,
         self.A.resource_id2,
         self.A.relation_code)
        if field not in top_fields:
            field = self.__attr(field)
        elif field == self.A.resource_id:
            field = _id
        return field

    @staticmethod
    def __regex_addslashes(value):
        for c in '\\.*^$&#<>/()[]{}':
            value = value.replace(c, '\\%s' % c)

        return '^%s$' % value.replace('?', '.').replace('%', '.*')


    def __build_output(self, params):
        if not params.get(self.A.output):
            return None
        result = {self.A.version: 1,
         self.A.deleted: 1,
         _id: 1}
        result.update({self.__attr(f):1 for f in params[self.A.output]})
        return result

    def __build_order(self, params):
        if not params.get(self.A.sorts):
            return None
        return [ (self.__convert_filed(o[self.A.field]), ASCENDING if o[self.A.type_] == 'ASC' else DESCENDING) for o in params[self.A.sorts] ]

    def delete_relation(self, params):
        condition = [self.__build_op(self.A.deleted, self.OP.eq, 0), self.__build_op(self.A.resource_id1, self.OP.eq, params[self.A.id1])]
        if params.get(self.A.id2):
            condition.append(self.__build_op(self.A.resource_id2, self.OP.in_, params[self.A.id2]))
        else:
            condition.append(self.__build_op(self.A.relation_code, self.OP.eq, int(params[self.A.relation_code])))
        version = self.new_version_for(self.V.CI_VERSION)
        self.relations.update_many({_and: condition}, {_set: {self.A.deleted: 1,
                self.A.version: version}})
        return self.rest_success({self.A.version: version})

    def __fetch_relation(self, condition, params):
        # projection = {_id: 0,
        #  self.A.resource_id1: 1,
        #  self.A.resource_id2: 1,
        #  self.A.relation_code: 1}
        # show_all = params.get(self.A.show_all)
        # if show_all is None or show_all not in ('0', 'false', 'no', 0):
        #     projection.update({_id: 1,
        #      self.A.deleted: 1,
        #      self.A.version: 1})
        #cursor = self.relations.find(filter=self.__extras_condition(params, condition, used_in=self.A.relations), projection=projection, sort=[(self.A.resource_id1, ASCENDING), (self.A.resource_id2, ASCENDING)])
        cursor = self.relations.find(condition)
        return [ rel for rel in cursor ]

    # {
    #     'attribute_name': 'ci_type',
    #     'output_format': 'list',
    #     'relation_code': 5,
    #     'attribute_value': '2%2C3%2C5',
    #     'extra_condition': {
    #         '_id': {
    #             '$in': [
    #                 u'0_18',
    #                 u'0_19'
    #             ]
    #         }
    #     }
    # }

    def internal_query_item(self, params):
        output_list = True if self.A.output_format in params and params[self.A.output_format] == self.A.list_ else False
        #skip, limit = self.__build_limit(params)
        #filters = self.__build_where(params)
        filters = params['extra_condition']['_id']['$in']
        total = len(filters)
        result = {self.A.resources: [],
                  self.A.resource_count: 0,
                  self.A.total_count: total}
        for filter in filters:
            import unicodedata
            str  = unicodedata.normalize('NFKD',filter).encode('ascii','ignore')
            cur = self.resources.find({"_id":str})
            for ci in cur:
                ci[self.A.resource_id] = ci[_id]
                ci[self.A.attributes][self.A.resource_id] = ci[_id]
                del ci[_id]
                result[self.A.resources].append(ci)
        result[self.A.resource_count] = len(result[self.A.resources])
        if output_list:
            result[self.A.resources] = [ ci[self.A.attributes] for ci in result[self.A.resources] ]
        if not output_list:
            return self.rest_success(result)
        return result[self.A.resources]

    def query_relation_item(self, params):
        first_id = self.A.resource_id2 if params.get(self.A.reverse) else self.A.resource_id1
        another_id = self.A.resource_id1 if params.get(self.A.reverse) else self.A.resource_id2
        relations = self.__fetch_relation({first_id: params[self.A.resource_id],
         self.A.relation_code: int(params[self.A.relation_code])}, params)
        relation_ci = [ rel[another_id] for rel in relations ]
        params[extra_condition] = self.__build_op(self.A.resource_id, self.OP.in_, relation_ci)
        del params[self.A.resource_id]
        return self.internal_query_item(params)


if __name__=="__main__":
    from cmdb_v2.db_select import BackendFactory
    operate = CMDBMongoBackend()
    backend = BackendFactory.new()
    # ids = backend.new_version_for("case",1)
    # items = {
    #         "resources": [{
    #             "resource_id": "0_33006",
    #             "attributes": {
    #                 "resource_id": "0_33006",
    #                 "sn": "",
    #                 "ci_type": "5",
    #                 "name": "luoyuediwu",
    #                 "space_type": "1",
    #                 "space_code": "1",
    #                 "position_types": [0],
    #                 "device_type": "",
    #                 "board_options": [],
    #                 "init_sub_space": [],
    #                 "status": "1",
    #                 "location": "project_root",
    #                 "path": "project_root",
    #                 "create_date": 1513148609293,
    #                 "creater_name": "admin",
    #                 "owner": {
    #
    #                 },
    #                 "description": "",
    #                 "parent_id": "project_root"
    #             }
    #         }],
    #         "relations": [{
    #             "resource_id1": "project_root",
    #             "resource_id2": "0_33006",
    #             "relation_code": 5
    #         }],
    #         "resource_count": 1,
    #         "relation_count": 1
    #     }
    # backend.batch_add_ci(items)
    # params = {"where":[{"terms":[{"field":"resource_id","operator":"eq","value":"project_root"}]}]}
    params = {"resource_id":"project_root","attribute_value":"2%2C3%2C5","relation_code":5,"output_format":"list","attribute_name":"ci_type"}
    print backend.query_relation_item(params)
