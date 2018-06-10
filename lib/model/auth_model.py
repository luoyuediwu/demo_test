#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/29 14:03
# @Author  : luoyuediwu
# @Site    : 
# @File    : auth_model.py
# @Software: PyCharm

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey
ModelBase = declarative_base()
__all__ = ['BaseDepartment',
 'BaseUsers',
 'BaseRoles',
 'BaseOperation',
 'RoleResourcePerms',
 'BaseMenu']

class BaseUserDepartment(ModelBase):
    __tablename__ = 'itom_base_user_department'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('itom_base_users.id'), nullable=False)
    department_id = Column(Integer, ForeignKey('itom_base_department.id'), nullable=False)


class BaseUserRole(ModelBase):
    __tablename__ = 'itom_base_user_role'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('itom_base_users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('itom_base_roles.id'), nullable=False)


class BaseRoleOperaton(ModelBase):
    __tablename__ = 'itom_base_role_operation'
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('itom_base_roles.id'), nullable=False)
    operation_id = Column(Integer, ForeignKey('itom_base_operations.id'), nullable=False)


class RoleResourcePerms(ModelBase):
    __tablename__ = 'itom_role_resource_perms'
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('itom_base_roles.id'), nullable=False)
    resource_id = Column(String(64), nullable=False)
    resource_type = Column(Enum('ci', 'inventory'), nullable=False)
    perms = Column(Integer, nullable=False, default=1, doc='0:\xe6\x9c\xaa\xe9\x80\x89\xe5\x8f\x96,1:\xe9\x80\x89\xe5\x8f\x96')
    role = relationship('BaseRoles', back_populates='perms')


class BaseDepartment(ModelBase):
    __tablename__ = 'itom_base_department'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    remark = Column(String(1000))
    parent_id = Column(Integer)
    default_dep = Column(Integer, nullable=False, default=20)
    row_status = Column(Integer, nullable=False, default=10)
    version = Column(Integer, nullable=False, default=0)
    users = relationship('BaseUsers', secondary='itom_base_user_department', back_populates='departments')


class BaseUsers(ModelBase):
    """
        用户信息表
    """
    __tablename__ = 'itom_base_users'
    ROW_STATUS_USED = 10
    ROW_STATUS_DELETED = 20
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    account = Column(String(100), nullable=False)
    salt = Column(String(100))
    password = Column(String(255), nullable=False)
    encrypt = Column(String(255))
    position = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    fax = Column(String(100))
    mobile = Column(String(100))
    version = Column(Integer, nullable=False, default=0)
    user_type = Column(Integer, nullable=False, default=10)
    row_status = Column(Integer, nullable=False, default=10)
    status = Column(Integer, nullable=False, default='1')
    engineer_level = Column(Integer)
    remark = Column(String(200))
    default_user = Column(Integer, nullable=False, default=20)
    userno = Column(String(20))
    user_level = Column(Integer)
    user_status = Column(Integer)
    roles = relationship('BaseRoles', secondary='itom_base_user_role', back_populates='users')
    departments = relationship('BaseDepartment', secondary='itom_base_user_department', back_populates='users')
    menus = relationship('BaseMenu', order_by='BaseMenu.display_order', back_populates='owner')


class BaseRoles(ModelBase):
    __tablename__ = 'itom_base_roles'
    id = Column(Integer, primary_key=True, nullable=False)
    default_role = Column(Integer, nullable=False, default=20)
    name = Column(String(100), nullable=False)
    remark = Column(String(255), nullable=False, default='')
    row_status = Column(Integer, nullable=False, default=10)
    version = Column(Integer, nullable=False, default=0)
    modify_status = Column(Integer)
    super_role = Column(Integer)
    users = relationship('BaseUsers', secondary='itom_base_user_role', back_populates='roles')
    operations = relationship('BaseOperation', secondary='itom_base_role_operation', back_populates='roles')
    perms = relationship('RoleResourcePerms', order_by=RoleResourcePerms.id, back_populates='role')


class BaseOperation(ModelBase):
    __tablename__ = 'itom_base_operations'
    id = Column(Integer, primary_key=True)
    pid = Column(Integer)
    module = Column(String(100, convert_unicode=True))
    title = Column(String(200))
    resource = Column(String(200))
    remark = Column(String(200, convert_unicode=True))
    row_status = Column(Integer, nullable=False, default=10)
    version = Column(Integer, nullable=False, default=0)
    comment = Column(String(200, convert_unicode=True))
    stoppage = Column(Integer, nullable=False, default=10)
    roles = relationship('BaseRoles', secondary='itom_base_role_operation', back_populates='operations')
    menu = relationship('BaseMenu', uselist=False, back_populates='operation')


class BaseMenu(ModelBase):
    __tablename__ = 'itom_base_menu'
    id = Column(String(40), primary_key=True)
    parent_id = Column(String(40), ForeignKey('itom_base_menu.id'))
    used = Column(Integer, default=1, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    internal = Column(Integer, default=0, nullable=False)
    owner_id = Column(Integer, ForeignKey('itom_base_users.id'))
    license = Column(String(64))
    name = Column(String(32), nullable=False)
    title = Column(String(32), nullable=False)
    url = Column(String(1024), nullable=False)
    tag = Column(String(64))
    target = Column(Enum('appzone', '_blank', 'popup', 'top'), default='appzone', nullable=False)
    operation_id = Column(Integer, ForeignKey('itom_base_operations.id'))
    operation = relationship('BaseOperation', uselist=False, back_populates='menu')
    owner = relationship('BaseUsers', uselist=False, back_populates='menus')