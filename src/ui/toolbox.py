#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具箱组件：变量列表和函数列表
"""

import json
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QInputDialog, QMessageBox
from PyQt6.QtGui import QDrag, QPixmap, QMouseEvent
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal

from core.data_models import Variable, Function


import json
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QInputDialog, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QGroupBox, QLabel, QMenu
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal, QPoint


class VariableDisplayWidget(QWidget):
    """变量显示部件，用于显示单个变量及其属性"""
    
    def __init__(self, variable, parent=None):
        super().__init__(parent)
        self.variable = variable
        self.setFixedHeight(60)
        self.setFixedWidth(250)
        
        # 根据变量类型设置不同的背景颜色
        self.setStyleSheet(self._get_style_sheet())
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 变量名和类型
        name_label = QLabel(f"{variable.name}")
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # 变量值和类型信息
        var_type = getattr(variable, 'var_type', getattr(variable, 'type', 'unknown'))
        value = getattr(variable, 'value', None)
        value_text = f"值: {value}"
        type_text = f"类型: {var_type}"
        value_type_label = QLabel(f"{value_text} | {type_text}")
        value_type_label.setStyleSheet("font-size: 12px; color: #555;")
        
        # 变量类型标记
        type_tag = QLabel(self._get_type_tag_text())
        type_tag.setStyleSheet("font-size: 10px; color: white; padding: 2px 5px; border-radius: 3px; background-color: #666;")
        
        # 水平布局放置变量类型标记
        type_layout = QHBoxLayout()
        type_layout.addWidget(name_label)
        type_layout.addWidget(type_tag)
        type_layout.addStretch()
        
        layout.addLayout(type_layout)
        layout.addWidget(value_type_label)
        
        self.setLayout(layout)
    
    def _get_style_sheet(self):
        """根据变量类型返回对应的样式表"""
        if hasattr(self.variable, 'is_readonly') and self.variable.is_readonly:
            return "background-color: #f0f0f0; border: 1px solid #ddd; border-radius: 5px;"
        elif hasattr(self.variable, 'is_temporary') and self.variable.is_temporary:
            return "background-color: #fff0f0; border: 1px solid #ffdddd; border-radius: 5px;"
        else:  # 读写变量
            return "background-color: #f0fff0; border: 1px solid #ddffdd; border-radius: 5px;"
    
    def _get_type_tag_text(self):
        """获取变量类型标记文本"""
        if hasattr(self.variable, 'is_readonly') and self.variable.is_readonly:
            return "只读"
        elif hasattr(self.variable, 'is_temporary') and self.variable.is_temporary:
            return "临时"
        else:
            return "读写"
    
    def update_value(self, new_value):
        """更新变量值显示"""
        self.variable.value = new_value
        # 重新获取子部件并更新值
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if isinstance(item, QHBoxLayout):
                continue  # 跳过水平布局
            widget = item.widget()
            if widget and isinstance(widget, QLabel) and "值: " in widget.text():
                current_text = widget.text()
                # 提取类型信息
                type_part = current_text.split(" | ")[1]
                widget.setText(f"值: {getattr(self.variable, 'value', None)} | {type_part}")
                break
    
    def mousePressEvent(self, event):
        """实现直接鼠标拖拽功能"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 创建拖拽操作
            mime_data = QMimeData()
            variable_data = {
                'name': getattr(self.variable, 'name', ''),
                'type': getattr(self.variable, 'var_type', getattr(self.variable, 'type', 'unknown')),
                'value': getattr(self.variable, 'value', None)
            }
            drag_data = {
                'type': 'variable',
                'data': variable_data
            }
            mime_data.setText(json.dumps(drag_data))
            
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            
            # 设置拖拽图标
            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            
            # 执行拖拽
            result = drag.exec(Qt.DropAction.CopyAction)
            event.accept()
        else:
            super().mousePressEvent(event)


