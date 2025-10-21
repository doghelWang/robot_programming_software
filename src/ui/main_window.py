#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用程序主窗口
"""

import os
import json
import yaml
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QGroupBox, QLabel, QDockWidget, QMessageBox, QFileDialog,
    QInputDialog, QToolBar, QMenu, QMenuBar, QStatusBar, QListWidget, 
    QListWidgetItem, QFrame, QComboBox, QLineEdit, QDialog, QGridLayout
)
from PyQt6.QtCore import Qt, QSettings, QSize, QMimeData
from PyQt6.QtGui import QIcon, QCloseEvent, QAction, QColor, QFont, QDrag

from ui.canvas import ProgrammingCanvas
from ui.toolbox import VariableListWidget, FunctionListWidget
from ui.dialogs import CreateVariableDialog
from core.data_models import ProgramBlock, Node, NodeType, Variable


class RobotProgrammingApp(QMainWindow):
    """机器人编程应用主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.connect_signals()
        # 连接画布的变量更新信号到变量显示更新槽函数
        self.canvas.variableUpdated.connect(self.handle_variable_updated)
        self.load_settings()
    
    def init_ui(self):
        """初始化UI"""
        # 设置窗口标题和大小
        self.setWindowTitle("机器人编程软件")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央组件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建变量显示区域
        self.variable_display_area = self.create_variable_display_area()
        self.main_layout.addWidget(self.variable_display_area)
        
        # 创建主分割器
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.main_splitter)
        
        # 创建左侧工具箱
        self.create_toolbox()
        
        # 创建编程画布
        self.canvas = ProgrammingCanvas(self)
        self.main_splitter.addWidget(self.canvas)
        
        # 设置分割器比例
        self.main_splitter.setSizes([300, 900])
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # 添加按钮
        self.new_action = QAction("新建", self)
        self.new_action.triggered.connect(self.new_program)
        toolbar.addAction(self.new_action)
        
        self.load_action = QAction("加载", self)
        self.load_action.triggered.connect(self.load_program)
        toolbar.addAction(self.load_action)
        
        self.save_action = QAction("保存", self)
        self.save_action.triggered.connect(self.save_program)
        toolbar.addAction(self.save_action)
        
        toolbar.addSeparator()
        
        self.run_action = QAction("运行", self)
        self.run_action.triggered.connect(self.run_program)
        toolbar.addAction(self.run_action)
        
        self.stop_action = QAction("停止", self)
        self.stop_action.triggered.connect(self.stop_program)
        toolbar.addAction(self.stop_action)
        
        toolbar.addSeparator()
        
        self.clear_action = QAction("清空", self)
        self.clear_action.triggered.connect(self.clear_canvas)
        toolbar.addAction(self.clear_action)
        
        toolbar.addSeparator()
        
        self.export_action = QAction("导出代码", self)
        self.export_action.triggered.connect(self.export_code)
        toolbar.addAction(self.export_action)
    
    def create_toolbox(self):
        """创建左侧工具箱"""
        toolbox_widget = QWidget()
        toolbox_layout = QVBoxLayout(toolbox_widget)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 创建函数列表选项卡
        self.function_list = FunctionListWidget()
        function_group = QGroupBox("函数库")
        function_layout = QVBoxLayout(function_group)
        function_layout.addWidget(self.function_list)
        self.tab_widget.addTab(function_group, "函数")
        
        # 创建变量列表选项卡
        self.variable_list = VariableListWidget()
        variable_group = QGroupBox("变量")
        variable_layout = QVBoxLayout(variable_group)
        
        # 添加变量按钮
        add_var_button = QPushButton("添加变量")
        add_var_button.clicked.connect(self.show_create_variable_dialog)
        variable_layout.addWidget(add_var_button)
        variable_layout.addWidget(self.variable_list)
        
        self.tab_widget.addTab(variable_group, "变量")
        
        # 添加到工具箱布局
        toolbox_layout.addWidget(self.tab_widget)
        toolbox_layout.addStretch()
        
        # 添加工具箱到分割器
        self.main_splitter.addWidget(toolbox_widget)
    
    def create_variable_display_area(self):
        """创建顶部变量显示区域"""
        # 创建容器部件
        container = QFrame()
        container.setFrameShape(QFrame.Shape.StyledPanel)
        container.setFrameShadow(QFrame.Shadow.Raised)
        container.setMinimumHeight(100)
        container.setMaximumHeight(150)
        
        # 创建主布局
        main_layout = QVBoxLayout(container)
        
        # 创建标题
        title_label = QLabel("变量列表")
        title_font = title_label.font()
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建变量分类显示
        categories_layout = QHBoxLayout()
        
        # 只读变量组
        read_only_group = QGroupBox("只读变量")
        read_only_layout = QVBoxLayout(read_only_group)
        self.read_only_variables_list = QListWidget()
        self.read_only_variables_list.setSortingEnabled(True)
        read_only_layout.addWidget(self.read_only_variables_list)
        categories_layout.addWidget(read_only_group, 1)
        
        # 读写变量组
        read_write_group = QGroupBox("读写变量")
        read_write_layout = QVBoxLayout(read_write_group)
        self.read_write_variables_list = QListWidget()
        self.read_write_variables_list.setSortingEnabled(True)
        read_write_layout.addWidget(self.read_write_variables_list)
        categories_layout.addWidget(read_write_group, 1)
        
        # 临时变量组
        temp_group = QGroupBox("临时变量")
        temp_layout = QVBoxLayout(temp_group)
        self.temp_variables_list = QListWidget()
        self.temp_variables_list.setSortingEnabled(True)
        temp_layout.addWidget(self.temp_variables_list)
        categories_layout.addWidget(temp_group, 1)
        
        # 添加分类布局到主布局
        main_layout.addLayout(categories_layout)
        
        # 初始化变量显示
        self.update_variable_display()
        
        # 允许从变量显示区域拖拽变量
        self.setup_variable_drag_and_drop()
        
        return container
    
    def handle_variable_updated(self, var_name, var_type):
        """处理变量更新事件，将变量添加到顶部变量区"""
        # 检查变量是否已存在
        if hasattr(self, 'variable_list') and self.variable_list:
            # 检查变量是否已存在
            variable_exists = False
            all_vars = self.variable_list.get_all_variables()
            for var_category, variables in all_vars.items():
                for var in variables:
                    if var['name'] == var_name:
                        variable_exists = True
                        break
                if variable_exists:
                    break
            
            # 如果变量不存在，添加到读写变量列表
            if not variable_exists:
                # 添加变量到读写变量列表
                self.variable_list.add_variable(var_name, var_type, 'read_write')
                print(f"变量 {var_name} 已添加到顶部变量区")
            
            # 更新变量显示
            self.update_variable_display()
    
    def setup_variable_drag_and_drop(self):
        """设置变量显示区域的拖拽功能"""
        print("设置变量显示区域的拖拽功能...")
        # 设置列表为可拖拽
        self.read_only_variables_list.setDragEnabled(True)
        self.read_write_variables_list.setDragEnabled(True)
        self.temp_variables_list.setDragEnabled(True)
        
        # 设置拖动模式
        self.read_only_variables_list.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        self.read_write_variables_list.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        self.temp_variables_list.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        
        # 重写拖拽事件
        def create_drag_item(source_list):
            items = source_list.selectedItems()
            if items:
                item_text = items[0].text()
                var_name = item_text.split()[0]  # 假设格式为 "变量名 (类型)"
                print(f"从变量区拖拽变量: {var_name}")
                # 获取变量信息
                if hasattr(self, 'variable_list'):
                    all_vars = self.variable_list.get_all_variables()
                    # 遍历分类变量字典查找变量
                    for var_category, variables in all_vars.items():
                        for var in variables:
                            if var['name'] == var_name:
                                # 创建拖拽数据
                                drag_data = {
                                    'type': 'variable',
                                    'data': {
                                        'name': var_name,
                                        'type': var.get('type', var.get('var_type', 'unknown')),
                                        'value': var.get('value', '')
                                    }
                                }
                                print(f"变量拖拽数据创建成功: {drag_data}")
                                return drag_data
            return None
        
        # 为每个列表添加拖拽事件处理器
        for var_list in [self.read_only_variables_list, self.read_write_variables_list, self.temp_variables_list]:
            original_start_drag = var_list.startDrag
            
            def start_drag_proxy(action, source=var_list):
                drag_data = create_drag_item(source)
                if drag_data:
                    mime_data = QMimeData()
                    mime_data.setText(json.dumps(drag_data))
                    drag = QDrag(source)
                    drag.setMimeData(mime_data)
                    drag.exec(Qt.CopyAction)
                else:
                    original_start_drag(action)
            
            var_list.startDrag = start_drag_proxy
    
    def update_variable_display(self):
        """更新变量显示区域"""
        print("更新变量显示区域...")
        # 清空所有列表
        self.read_only_variables_list.clear()
        self.read_write_variables_list.clear()
        self.temp_variables_list.clear()
        
        # 分类添加变量
        # 从variable_list获取变量列表
        if hasattr(self, 'variable_list'):
            all_vars = self.variable_list.get_all_variables()
            print(f"获取到变量列表: {all_vars}")
            # 遍历分类变量字典
            for var_category, variables in all_vars.items():
                print(f"处理{var_category}分类下的变量")
                for var in variables:
                    # 确保变量是字典形式
                    if isinstance(var, dict):
                        var_name = var.get('name', 'Unknown')
                        var_type = var.get('type', var.get('var_type', 'Unknown'))
                        value = var.get('value', '')
                        is_readonly = var.get('is_readonly', False)
                        is_temporary = var.get('is_temporary', False)
                    else:
                        # 处理对象形式的变量
                        var_name = getattr(var, 'name', 'Unknown')
                        var_type = getattr(var, 'type', getattr(var, 'var_type', 'Unknown'))
                        value = getattr(var, 'value', '')
                        is_readonly = getattr(var, 'is_readonly', False)
                        is_temporary = getattr(var, 'is_temporary', False)
                      
                    # 格式化变量显示文本
                    display_text = f"{var_name} ({var_type})\n值: {value}"
                    print(f"添加变量到显示区域: {display_text}")
                    item = QListWidgetItem(display_text)
                  
                    # 根据变量类型设置背景色
                    if is_readonly:
                        item.setBackground(QColor(240, 240, 240))
                        self.read_only_variables_list.addItem(item)
                    elif is_temporary:
                        item.setBackground(QColor(255, 248, 225))
                        self.temp_variables_list.addItem(item)
                    else:
                        item.setBackground(QColor(220, 230, 241))
                        self.read_write_variables_list.addItem(item)
                    
                    # 设置字体大小
                    font = item.font()
                    font.setPointSize(9)
                    item.setFont(font)
                    
                    # 设置物品大小
                    item.setSizeHint(QSize(0, 40))
    
    def connect_signals(self):
        """连接信号槽"""
        self.canvas.blockSelected.connect(self.on_block_selected)
        self.canvas.connectionCreated.connect(self.on_connection_created)
        self.variable_list.variableCreated.connect(self.on_variable_created)
        self.variable_list.variableUpdated.connect(self.on_variable_updated)
        self.variable_list.variableDeleted.connect(self.on_variable_deleted)
    
    def load_settings(self):
        """加载设置"""
        # 这里可以加载应用程序设置
        pass
    
    def save_settings(self):
        """保存设置"""
        # 这里可以保存应用程序设置
        pass
    
    def on_block_selected(self, block_index):
        """块选择事件处理"""
        if block_index >= 0:
            block = self.canvas.blocks[block_index]
            self.statusBar.showMessage(f"选中: {block.name}")
        else:
            self.statusBar.showMessage("就绪")
    
    def on_connection_created(self, connection):
        """连接创建事件处理"""
        # 这里可以添加连接创建后的处理逻辑
        self.statusBar.showMessage(f"创建连接: {connection.from_node.name} -> {connection.to_node.name}")
    
    def on_variable_created(self, variable):
        """变量创建事件处理"""
        self.statusBar.showMessage(f"创建变量: {variable.name}")
        # 更新变量显示
        self.update_variable_display()
    
    def on_variable_updated(self, old_name, variable):
        """变量更新事件处理"""
        self.statusBar.showMessage(f"更新变量: {old_name} -> {variable.name}")
        # 更新变量显示
        self.update_variable_display()
    
    def on_variable_deleted(self, name):
        """变量删除事件处理"""
        self.statusBar.showMessage(f"删除变量: {name}")
        # 更新变量显示
        self.update_variable_display()
    
    def show_create_variable_dialog(self):
        """显示创建变量对话框"""
        from PyQt6.QtWidgets import QDialog, QLineEdit, QComboBox, QRadioButton, QButtonGroup
        
        dialog = QDialog(self)
        dialog.setWindowTitle("创建变量")
        dialog.resize(300, 250)
        
        layout = QVBoxLayout(dialog)
        
        # 变量名输入
        name_layout = QHBoxLayout()
        name_label = QLabel("变量名:")
        name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_input)
        layout.addLayout(name_layout)
        
        # 变量类型选择
        type_layout = QHBoxLayout()
        type_label = QLabel("变量类型:")
        type_combo = QComboBox()
        type_combo.addItems(["int", "float", "string", "bool"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(type_combo)
        layout.addLayout(type_layout)
        
        # 默认值输入
        value_layout = QHBoxLayout()
        value_label = QLabel("默认值:")
        value_input = QLineEdit()
        value_layout.addWidget(value_label)
        value_layout.addWidget(value_input)
        layout.addLayout(value_layout)
        
        # 变量访问类型选择
        access_type_layout = QHBoxLayout()
        access_type_label = QLabel("访问类型:")
        access_type_group = QButtonGroup(dialog)
        
        readwrite_radio = QRadioButton("读写")
        readonly_radio = QRadioButton("只读")
        temporary_radio = QRadioButton("临时")
        
        # 默认选择读写
        readwrite_radio.setChecked(True)
        
        access_type_group.addButton(readwrite_radio)
        access_type_group.addButton(readonly_radio)
        access_type_group.addButton(temporary_radio)
        
        access_type_layout.addWidget(access_type_label)
        access_type_layout.addWidget(readwrite_radio)
        access_type_layout.addWidget(readonly_radio)
        access_type_layout.addWidget(temporary_radio)
        layout.addLayout(access_type_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("取消")
        create_button = QPushButton("创建")
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(create_button)
        layout.addLayout(button_layout)
        
        # 连接信号
        cancel_button.clicked.connect(dialog.reject)
        
        # 处理创建按钮点击
        def handle_create():
            name = name_input.text().strip()
            value_type = type_combo.currentText()
            default_value_text = value_input.text().strip()
            
            # 确定变量访问类型
            is_readonly = readonly_radio.isChecked()
            is_temporary = temporary_radio.isChecked()
            
            # 验证变量名
            if not name:
                QMessageBox.warning(dialog, "错误", "变量名不能为空")
                return
            
            # 解析默认值
            try:
                if value_type == "int":
                    default_value = int(default_value_text) if default_value_text else 0
                elif value_type == "float":
                    default_value = float(default_value_text) if default_value_text else 0.0
                elif value_type == "bool":
                    if default_value_text.lower() in ("true", "yes", "1", "y", "t"):
                        default_value = True
                    elif default_value_text.lower() in ("false", "no", "0", "n", "f"):
                        default_value = False
                    else:
                        default_value = False
                else:  # string
                    default_value = default_value_text
            except ValueError:
                QMessageBox.warning(dialog, "错误", f"无法将 '{default_value_text}' 转换为 {value_type} 类型")
                return
            
            # 创建变量
            variable = Variable(name=name, var_type=value_type, value=default_value,
                               is_readonly=is_readonly, is_temporary=is_temporary)
            
            # 添加到变量列表
            self.variable_list.addVariable(variable)
            
            # 关闭对话框
            dialog.accept()
        
        create_button.clicked.connect(handle_create)
        
        # 显示对话框
        dialog.exec()
    
    def new_program(self):
        """新建程序"""
        # 询问是否保存当前程序
        if self.canvas.blocks or self.canvas.connections:
            reply = QMessageBox.question(
                self, "确认", "是否保存当前程序？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                if not self.save_program():
                    return
        
        # 清空画布
        self.canvas.clear()
        self.statusBar.showMessage("新建程序")
    
    def save_program(self):
        """保存程序"""
        # 打开文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存程序", "", "程序文件 (*.robot);;JSON文件 (*.json);;YAML文件 (*.yaml;*.yml)"
        )
        
        if not file_path:
            return False
        
        try:
            # 准备程序数据
            program_data = {
                "blocks": [],
                "connections": []
            }
            
            # 保存块数据
            for block in self.canvas.blocks:
                block_data = {
                    "id": block.id,
                    "name": block.name,
                    "type": block.type,
                    "x": block.x,
                    "y": block.y,
                    "params": block.params,
                    "input_nodes": [node.node_id for node in block.input_nodes],
                    "output_nodes": [node.node_id for node in block.output_nodes]
                }
                program_data["blocks"].append(block_data)
            
            # 保存连接数据
            for conn in self.canvas.connections:
                conn_type = "execution" if conn.from_node.value_type == "execution" else "data"
                conn_data = {
                    "from_block": conn.from_block,
                    "from_block_id": self.canvas.blocks[conn.from_block].id,
                    "from_node": conn.from_node.node_id,
                    "to_block": conn.to_block,
                    "to_block_id": self.canvas.blocks[conn.to_block].id,
                    "to_node": conn.to_node.node_id,
                    "type": conn_type  # 区分执行流连接和数据流连接
                }
                program_data["connections"].append(conn_data)
            
            # 根据文件扩展名选择保存格式
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.json' or ext == '.robot':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(program_data, f, ensure_ascii=False, indent=2)
            elif ext in ['.yaml', '.yml']:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(program_data, f, allow_unicode=True)
            
            self.statusBar.showMessage(f"程序已保存: {file_path}")
            return True
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存程序失败: {str(e)}")
            return False
    
    def load_program(self):
        """加载程序"""
        # 询问是否保存当前程序
        if self.canvas.blocks or self.canvas.connections:
            reply = QMessageBox.question(
                self, "确认", "是否保存当前程序？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                if not self.save_program():
                    return
        
        # 打开文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载程序", "", "程序文件 (*.robot);;JSON文件 (*.json);;YAML文件 (*.yaml;*.yml)"
        )
        
        if not file_path:
            return
        
        try:
            # 清空画布
            self.canvas.clear()
            
            # 根据文件扩展名选择加载格式
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.json', '.robot']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    program_data = json.load(f)
            elif ext in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    program_data = yaml.safe_load(f)
            
            # 创建块ID到索引的映射
            block_id_to_index = {}
            
            # 加载块数据
            for block_data in program_data.get("blocks", []):
                block = ProgramBlock(
                    name=block_data["name"],
                    block_type=block_data["type"],
                    x=block_data["x"],
                    y=block_data["y"],
                    params=block_data.get("params", [])
                )
                # 如果保存的数据中有ID，使用它；否则保留自动生成的ID
                if "id" in block_data:
                    block.id = block_data["id"]
                
                self.canvas.addBlock(block)
                block_id_to_index[block.id] = len(self.canvas.blocks) - 1
            
            # 加载连接数据
            for conn_data in program_data.get("connections", []):
                # 找到源块和目标块
                from_block_idx = conn_data["from_block"]
                to_block_idx = conn_data["to_block"]
                
                # 找到源节点和目标节点
                from_node_id = conn_data["from_node"]
                to_node_id = conn_data["to_node"]
                
                from_node = None
                to_node = None
                
                # 查找源节点
                for node in self.canvas.blocks[from_block_idx].output_nodes:
                    if node.node_id == from_node_id:
                        from_node = node
                        break
                
                # 查找目标节点
                for node in self.canvas.blocks[to_block_idx].input_nodes:
                    if node.node_id == to_node_id:
                        to_node = node
                        break
                
                # 如果找到节点，创建连接
                if from_node and to_node:
                    new_connection = Connection(
                        from_block=from_block_idx,
                        from_node=from_node,
                        to_block=to_block_idx,
                        to_node=to_node
                    )
                    self.canvas.connections.append(new_connection)
            
            self.statusBar.showMessage(f"程序已加载: {file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载程序失败: {str(e)}")
    
    def export_code(self):
        """导出Python代码"""
        # 打开文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出代码", "", "Python文件 (*.py)"
        )
        
        if not file_path:
            return
        
        try:
            # 生成Python代码
            code = self.generate_python_code()
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            self.statusBar.showMessage(f"代码已导出: {file_path}")
            QMessageBox.information(self, "成功", "代码导出成功！")
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出代码失败: {str(e)}")
    
    def generate_python_code(self):
        """生成Python代码，支持逻辑分支与函数关联"""
        code = ["#!/usr/bin/env python3", "# -*- coding: utf-8 -*-\n"]
        code.append("# 自动生成的机器人控制代码")
        code.append("\nimport time")
        code.append("\n# 初始化变量")
        
        # 添加变量初始化
        for name, var in self.variable_list.getAllVariables().items():
            code.append(f"{name} = {var.value!r}")
        
        code.append("\ndef main():")
        code.append("    \"\"\"主函数\"\"\"")
        
        # 构建连接图，用于确定执行顺序和分支关系
        # 执行流连接映射：from_node -> [to_nodes]
        execution_graph = {}
        # 数据流连接映射：to_node -> from_node
        data_graph = {}
        
        for conn in self.canvas.connections:
            # 判断连接类型
            if conn.from_node.value_type == "execution":
                # 执行流连接
                if (conn.from_block, conn.from_node.node_id) not in execution_graph:
                    execution_graph[(conn.from_block, conn.from_node.node_id)] = []
                execution_graph[(conn.from_block, conn.from_node.node_id)].append(
                    (conn.to_block, conn.to_node.node_id)
                )
            else:
                # 数据流连接
                data_graph[(conn.to_block, conn.to_node.node_id)] = (
                    conn.from_block, conn.from_node.node_id
                )
        
        # 定义块ID到索引的映射，用于递归查找
        block_to_index = {}
        for i, block in enumerate(self.canvas.blocks):
            block_to_index[block.id] = i
        
        # 生成代码的递归函数
        def generate_block_code(block_idx, indent_level=1):
            block = self.canvas.blocks[block_idx]
            indent = "    " * indent_level
            
            if block.type == 'logic':
                if block.name == '条件判断':
                    # 条件判断块
                    # 查找条件输入节点的值
                    condition_value = "True"
                    
                    # 先尝试从参数获取条件
                    for param in block.params:
                        if param.get('name') == '条件':
                            condition_value = param.get('value', 'True')
                    
                    # 检查是否有数据流连接到条件节点
                    found_connection = False
                    for node in block.input_nodes:
                        if node.value_type == "boolean" or node.value_type == "bool" or node.value_type == "data":
                            conn_key = (block_idx, node.node_id)
                            if conn_key in data_graph:
                                # 获取数据源
                                from_block_idx, from_node_id = data_graph[conn_key]
                                from_block = self.canvas.blocks[from_block_idx]
                                # 尝试获取节点对应的值或变量
                                # 使用有效的变量名格式
                                valid_var_name = from_block.name.lower().replace(" ", "_")
                                condition_value = f"{valid_var_name}_result"
                                found_connection = True
                                break
                        if found_connection:
                            break
                    
                    code.append(f"{indent}# 条件判断: {condition_value}")
                    code.append(f"{indent}if {condition_value}:")
                    
                    # 查找真分支的执行流连接
                    true_output_node = None
                    for node in block.output_nodes:
                        if node.name == "真" or node.name == "then":
                            true_output_node = node
                            break
                    
                    if true_output_node:
                        # 生成真分支的代码
                        true_connections = execution_graph.get((block_idx, true_output_node.node_id), [])
                        for to_block_idx, to_node_id in true_connections:
                            generate_block_code(to_block_idx, indent_level + 1)
                    else:
                        code.append(f"{indent}    pass")
                    
                    code.append(f"{indent}else:")
                    
                    # 查找假分支的执行流连接
                    false_output_node = None
                    for node in block.output_nodes:
                        if node.name == "假" or node.name == "else":
                            false_output_node = node
                            break
                    
                    if false_output_node:
                        # 生成假分支的代码
                        false_connections = execution_graph.get((block_idx, false_output_node.node_id), [])
                        for to_block_idx, to_node_id in false_connections:
                            generate_block_code(to_block_idx, indent_level + 1)
                    else:
                        code.append(f"{indent}    pass")
                
                elif block.name == '循环':
                    # 循环块
                    times = self._get_param_value(block, '次数')
                    code.append(f"{indent}# 循环 {times} 次")
                    code.append(f"{indent}for _ in range({times}):")
                    
                    # 查找循环体的执行流连接
                    body_output_node = None
                    for node in block.output_nodes:
                        if node.name == "循环体" or node.value_type == "execution":
                            body_output_node = node
                            break
                    
                    if body_output_node:
                        # 生成循环体的代码
                        body_connections = execution_graph.get((block_idx, body_output_node.node_id), [])
                        for to_block_idx, to_node_id in body_connections:
                            generate_block_code(to_block_idx, indent_level + 1)
                    else:
                        code.append(f"{indent}    pass")
            
            elif block.type == 'variable':
                if block.name == '变量赋值':
                    var_name = self._get_param_value(block, '变量名')
                    value = self._get_param_value(block, '值')
                    
                    # 检查是否有数据流连接到值节点
                    for node in block.input_nodes:
                        if node.name == "值" or node.value_type == "data":
                            conn_key = (block_idx, node.node_id)
                            if conn_key in data_graph:
                                from_block_idx, from_node_id = data_graph[conn_key]
                                from_block = self.canvas.blocks[from_block_idx]
                                # 使用数据源的值
                                value = f"{from_block.name}_result"
                                break
                    
                    code.append(f"{indent}# 变量赋值")
                    code.append(f"{indent}{var_name} = {value}")
                elif block.name == '变量增加':
                    var_name = self._get_param_value(block, '变量名')
                    increment = self._get_param_value(block, '增量')
                    code.append(f"{indent}# 变量增加")
                    code.append(f"{indent}{var_name} += {increment}")
                
                # 生成后续执行流连接的代码
                for node in block.output_nodes:
                    if node.value_type == "execution":
                        next_connections = execution_graph.get((block_idx, node.node_id), [])
                        for to_block_idx, to_node_id in next_connections:
                            generate_block_code(to_block_idx, indent_level)
            
            elif block.type == 'motor':
                # 电机控制块
                code.append(f"{indent}# {block.name}")
                
                if block.name == '前进':
                    speed = self._get_param_value(block, '速度')
                    duration = self._get_param_value(block, '时间')
                    code.append(f"{indent}# 控制机器人前进: 速度={speed}, 时间={duration}秒")
                    code.append(f"{indent}print(f'前进: 速度={{speed}}, 时间={{duration}}秒')")
                    code.append(f"{indent}time.sleep({duration})")
                elif block.name == '后退':
                    speed = self._get_param_value(block, '速度')
                    duration = self._get_param_value(block, '时间')
                    code.append(f"{indent}# 控制机器人后退: 速度={speed}, 时间={duration}秒")
                    code.append(f"{indent}print(f'后退: 速度={{speed}}, 时间={{duration}}秒')")
                    code.append(f"{indent}time.sleep({duration})")
                elif block.name == '左转':
                    speed = self._get_param_value(block, '速度')
                    angle = self._get_param_value(block, '角度')
                    code.append(f"{indent}# 控制机器人左转: 速度={speed}, 角度={angle}度")
                    code.append(f"{indent}print(f'左转: 速度={{speed}}, 角度={{angle}}度')")
                elif block.name == '右转':
                    speed = self._get_param_value(block, '速度')
                    angle = self._get_param_value(block, '角度')
                    code.append(f"{indent}# 控制机器人右转: 速度={speed}, 角度={angle}度")
                    code.append(f"{indent}print(f'右转: 速度={{speed}}, 角度={{angle}}度')")
                elif block.name == '停止':
                    code.append(f"{indent}# 停止所有电机")
                    code.append(f"{indent}print('停止')")
                
                # 生成后续执行流连接的代码
                for node in block.output_nodes:
                    if node.value_type == "execution":
                        next_connections = execution_graph.get((block_idx, node.node_id), [])
                        for to_block_idx, to_node_id in next_connections:
                            generate_block_code(to_block_idx, indent_level)
            
            elif block.type == 'sensor':
                # 传感器块
                code.append(f"{indent}# {block.name}")
                result_var = f"{block.name}_result"
                
                if block.name == '读取超声波':
                    code.append(f"{indent}# 读取超声波传感器")
                    code.append(f"{indent}# {result_var} = robot.get_ultrasonic_distance()")
                    code.append(f"{indent}{result_var} = 0  # 模拟传感器值")
                    code.append(f"{indent}print(f'距离: {{{result_var}}} cm')")
                elif block.name == '读取光线':
                    code.append(f"{indent}# 读取光线传感器")
                    code.append(f"{indent}# {result_var} = robot.get_light_level()")
                    code.append(f"{indent}{result_var} = 0  # 模拟传感器值")
                    code.append(f"{indent}print(f'亮度: {{{result_var}}}')")
                elif block.name == '读取声音':
                    code.append(f"{indent}# 读取声音传感器")
                    code.append(f"{indent}# {result_var} = robot.get_sound_level()")
                    code.append(f"{indent}{result_var} = 0  # 模拟传感器值")
                    code.append(f"{indent}print(f'音量: {{{result_var}}}')")
                
                # 生成后续执行流连接的代码
                for node in block.output_nodes:
                    if node.value_type == "execution":
                        next_connections = execution_graph.get((block_idx, node.node_id), [])
                        for to_block_idx, to_node_id in next_connections:
                            generate_block_code(to_block_idx, indent_level)
        
        # 找出起始块（没有输入执行流连接的块）
        start_blocks = []
        for i, block in enumerate(self.canvas.blocks):
            is_start = True
            # 检查是否有执行流连接到这个块的任何输入节点
            for node in block.input_nodes:
                if node.value_type == "execution":
                    # 检查是否有连接到这个节点
                    for conn in self.canvas.connections:
                        if conn.to_block == i and conn.to_node == node:
                            is_start = False
                            break
                    if not is_start:
                        break
            if is_start:
                start_blocks.append(i)
        
        # 如果没有找到起始块，按顺序处理所有块
        if not start_blocks:
            start_blocks = range(len(self.canvas.blocks))
        
        # 从起始块开始生成代码
        for block_idx in start_blocks:
            generate_block_code(block_idx)
        
        code.append("\nif __name__ == '__main__':")
        code.append("    main()")
        
        return "\n".join(code)
    
    def _get_param_value(self, block, param_name):
        """获取参数值"""
        for param in block.params:
            if param['name'] == param_name:
                return param.get('value', param.get('default', 0))
        return 0
    
    def run_program(self):
        """运行程序"""
        self.statusBar.showMessage("程序运行中...")
        
        # 实际实现中，这里应该将程序发送到机器人或模拟器执行
        # 现在只是简单的显示消息
        QMessageBox.information(self, "运行", "程序开始运行！")
        
        # 生成并显示Python代码
        code = self.generate_python_code()
        
        # 这里可以添加实际执行代码的逻辑
        
        self.statusBar.showMessage("程序运行完成")
    
    def stop_program(self):
        """停止程序"""
        self.statusBar.showMessage("程序已停止")
        QMessageBox.information(self, "停止", "程序已停止执行！")
    
    def clear_canvas(self):
        """清空画布"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空画布吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.clear()
            self.statusBar.showMessage("画布已清空")
    
    def closeEvent(self, event: QCloseEvent):
        """窗口关闭事件"""
        # 询问是否保存程序
        if self.canvas.blocks or self.canvas.connections:
            reply = QMessageBox.question(
                self, "确认", "是否保存当前程序？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.StandardButton.Yes:
                if not self.save_program():
                    event.ignore()
                    return
        
        # 保存设置
        self.save_settings()
        
        event.accept()