#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
核心数据模型模块
"""

from enum import Enum
from typing import List, Dict, Any, Optional


class NodeType(Enum):
    """节点类型枚举"""
    INPUT = "input"
    OUTPUT = "output"
    PARAMETER = "parameter"


class Node:
    """连接节点类"""
    def __init__(self, node_id: str, node_type: NodeType, name: str, value_type: str):
        self.node_id = node_id
        self.node_type = node_type
        self.name = name
        self.value_type = value_type
        self.connection = None  # 连接到的其他节点


class ProgramBlock:
    """程序块数据类"""
    def __init__(self, name: str, block_type: str, x: int = 0, y: int = 0, params: List[Dict] = None):
        self.id = str(id(self))  # 添加唯一ID
        self.name = name
        self.type = block_type
        self.x = x
        self.y = y
        self.params = params or []
        self.selected = False
        self.input_nodes = []  # 输入节点列表
        self.output_nodes = []  # 输出节点列表
        
        # 为参数设置默认值
        for param in self.params:
            if 'value' not in param:
                if param['type'] == 'bool':
                    param['value'] = False
                elif param['type'] == 'int' or param['type'] == 'float':
                    param['value'] = 0
                else:
                    param['value'] = ''
        
        # 初始化输入输出节点
        self._init_nodes()
    
    def _init_nodes(self):
        """初始化输入输出节点"""
        # 为逻辑块创建条件输入和两个分支输出
        if self.type == 'logic' and (self.name == '条件判断' or self.name == '如果' or self.name == '如果-否则'):
            # 创建条件输入节点，支持boolean类型变量
            self.input_nodes.append(Node(
                node_id=f"{id(self)}_cond",
                node_type=NodeType.INPUT,
                name="条件",
                value_type="boolean"
            ))
            # 创建真分支输出节点
            self.output_nodes.append(Node(
                node_id=f"{id(self)}_true",
                node_type=NodeType.OUTPUT,
                name="真",
                value_type="execution"
            ))
            # 创建假分支输出节点
            self.output_nodes.append(Node(
                node_id=f"{id(self)}_false",
                node_type=NodeType.OUTPUT,
                name="假",
                value_type="execution"
            ))
        # 为循环块创建特定的输入输出节点
        elif self.type == 'logic' and (self.name == '循环' or self.name == '当条件满足时循环' or self.name == '无限循环'):
            # 添加开始输入节点
            self.input_nodes.append(Node(
                node_id=f"{id(self)}_start",
                node_type=NodeType.INPUT,
                name="开始",
                value_type="execution"
            ))
            # 添加结束输入节点
            self.input_nodes.append(Node(
                node_id=f"{id(self)}_end",
                node_type=NodeType.INPUT,
                name="结束",
                value_type="execution"
            ))
            # 添加循环体输出节点
            self.output_nodes.append(Node(
                node_id=f"{id(self)}_loop",
                node_type=NodeType.OUTPUT,
                name="循环体",
                value_type="execution"
            ))
            # 添加完成输出节点
            self.output_nodes.append(Node(
                node_id=f"{id(self)}_done",
                node_type=NodeType.OUTPUT,
                name="完成",
                value_type="execution"
            ))
        # 为其他块创建默认输入输出节点
        else:
            # 添加控制流输入节点
            self.input_nodes.append(Node(
                node_id=f"{id(self)}_input",
                node_type=NodeType.INPUT,
                name="输入",
                value_type="execution"
            ))
            # 添加控制流输出节点
            self.output_nodes.append(Node(
                node_id=f"{id(self)}_output",
                node_type=NodeType.OUTPUT,
                name="输出",
                value_type="execution"
            ))
        
        # 为传感器块添加数据输出节点
        if self.type == 'sensor':
            self.output_nodes.append(Node(
                node_id=f"{id(self)}_data",
                node_type=NodeType.OUTPUT,
                name="数据输出",
                value_type="float"
            ))


class Connection:
    """程序块连接类"""
    def __init__(self, from_block: int, from_node: Node, to_block: int, to_node: Node):
        self.from_block = from_block
        self.from_node = from_node
        self.to_block = to_block
        self.to_node = to_node
        
        # 建立双向连接
        from_node.connection = to_node
        to_node.connection = from_node


class Variable:
    """变量类"""
    def __init__(self, name: str, var_type: str, value: Any, unit: str = '', 
                 description: str = '', is_readonly: bool = False, is_temporary: bool = False):
        self.name = name
        self.type = var_type
        self.value = value
        self.unit = unit
        self.description = description
        self.is_readonly = is_readonly
        self.is_temporary = is_temporary  # 临时变量标志
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'type': self.type,
            'value': self.value,
            'unit': self.unit,
            'description': self.description,
            'is_readonly': self.is_readonly,
            'is_temporary': self.is_temporary
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Variable':
        """从字典创建变量"""
        return cls(
            name=data['name'],
            var_type=data['type'],
            value=data['value'],
            unit=data.get('unit', ''),
            description=data.get('description', ''),
            is_readonly=data.get('is_readonly', False),
            is_temporary=data.get('is_temporary', False)
        )


class Function:
    """函数模块类"""
    def __init__(self, name: str, func_type: str, description: str = '', params: List[Dict] = None):
        self.name = name
        self.type = func_type
        self.description = description
        self.params = params or []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'params': self.params
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Function':
        """从字典创建函数"""
        return cls(
            name=data['name'],
            func_type=data['type'],
            description=data.get('description', ''),
            params=data.get('params', [])
        )