class VariableListWidget(QWidget):
    """变量列表组件，区分不同类型的变量"""
    variableCreated = pyqtSignal(Variable)
    variableUpdated = pyqtSignal(str, Variable)
    variableDeleted = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.variables = {}
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 创建滚动区域的内容部件
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 创建变量分类区域
        self.readonly_group = QGroupBox("只读变量")
        self.readonly_layout = QVBoxLayout(self.readonly_group)
        
        self.readwrite_group = QGroupBox("读写变量")
        self.readwrite_layout = QVBoxLayout(self.readwrite_group)
        
        self.temporary_group = QGroupBox("临时变量")
        self.temporary_layout = QVBoxLayout(self.temporary_group)
        
        # 添加到滚动布局
        self.scroll_layout.addWidget(self.readonly_group)
        self.scroll_layout.addWidget(self.readwrite_group)
        self.scroll_layout.addWidget(self.temporary_group)
        
        # 设置滚动区域
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
        
        # 初始化时隐藏空的分组
        self._update_group_visibility()
        
        # 初始化一些默认变量
        self._initDefaultVariables()
    
    def _initDefaultVariables(self):
        """初始化默认变量"""
        # 添加一些示例变量
        self.addVariable(Variable(name="count", var_type="int", value=0))
        self.addVariable(Variable(name="distance", var_type="float", value=0.0))
        self.addVariable(Variable(name="isDone", var_type="bool", value=False))
        self.addVariable(Variable(name="message", var_type="string", value=""))
    
    def addVariable(self, variable):
        """添加变量"""
        # 检查变量名是否已存在
        if variable.name in self.variables:
            QMessageBox.warning(self, "警告", f"变量名 '{variable.name}' 已存在！")
            return False
        
        # 存储变量
        self.variables[variable.name] = variable
        
        # 更新显示
        self.updateVariableDisplay()
        
        # 发射信号
        self.variableCreated.emit(variable)
        
        return True
    
    def updateVariable(self, name, variable):
        """更新变量"""
        if name not in self.variables:
            return False
        
        # 更新变量
        self.variables[name] = variable
        
        # 更新显示
        self._update_variable_widget(name, variable.value)
        
        # 发射信号
        self.variableUpdated.emit(name, variable)
        
        return True
    
    def removeVariable(self, name):
        """删除变量"""
        if name not in self.variables:
            return False
        
        # 删除变量
        del self.variables[name]
        
        # 更新显示
        self.updateVariableDisplay()
        
        # 发射信号
        self.variableDeleted.emit(name)
        
        return True
    
    def getVariable(self, name):
        """获取变量"""
        return self.variables.get(name)
    
    def getAllVariables(self):
        """获取所有变量"""
        return self.variables.copy()
    
    def _update_variable_widget(self, variable_name, new_value):
        """更新指定变量的显示部件"""
        # 检查只读变量区域
        for i in range(self.readonly_layout.count()):
            widget = self.readonly_layout.itemAt(i).widget()
            if isinstance(widget, VariableDisplayWidget) and widget.variable.name == variable_name:
                widget.update_value(new_value)
                return
        
        # 检查读写变量区域
        for i in range(self.readwrite_layout.count()):
            widget = self.readwrite_layout.itemAt(i).widget()
            if isinstance(widget, VariableDisplayWidget) and widget.variable.name == variable_name:
                widget.update_value(new_value)
                return
        
        # 检查临时变量区域
        for i in range(self.temporary_layout.count()):
            widget = self.temporary_layout.itemAt(i).widget()
            if isinstance(widget, VariableDisplayWidget) and widget.variable.name == variable_name:
                widget.update_value(new_value)
                return
    
    def updateVariableDisplay(self):
        """更新变量显示"""
        # 清空所有布局
        self._clear_layout(self.readonly_layout)
        self._clear_layout(self.readwrite_layout)
        self._clear_layout(self.temporary_layout)
        
        # 根据变量类型添加到不同区域
        for variable in self.variables.values():
            var_widget = VariableDisplayWidget(variable)
            
            # 设置拖拽功能和鼠标光标
            var_widget.setAcceptDrops(False)
            var_widget.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # 创建拖拽相关的上下文菜单
            var_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            var_widget.customContextMenuRequested.connect(lambda pos, v=variable, w=var_widget: self._show_var_menu(v, pos, w))
            
            # 双击编辑变量
            var_widget.mouseDoubleClickEvent = lambda event, v=variable: self._on_double_click(v)
            
            # 根据变量类型添加到不同布局
            if hasattr(variable, 'is_readonly') and variable.is_readonly:
                self.readonly_layout.addWidget(var_widget)
            elif hasattr(variable, 'is_temporary') and variable.is_temporary:
                self.temporary_layout.addWidget(var_widget)
            else:
                self.readwrite_layout.addWidget(var_widget)
        
        # 更新分组可见性
        self._update_group_visibility()
    
    def _clear_layout(self, layout):
        """清空布局中的所有部件"""
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def _update_group_visibility(self):
        """更新分组的可见性"""
        self.readonly_group.setVisible(self.readonly_layout.count() > 0)
        self.readwrite_group.setVisible(self.readwrite_layout.count() > 0)
        self.temporary_group.setVisible(self.temporary_layout.count() > 0)
    
    def _show_var_menu(self, variable, pos, widget):
        """显示变量上下文菜单，支持拖拽操作"""
        menu = QMenu()
        drag_action = menu.addAction("拖拽到参数位置")
        
        action = menu.exec(widget.mapToGlobal(pos))
        if action == drag_action:
            # 创建拖拽操作
            mime_data = QMimeData()
            variable_data = {
                'name': variable.name,
                'type': variable.var_type,
                'value': variable.value
            }
            drag_data = {
                'type': 'variable',
                'data': variable_data
            }
            mime_data.setText(json.dumps(drag_data))
            
            drag = QDrag(widget)
            drag.setMimeData(mime_data)
            
            # 设置拖拽图标
            pixmap = QPixmap(64, 32)
            pixmap.fill(Qt.GlobalColor.white)
            drag.setPixmap(pixmap)
            
            # 执行拖拽
            drag.exec(Qt.DropAction.CopyAction)
    
    def _on_double_click(self, variable):
        """双击编辑变量"""
        if hasattr(variable, 'is_readonly') and variable.is_readonly:
            QMessageBox.information(self, "信息", "只读变量不可编辑！")
            return
        
        # 显示编辑对话框
        new_value, ok = QInputDialog.getText(self, "编辑变量", 
                                          f"变量名: {variable.name}\n类型: {variable.var_type}\n输入新值:", 
                                          text=str(variable.value))
        
        if ok:
            # 转换值类型
            try:
                if variable.var_type == "int":
                    new_value = int(new_value)
                elif variable.var_type == "float":
                    new_value = float(new_value)
                elif variable.var_type == "bool":
                    new_value = new_value.lower() in ("true", "yes", "1", "y", "t")
            except ValueError:
                QMessageBox.warning(self, "警告", f"无法将 '{new_value}' 转换为 {variable.var_type} 类型！")
                return
            
            # 更新变量值
            self.updateVariable(variable.name, variable)


