#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对话框组件
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
    QPushButton, QGroupBox, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt


class CreateVariableDialog(QDialog):
    """创建变量对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("创建变量")
        self.resize(300, 200)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 变量名输入
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("变量名:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入变量名")
        name_layout.addWidget(self.name_edit)
        main_layout.addLayout(name_layout)
        
        # 变量类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["int", "float", "bool", "string"])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        main_layout.addLayout(type_layout)
        
        # 默认值输入
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("默认值:"))
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("输入默认值")
        value_layout.addWidget(self.value_edit)
        main_layout.addLayout(value_layout)
        
        # 设置默认值
        self.on_type_changed(0)  # 默认选择int类型
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
    
    def on_type_changed(self, index):
        """类型改变事件处理"""
        # 根据类型设置默认值
        type_str = self.type_combo.currentText()
        if type_str == "int":
            self.value_edit.setText("0")
            self.value_edit.setPlaceholderText("整数")
        elif type_str == "float":
            self.value_edit.setText("0.0")
            self.value_edit.setPlaceholderText("浮点数")
        elif type_str == "bool":
            self.value_edit.setText("False")
            self.value_edit.setPlaceholderText("True或False")
        elif type_str == "string":
            self.value_edit.setText("")
            self.value_edit.setPlaceholderText("字符串")
    
    def accept(self):
        """确认按钮点击事件"""
        # 验证变量名
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "变量名不能为空！")
            return
        
        # 验证变量名格式
        if not name.isidentifier():
            QMessageBox.warning(self, "警告", "变量名格式不正确！变量名只能包含字母、数字和下划线，且不能以数字开头。")
            return
        
        # 验证默认值
        type_str = self.type_combo.currentText()
        value_text = self.value_edit.text().strip()
        
        try:
            if type_str == "int":
                int(value_text)
            elif type_str == "float":
                float(value_text)
            elif type_str == "bool":
                if value_text.lower() not in ("true", "false", "yes", "no", "1", "0"):
                    raise ValueError("布尔值必须是True或False")
        except ValueError as e:
            QMessageBox.warning(self, "警告", f"默认值格式不正确: {str(e)}")
            return
        
        super().accept()
    
    def get_values(self):
        """获取对话框输入的值"""
        name = self.name_edit.text().strip()
        type_str = self.type_combo.currentText()
        value_text = self.value_edit.text().strip()
        
        # 转换值类型
        if type_str == "int":
            value = int(value_text)
        elif type_str == "float":
            value = float(value_text)
        elif type_str == "bool":
            value = value_text.lower() in ("true", "yes", "1")
        elif type_str == "string":
            value = value_text
        
        return name, type_str, value


class EditParameterDialog(QDialog):
    """编辑参数对话框"""
    
    def __init__(self, param_info, parent=None):
        super().__init__(parent)
        self.param_info = param_info
        self.setWindowTitle(f"编辑参数: {param_info['name']}")
        self.resize(300, 150)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 参数信息
        info_label = QLabel(f"参数名: {self.param_info['name']}\n类型: {self.param_info['type']}")
        main_layout.addWidget(info_label)
        
        # 参数值输入
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("值:"))
        self.value_edit = QLineEdit()
        
        # 设置当前值
        current_value = self.param_info.get('value', self.param_info.get('default', ''))
        self.value_edit.setText(str(current_value))
        
        value_layout.addWidget(self.value_edit)
        main_layout.addLayout(value_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
    
    def accept(self):
        """确认按钮点击事件"""
        # 验证值格式
        type_str = self.param_info['type']
        value_text = self.value_edit.text().strip()
        
        try:
            if type_str == "int":
                value = int(value_text)
                # 检查范围
                if 'min' in self.param_info and value < self.param_info['min']:
                    raise ValueError(f"值不能小于 {self.param_info['min']}")
                if 'max' in self.param_info and value > self.param_info['max']:
                    raise ValueError(f"值不能大于 {self.param_info['max']}")
            elif type_str == "float":
                value = float(value_text)
                # 检查范围
                if 'min' in self.param_info and value < self.param_info['min']:
                    raise ValueError(f"值不能小于 {self.param_info['min']}")
                if 'max' in self.param_info and value > self.param_info['max']:
                    raise ValueError(f"值不能大于 {self.param_info['max']}")
            elif type_str == "bool":
                if value_text.lower() not in ("true", "false", "yes", "no", "1", "0"):
                    raise ValueError("布尔值必须是True或False")
            # 字符串和表达式类型不需要特殊验证
        except ValueError as e:
            QMessageBox.warning(self, "警告", f"值格式不正确: {str(e)}")
            return
        
        super().accept()
    
    def get_value(self):
        """获取编辑后的值"""
        type_str = self.param_info['type']
        value_text = self.value_edit.text().strip()
        
        # 转换值类型
        if type_str == "int":
            return int(value_text)
        elif type_str == "float":
            return float(value_text)
        elif type_str == "bool":
            return value_text.lower() in ("true", "yes", "1")
        else:
            return value_text


class ExpressionEditorDialog(QDialog):
    """表达式编辑器对话框"""
    
    def __init__(self, current_expression="", variables=[], parent=None):
        super().__init__(parent)
        self.variables = variables
        self.setWindowTitle("编辑表达式")
        self.resize(400, 300)
        self.init_ui(current_expression)
    
    def init_ui(self, current_expression):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 表达式输入
        expr_label = QLabel("表达式:")
        main_layout.addWidget(expr_label)
        self.expr_edit = QLineEdit()
        self.expr_edit.setText(current_expression)
        main_layout.addWidget(self.expr_edit)
        
        # 可用变量列表
        if self.variables:
            var_group = QGroupBox("可用变量:")
            var_layout = QVBoxLayout(var_group)
            
            for var_name, var_type, var_value in self.variables:
                var_label = QLabel(f"{var_name} ({var_type}): {var_value}")
                var_layout.addWidget(var_label)
            
            main_layout.addWidget(var_group)
        
        # 表达式说明
        help_text = """
表达式语法说明：
- 可以使用变量、数字和操作符
- 支持的操作符：+ - * / % ** ( )
- 支持的比较操作符：== != < > <= >=
- 支持的逻辑操作符：and or not
        """
        help_label = QLabel(help_text)
        help_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        main_layout.addWidget(help_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
    
    def accept(self):
        """确认按钮点击事件"""
        # 简单验证表达式
        expression = self.expr_edit.text().strip()
        if not expression:
            QMessageBox.warning(self, "警告", "表达式不能为空！")
            return
        
        # 可以添加更复杂的表达式验证
        # 例如检查括号是否匹配等
        
        super().accept()
    
    def get_expression(self):
        """获取编辑后的表达式"""
        return self.expr_edit.text().strip()