class FunctionCategoryWidget(QGroupBox):
    """函数分类组件"""
    
    def __init__(self, title, functions, parent=None):
        super().__init__(title, parent)
        self.functions = {}
        
        # 创建列表部件
        self.list_widget = QListWidget()
        self.list_widget.setDragEnabled(True)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        
        # 添加函数到列表
        for func_data in functions:
            # 创建Function对象并存储
            function = Function(
                name=func_data["name"],
                func_type=func_data["type"],
                params=func_data["params"],
                description=func_data.get("description", "")
            )
            self.functions[function.name] = function
            
            # 创建列表项
            item = QListWidgetItem(function.name)
            item.setData(Qt.ItemDataRole.UserRole, function.name)
            self.list_widget.addItem(item)
            
            # 设置提示信息
            if function.description:
                item.setToolTip(function.description)
        
        # 设置布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)
        
        # 连接拖拽信号
        self.list_widget.startDrag = self._start_drag
    
    def _start_drag(self, supported_actions):
        """开始拖拽操作"""
        item = self.list_widget.currentItem()
        if item:
            name = item.data(Qt.ItemDataRole.UserRole)
            function = self.functions.get(name)
            if function:
                # 创建拖拽对象
                drag = QDrag(self.list_widget)
                
                # 设置拖拽数据
                mime_data = QMimeData()
                function_data = {
                      'name': function.name,
                      'type': getattr(function, 'type', getattr(function, 'func_type', 'unknown')),
                      'params': function.params
                  }
                drag_data = {
                    'type': 'function',
                    'data': function_data
                }
                mime_data.setText(json.dumps(drag_data))
                drag.setMimeData(mime_data)
                
                # 设置拖拽图标
                pixmap = QPixmap(64, 32)
                pixmap.fill(Qt.GlobalColor.white)
                drag.setPixmap(pixmap)
                
                # 执行拖拽
                drag.exec(Qt.DropAction.CopyAction)


class FunctionListWidget(QWidget):
    """函数列表部件，支持分类显示"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_functions = {}
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 创建滚动区域的内容部件
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 初始化函数分类
        self._init_function_categories()
        
        # 设置滚动区域
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
    
    def _init_function_categories(self):
        """初始化函数分类"""
        # 电机控制函数
        motor_functions = [
            {
                "name": "前进",
                "type": "motor",
                "params": [
                    {"name": "速度", "type": "int", "default": 50, "min": 0, "max": 100},
                    {"name": "时间", "type": "float", "default": 1.0, "min": 0.1, "max": 10.0}
                ],
                "description": "控制机器人前进"
            },
            {
                "name": "后退",
                "type": "motor",
                "params": [
                    {"name": "速度", "type": "int", "default": 50, "min": 0, "max": 100},
                    {"name": "时间", "type": "float", "default": 1.0, "min": 0.1, "max": 10.0}
                ],
                "description": "控制机器人后退"
            },
            {
                "name": "左转",
                "type": "motor",
                "params": [
                    {"name": "速度", "type": "int", "default": 30, "min": 0, "max": 100},
                    {"name": "角度", "type": "int", "default": 90, "min": 1, "max": 360}
                ],
                "description": "控制机器人左转"
            },
            {
                "name": "右转",
                "type": "motor",
                "params": [
                    {"name": "速度", "type": "int", "default": 30, "min": 0, "max": 100},
                    {"name": "角度", "type": "int", "default": 90, "min": 1, "max": 360}
                ],
                "description": "控制机器人右转"
            },
            {
                "name": "停止",
                "type": "motor",
                "params": [],
                "description": "停止所有电机"
            }
        ]
        
        # 传感器函数
        sensor_functions = [
            {
                "name": "读取距离",
                "type": "sensor",
                "params": [
                    {"name": "传感器ID", "type": "int", "default": 1},
                    {"name": "变量名", "type": "string", "default": "distance"}
                ],
                "description": "读取超声波传感器距离"
            },
            {
                "name": "读取光线",
                "type": "sensor",
                "params": [
                    {"name": "传感器ID", "type": "int", "default": 1},
                    {"name": "变量名", "type": "string", "default": "light"}
                ],
                "description": "读取环境光线强度"
            },
            {
                "name": "读取声音",
                "type": "sensor",
                "params": [
                    {"name": "传感器ID", "type": "int", "default": 1},
                    {"name": "变量名", "type": "string", "default": "sound"}
                ],
                "description": "读取环境声音强度"
            },
            {
                "name": "读取温度",
                "type": "sensor",
                "params": [
                    {"name": "传感器ID", "type": "int", "default": 1},
                    {"name": "变量名", "type": "string", "default": "temperature"}
                ],
                "description": "读取环境温度"
            }
        ]
        
        # 逻辑函数 - 增加更多逻辑块
        logic_functions = [
            {
                "name": "条件判断",
                "type": "logic",
                "params": [
                    {"name": "条件", "type": "expression", "default": "count > 0"}
                ],
                "description": "条件判断逻辑块"
            },
            {
                "name": "循环",
                "type": "logic",
                "params": [
                    {"name": "次数", "type": "int", "default": 10, "min": 1, "max": 100}
                ],
                "description": "循环逻辑块"
            },
            {
                "name": "如果",
                "type": "logic",
                "params": [
                    {"name": "条件", "type": "expression", "default": "x > y"}
                ],
                "description": "如果条件满足则执行"
            },
            {
                "name": "如果-否则",
                "type": "logic",
                "params": [
                    {"name": "条件", "type": "expression", "default": "x > y"}
                ],
                "description": "条件判断带分支"
            },
            {
                "name": "当条件满足时循环",
                "type": "logic",
                "params": [
                    {"name": "条件", "type": "expression", "default": "count < 10"}
                ],
                "description": "条件循环"
            },
            {
                "name": "无限循环",
                "type": "logic",
                "params": [],
                "description": "无限循环块"
            }
        ]
        
        # 变量操作函数
        variable_functions = [
            {
                "name": "变量赋值",
                "type": "variable",
                "params": [
                    {"name": "变量名", "type": "string", "default": "count"},
                    {"name": "值", "type": "expression", "default": "0"}
                ],
                "description": "给变量赋值"
            },
            {
                "name": "变量增加",
                "type": "variable",
                "params": [
                    {"name": "变量名", "type": "string", "default": "count"},
                    {"name": "增量", "type": "int", "default": 1}
                ],
                "description": "增加变量的值"
            },
            {
                "name": "变量减少",
                "type": "variable",
                "params": [
                    {"name": "变量名", "type": "string", "default": "count"},
                    {"name": "减量", "type": "int", "default": 1}
                ],
                "description": "减少变量的值"
            }
        ]
        
        # 创建并添加分类组件
        motor_category = FunctionCategoryWidget("电机控制", motor_functions)
        sensor_category = FunctionCategoryWidget("传感器", sensor_functions)
        logic_category = FunctionCategoryWidget("逻辑块", logic_functions)
        variable_category = FunctionCategoryWidget("变量操作", variable_functions)
        
        # 添加到滚动布局
        self.scroll_layout.addWidget(motor_category)
        self.scroll_layout.addWidget(sensor_category)
        self.scroll_layout.addWidget(logic_category)
        self.scroll_layout.addWidget(variable_category)
        
        # 合并所有函数到all_functions字典
        for category in [motor_category, sensor_category, logic_category, variable_category]:
            self.all_functions.update(category.functions)
    
    def getFunction(self, name):
        """获取函数"""
        return self.all_functions.get(name)
    
    def getAllFunctions(self):
        """获取所有函数"""
        return self.all_functions.copy()