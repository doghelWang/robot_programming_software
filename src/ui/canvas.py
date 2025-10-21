#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
编程画布组件
"""

import json
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QDrag, QPixmap
from PyQt6.QtCore import Qt, QMimeData, QPoint, QRect, pyqtSignal
from typing import List, Optional, Tuple

from core.data_models import ProgramBlock, Connection, Node, NodeType


class ProgrammingCanvas(QWidget):
    """编程画布"""
    blockSelected = pyqtSignal(int)
    connectionCreated = pyqtSignal(Connection)
    variableUpdated = pyqtSignal(str, str)  # 变量名和变量类型
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blocks: List[ProgramBlock] = []
        self.connections: List[Connection] = []
        self.selected_block_index = -1
        self.is_dragging = False
        self.drag_start = QPoint()
        self.block_start = QPoint()
        self.drag_item = None
        self.drag_item_type = None
        self.drag_preview = None
        
        # 连接模式相关变量
        self.connection_mode = False
        self.source_node = None
        self.source_block_index = -1
        self.current_mouse_pos = QPoint()
        
        # 设置画布属性
        self.setMinimumSize(800, 600)
        self.setAcceptDrops(True)
        
        # 网格大小
        self.grid_size = 20
        
        # 节点半径
        self.node_radius = 6
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 绘制网格背景
        self._drawGrid(painter)
        
        # 绘制连接线
        self._drawConnections(painter)
        
        # 绘制程序块
        for i, block in enumerate(self.blocks):
            self._drawBlock(painter, block, i == self.selected_block_index)
        
        # 绘制拖拽预览
        if self.drag_preview:
            self._drawDragPreview(painter)
        
        # 绘制临时连接线（当处于连接模式时）
        if self.connection_mode and self.source_node:
            self._drawTempConnection(painter)
    
    def _drawGrid(self, painter):
        """绘制网格背景"""
        painter.setPen(QPen(QColor(220, 220, 220), 1))
        
        # 绘制垂直网格线
        for x in range(0, self.width(), self.grid_size):
            painter.drawLine(x, 0, x, self.height())
        
        # 绘制水平网格线
        for y in range(0, self.height(), self.grid_size):
            painter.drawLine(0, y, self.width(), y)
    
    def _drawBlock(self, painter, block, is_selected):
        """绘制程序块"""
        block_height = 80 + len(block.params) * 25
        block_rect = QRect(block.x, block.y, 200, block_height)
        
        # 设置块的颜色
        if is_selected:
            border_color = QColor(82, 196, 26)  # 选中状态的边框颜色
            border_width = 2
        else:
            # 根据块类型设置不同的背景色
            if block.type == 'logic':
                border_color = QColor(255, 128, 0)
            elif block.type == 'motor':
                border_color = QColor(255, 0, 0)
            elif block.type == 'sensor':
                border_color = QColor(0, 128, 128)
            else:
                border_color = QColor(24, 144, 255)
            border_width = 1
        
        # 绘制块背景
        painter.setPen(QPen(border_color, border_width))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRoundedRect(block_rect, 8, 8)
        
        # 绘制块标题
        painter.setPen(QPen(border_color, 1))
        painter.setFont(self.font())
        painter.drawText(block_rect.adjusted(10, 10, -10, -10), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, block.name)
        
        # 绘制参数
        for i, param in enumerate(block.params):
            y_pos = 40 + i * 25
            # 参数标签
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.drawText(QRect(block.x + 10, block.y + y_pos, 60, 20), 
                            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, f"{param['name']}:")
            # 参数值
            param_value = str(param.get('value', ''))
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawText(QRect(block.x + 70, block.y + y_pos, 120, 20), 
                            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, param_value)
        
        # 绘制输入输出节点
        self._drawNodes(painter, block_rect, block)
    
    def _drawNodes(self, painter, block_rect, block):
        """绘制输入输出节点"""
        # 计算节点位置
        input_node_y_positions = []
        output_node_y_positions = []
        
        # 逻辑块的特殊处理
        if block.type == 'logic':
            if block.name == '条件判断' or block.name == '如果' or block.name == '如果-否则':
                # 条件节点在顶部
                input_node_y_positions.append(block_rect.y() + 30)
                # 真分支输出节点
                output_node_y_positions.append(block_rect.y() + 40)
                # 假分支输出节点 (如果-否则块有)
                if block.name == '如果-否则' or block.name == '条件判断':
                    output_node_y_positions.append(block_rect.y() + block_rect.height() - 30)
            elif block.name == '循环' or block.name == '当条件满足时循环' or block.name == '无限循环':
                # 循环开始输入节点
                input_node_y_positions.append(block_rect.y() + 20)
                # 循环结束输入节点
                input_node_y_positions.append(block_rect.y() + block_rect.height() - 20)
                # 循环体输出节点
                output_node_y_positions.append(block_rect.y() + 60)
                # 循环完成输出节点
                output_node_y_positions.append(block_rect.y() + block_rect.height() - 20)
        else:
            # 普通块的节点位置
            node_count = max(len(block.input_nodes), len(block.output_nodes))
            step = block_rect.height() / (node_count + 1)
            
            for i in range(len(block.input_nodes)):
                input_node_y_positions.append(block_rect.y() + (i + 1) * step)
            
            for i in range(len(block.output_nodes)):
                output_node_y_positions.append(block_rect.y() + (i + 1) * step)
        
        # 绘制输入节点
        for i, node in enumerate(block.input_nodes):
            if i < len(input_node_y_positions):
                x = block_rect.left() - self.node_radius
                y = input_node_y_positions[i]
                
                # 检查节点是否已连接
                is_connected = node.connection is not None
                
                # 绘制节点
                painter.setBrush(QBrush(QColor(255, 0, 0) if is_connected else QColor(24, 144, 255)))
                painter.setPen(QPen(QColor(0, 0, 0), 1))
                painter.drawEllipse(QPoint(int(x), int(y)), self.node_radius, self.node_radius)
                
                # 绘制节点名称
                painter.drawText(QRect(int(x) - 80, int(y) - 10, 70, 20), 
                                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, node.name)
        
        # 绘制输出节点
        for i, node in enumerate(block.output_nodes):
            if i < len(output_node_y_positions):
                x = block_rect.right() + self.node_radius
                y = output_node_y_positions[i]
                
                # 检查节点是否已连接
                is_connected = node.connection is not None
                
                # 绘制节点
                painter.setBrush(QBrush(QColor(0, 255, 0) if is_connected else QColor(24, 144, 255)))
                painter.setPen(QPen(QColor(0, 0, 0), 1))
                painter.drawEllipse(QPoint(int(x), int(y)), self.node_radius, self.node_radius)
                
                # 绘制节点名称
                painter.drawText(QRect(int(x) + 15, int(y) - 10, 70, 20), 
                                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, node.name)
    
    def _drawConnections(self, painter):
        """绘制块之间的连接线，区分执行流和数据流连接"""
        for connection in self.connections:
            # 获取起始块和目标块
            from_block = self.blocks[connection.from_block]
            to_block = self.blocks[connection.to_block]
            
            # 计算起始节点位置
            from_x, from_y = self._get_node_position(from_block, connection.from_node)
            
            # 计算目标节点位置
            to_x, to_y = self._get_node_position(to_block, connection.to_node)
            
            # 根据连接类型设置不同的样式
            if hasattr(connection, 'type') and connection.type == 'execution':
                # 执行流连接：实心线，蓝色
                painter.setPen(QPen(QColor(24, 144, 255), 2))
            else:
                # 数据流连接：虚线，绿色
                painter.setPen(QPen(QColor(46, 204, 113), 2, Qt.PenStyle.DashLine))
            
            painter.drawLine(int(from_x), int(from_y), int(to_x), int(to_y))
    
    def _drawTempConnection(self, painter):
        """绘制临时连接线"""
        if not self.connection_mode or not self.source_node:
            return
        
        # 获取源节点位置
        source_block = self.blocks[self.source_block_index]
        source_x, source_y = self._get_node_position(source_block, self.source_node)
        
        # 绘制临时连接线
        painter.setPen(QPen(QColor(24, 144, 255), 2, Qt.PenStyle.DashLine))
        painter.drawLine(int(source_x), int(source_y), self.current_mouse_pos.x(), self.current_mouse_pos.y())
    
    def _drawDragPreview(self, painter):
        """绘制拖拽预览"""
        if not self.drag_item or not self.drag_preview:
            return
        
        block_rect = QRect(self.drag_preview.x(), self.drag_preview.y(), 200, 80 + len(self.drag_item.params) * 25)
        
        # 绘制半透明的预览块
        painter.setOpacity(0.5)
        painter.setPen(QPen(QColor(24, 144, 255), 2, Qt.PenStyle.DashLine))
        painter.setBrush(QBrush(QColor(24, 144, 255, 50)))
        painter.drawRoundedRect(block_rect, 8, 8)
        
        # 绘制块标题
        painter.setOpacity(0.7)
        painter.setPen(QPen(QColor(24, 144, 255), 1))
        painter.drawText(block_rect.adjusted(10, 10, -10, -10), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, self.drag_item.name)
        
        # 重置透明度
        painter.setOpacity(1.0)
    
    def _get_node_position(self, block: ProgramBlock, node: Node) -> Tuple[int, int]:
        """获取节点在画布上的位置"""
        block_rect = QRect(block.x, block.y, 200, 80 + len(block.params) * 25)
        
        # 逻辑块的特殊处理
        if block.type == 'logic':
            if block.name == '条件判断' or block.name == '如果' or block.name == '如果-否则':
                if node.node_id.endswith('_cond') or node.name == '条件':  # 条件输入节点
                    return block_rect.left() - self.node_radius, block_rect.y() + 30
                elif node.node_id.endswith('_true') or node.name == '真':  # 真分支输出节点
                    return block_rect.right() + self.node_radius, block_rect.y() + 40
                elif (node.node_id.endswith('_false') or node.name == '假') and \
                     (block.name == '如果-否则' or block.name == '条件判断'):  # 假分支输出节点
                    return block_rect.right() + self.node_radius, block_rect.y() + block_rect.height() - 30
            elif block.name == '循环' or block.name == '当条件满足时循环' or block.name == '无限循环':
                if node.node_id.endswith('_start') or node.name == '开始':  # 循环开始输入节点
                    return block_rect.left() - self.node_radius, block_rect.y() + 20
                elif node.node_id.endswith('_loop') or node.name == '循环体':  # 循环体输出节点
                    return block_rect.right() + self.node_radius, block_rect.y() + 60
                elif node.node_id.endswith('_end') or node.name == '结束':  # 循环结束输入节点
                    return block_rect.left() - self.node_radius, block_rect.y() + block_rect.height() - 20
                elif node.node_id.endswith('_done') or node.name == '完成':  # 循环完成输出节点
                    return block_rect.right() + self.node_radius, block_rect.y() + block_rect.height() - 20
        
        # 普通节点的处理
        if node in block.input_nodes:
            index = block.input_nodes.index(node)
            node_count = max(len(block.input_nodes), len(block.output_nodes))
            step = block_rect.height() / (node_count + 1)
            y = block_rect.y() + (index + 1) * step
            return block_rect.left() - self.node_radius, y
        elif node in block.output_nodes:
            index = block.output_nodes.index(node)
            node_count = max(len(block.input_nodes), len(block.output_nodes))
            step = block_rect.height() / (node_count + 1)
            y = block_rect.y() + (index + 1) * step
            return block_rect.right() + self.node_radius, y
        
        return 0, 0
    
    def _find_node_at_position(self, pos) -> Tuple[Optional[int], Optional[Node]]:
        """查找指定位置的节点"""
        # 确保pos是QPoint类型
        if hasattr(pos, 'x') and hasattr(pos, 'y'):
            # 转换QPointF到QPoint
            pos = QPoint(int(pos.x()), int(pos.y()))
            
        for i, block in enumerate(self.blocks):
            block_rect = QRect(block.x, block.y, 200, 80 + len(block.params) * 25)
            
            # 检查所有输入节点
            for node in block.input_nodes:
                node_x, node_y = self._get_node_position(block, node)
                node_rect = QRect(int(node_x) - self.node_radius, int(node_y) - self.node_radius,
                     self.node_radius * 2, self.node_radius * 2)
                if node_rect.contains(pos):
                    return i, node
            
            # 检查所有输出节点
            for node in block.output_nodes:
                node_x, node_y = self._get_node_position(block, node)
                node_rect = QRect(int(node_x) - self.node_radius, int(node_y) - self.node_radius,
                     self.node_radius * 2, self.node_radius * 2)
                if node_rect.contains(pos):
                    return i, node
        
        return None, None
    
    def connectNodes(self, from_node, to_node, from_block_idx, to_block_idx):
        """连接两个节点，支持逻辑分支与函数间执行流连接"""
        print(f"尝试连接节点: 源块={from_block_idx}, 源节点={from_node.name}, 目标块={to_block_idx}, 目标节点={to_node.name}")
        
        # 重要检查：不允许将output连接到另一个output
        if from_node.node_type == NodeType.OUTPUT and to_node.node_type == NodeType.OUTPUT:
            print("连接失败: 不允许将输出节点连接到另一个输出节点")
            return False
        
        # 支持两种类型的连接：
        # 1. 执行流连接：控制执行顺序（value_type为"execution"）
        # 2. 数据流连接：传递数据值（其他类型）
        
        # 检查连接类型匹配规则
        connection_valid = False
        connection_type = 'data'  # 默认是数据流连接
        
        # 执行流连接规则：execution类型节点可以连接到任何其他execution类型节点
        if from_node.value_type == "execution" and to_node.value_type == "execution":
            connection_valid = True
            connection_type = 'execution'
        # 数据流连接规则：数据类型必须匹配，或者源节点为变量/常量节点
        elif from_node.value_type == to_node.value_type:
            connection_valid = True
        # 特殊处理：布尔值节点也可以连接到布尔类型的条件输入
        elif ((from_node.value_type == "bool" and to_node.value_type == "boolean") or
              (from_node.value_type == "boolean" and to_node.value_type == "bool")):
            connection_valid = True
        # 特殊处理：变量节点可以连接到任何参数节点
        elif hasattr(from_node, 'variable'):
            # 变量节点可以连接到任何类型的参数节点
            connection_valid = True
        
        if not connection_valid:
            print(f"连接失败: 节点类型不匹配 {from_node.value_type} -> {to_node.value_type}")
            return False
        
        # 删除目标节点的旧连接（支持变量替换功能）
        for conn in self.connections[:]:
            if conn.to_node == to_node and conn.to_block == to_block_idx:
                print(f"清除目标节点的旧连接: {conn.from_node.name}")
                self.connections.remove(conn)
        
        # 检查是否已经存在相同的连接
        for conn in self.connections:
            if (conn.from_node == from_node and conn.to_node == to_node and
                conn.from_block == from_block_idx and conn.to_block == to_block_idx):
                print("连接失败: 连接已存在")
                return False
        
        # 创建新连接
        new_connection = Connection(
            from_block=from_block_idx,
            from_node=from_node,
            to_block=to_block_idx,
            to_node=to_node
        )
        # 添加连接类型属性
        new_connection.type = connection_type
        self.connections.append(new_connection)
        
        # 输出连接创建信息
        if connection_type == 'execution':
            print(f"执行流连接创建成功: 从块 {from_block_idx} 的节点 {from_node.node_id} 到块 {to_block_idx} 的节点 {to_node.node_id}")
        else:
            print(f"数据流连接创建成功: 从块 {from_block_idx} 的节点 {from_node.node_id} 到块 {to_block_idx} 的节点 {to_node.node_id}")
        
        self.update()
        return True
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        # 检查是否点击了节点
        pos = event.position()
        block_index, node = self._find_node_at_position(QPoint(int(pos.x()), int(pos.y())))
        if block_index is not None and node is not None:
            # 开始连接模式
            self.connection_mode = True
            self.source_node = node
            self.source_block_index = block_index
            self.update()
            return
        
        # 检查是否点击了程序块
        clicked_block = -1
        pos = event.position()
        mouse_pos = QPoint(int(pos.x()), int(pos.y()))
        for i, block in enumerate(self.blocks):
            block_rect = QRect(block.x, block.y, 200, 80 + len(block.params) * 25)
            if block_rect.contains(mouse_pos):
                clicked_block = i
                break
        
        if clicked_block >= 0:
            # 选择块
            self.selected_block_index = clicked_block
            self.blockSelected.emit(clicked_block)
            
            # 开始拖拽
            self.is_dragging = True
            self.drag_start = QPoint(int(pos.x()), int(pos.y()))
            self.block_start = QPoint(self.blocks[clicked_block].x, self.blocks[clicked_block].y)
        else:
            # 取消选择
            self.selected_block_index = -1
            self.blockSelected.emit(-1)
        
        self.update()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_dragging and self.selected_block_index >= 0:
            # 计算拖拽偏移
            pos = event.position()
            current_pos = QPoint(int(pos.x()), int(pos.y()))
            dx = current_pos.x() - self.drag_start.x()
            dy = current_pos.y() - self.drag_start.y()
            
            # 更新块位置（对齐到网格）
            new_x = self.block_start.x() + dx
            new_y = self.block_start.y() + dy
            
            # 对齐到网格
            new_x = round(new_x / self.grid_size) * self.grid_size
            new_y = round(new_y / self.grid_size) * self.grid_size
            
            # 确保块不超出边界
            new_x = max(0, new_x)
            new_y = max(0, new_y)
            
            # 更新块位置
            self.blocks[self.selected_block_index].x = new_x
            self.blocks[self.selected_block_index].y = new_y
            
            self.update()
        elif self.drag_preview:
            # 更新拖拽预览位置
            self.drag_preview.setX(round(event.position().x() / self.grid_size) * self.grid_size - 100)
            self.drag_preview.setY(round(event.position().y() / self.grid_size) * self.grid_size - 40)
            self.update()
        elif self.connection_mode:
            # 存储当前鼠标位置
            pos = event.position()
            self.current_mouse_pos = QPoint(int(pos.x()), int(pos.y()))
            # 在连接模式下，刷新画布以更新临时连接线
            self.update()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        # 处理连接模式
        if self.connection_mode and self.source_node:
            # 查找目标节点
            pos = event.position()
            target_block_index, target_node = self._find_node_at_position(QPoint(int(pos.x()), int(pos.y())))
            
            if target_block_index is not None and target_node is not None:
                # 调用connectNodes方法处理连接逻辑
                self.connectNodes(self.source_node, target_node, self.source_block_index, target_block_index)
            
            # 结束连接模式
            self.connection_mode = False
            self.source_node = None
            self.source_block_index = -1
        
        self.is_dragging = False
        self.update()
    
    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            
            # 更新拖拽预览位置
            if not self.drag_preview:
                self.drag_preview = QPoint()
            pos = event.position()
            self.drag_preview.setX(round(int(pos.x()) / self.grid_size) * self.grid_size - 100)
            self.drag_preview.setY(round(int(pos.y()) / self.grid_size) * self.grid_size - 40)
            self.update()
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.drag_preview = None
        self.update()
    
    def dropEvent(self, event):
        """放置事件，支持变量替换、变量赋值和函数输出连接"""
        print("处理拖拽放置事件...")
        if event.mimeData().hasText():
            # 获取拖拽的数据
            data_text = event.mimeData().text()
            
            try:
                # 解析拖拽的数据
                drag_data = json.loads(data_text)
                item_type = drag_data.get('type')
                item_data = drag_data.get('data')
                print(f"拖拽项目类型: {item_type}, 数据: {item_data}")
                
                # 检查是否拖拽到任何连接的目标节点位置（用于替换连接）
                pos = event.position()
                target_block_index, target_node = self._find_node_at_position(QPoint(int(pos.x()), int(pos.y())))
                print(f"目标块索引: {target_block_index}, 目标节点: {target_node}")
                
                # 获取源节点信息（如果从其他块拖拽）
                from_block_index, from_node = None, None
                for i, block in enumerate(self.blocks):
                    # 检查是否从输出节点拖拽
                    for node in block.output_nodes:
                        node_x, node_y = self._get_node_position(block, node)
                        node_rect = QRect(int(node_x) - self.node_radius, int(node_y) - self.node_radius,
                                         self.node_radius * 2, self.node_radius * 2)
                        pos = event.position()
                        if node_rect.contains(QPoint(int(pos.x()), int(pos.y()))):
                            from_block_index = i
                            from_node = node
                            print(f"源块索引: {from_block_index}, 源节点: {from_node}")
                            break
                
                # 处理变量替换和函数输出到变量的情况
                if item_type == 'variable' and target_node and target_node.node_type == NodeType.INPUT and target_node.value_type != 'execution':
                    print(f"将变量连接到输入节点: {item_data['name']} -> {target_node.name}")
                    # 尝试创建一个虚拟的变量输出节点用于连接
                    # 这里简化处理，直接创建连接
                    from_variable_node = Node(
                        name=f'var_{item_data["name"]}',
                        node_type=NodeType.OUTPUT,
                        value_type=item_data.get('type', 'unknown'),
                        node_id=f'var_{item_data["name"]}_output'
                    )
                    from_variable_node.variable = item_data['name']  # 标记为变量节点
                    
                    # 清除目标节点的旧连接
                    for conn in self.connections[:]:
                        if conn.to_node == target_node and conn.to_block == target_block_index:
                            self.connections.remove(conn)
                    
                    # 创建新连接
                    new_connection = Connection(
                        from_block=-1,  # 特殊标记，表示来自变量
                        from_node=from_variable_node,
                        to_block=target_block_index,
                        to_node=target_node
                    )
                    new_connection.type = 'data'
                    self.connections.append(new_connection)
                    self.update()
                    print(f"变量 {item_data['name']} 已连接到节点 {target_node.name}")
                    return
                
                if item_type == 'function':
                    # 创建新的程序块
                    pos = event.position()
                    new_block = ProgramBlock(
                        name=item_data['name'],
                        block_type=item_data['type'],  # 构造函数参数是block_type
                        x=round(int(pos.x()) / self.grid_size) * self.grid_size - 100,
                        y=round(int(pos.y()) / self.grid_size) * self.grid_size - 40,
                        params=item_data.get('params', [])
                    )
                    
                    # 对于逻辑块，确保有正确的输入输出节点
                    if new_block.type == 'logic':
                        # 根据逻辑块类型设置相应的节点
                        if new_block.name == '条件判断' or new_block.name == '如果':
                            new_block.input_nodes = [Node(name='条件', node_type=NodeType.INPUT, value_type='boolean', node_id='cond_input')]
                            new_block.output_nodes = [
                                Node(name='真', node_type=NodeType.OUTPUT, value_type='execution', node_id='true_output'),
                                Node(name='假', node_type=NodeType.OUTPUT, value_type='execution', node_id='false_output')
                            ]
                        elif new_block.name == '如果-否则':
                            new_block.input_nodes = [Node(name='条件', node_type=NodeType.INPUT, value_type='boolean', node_id='cond_input')]
                            new_block.output_nodes = [
                                Node(name='真', node_type=NodeType.OUTPUT, value_type='execution', node_id='true_output'),
                                Node(name='假', node_type=NodeType.OUTPUT, value_type='execution', node_id='false_output')
                            ]
                        elif new_block.name in ['循环', '当条件满足时循环', '无限循环']:
                            new_block.input_nodes = [
                                Node(name='开始', node_type=NodeType.INPUT, value_type='execution', node_id='start_input'),
                                Node(name='结束', node_type=NodeType.INPUT, value_type='execution', node_id='end_input')
                            ]
                            new_block.output_nodes = [
                                Node(name='循环体', node_type=NodeType.OUTPUT, value_type='execution', node_id='loop_output'),
                                Node(name='完成', node_type=NodeType.OUTPUT, value_type='execution', node_id='done_output')
                            ]
                    
                    self.blocks.append(new_block)
                    
                    # 选中新创建的块
                    self.selected_block_index = len(self.blocks) - 1
                    self.blockSelected.emit(self.selected_block_index)
                elif item_type == 'variable':
                    # 检查是否拖拽到参数位置
                    # 遍历所有块，检查是否拖拽到块的参数区域
                    pos = event.position()
                    mouse_x = int(pos.x())
                    mouse_y = int(pos.y())
                    
                    for block_idx, block in enumerate(self.blocks):
                        # 计算完整的块高度，包括所有参数
                        block_height = 80 + len(block.params) * 25
                        block_rect = QRect(block.x, block.y, 200, block_height)
                        
                        if block_rect.contains(int(mouse_x), int(mouse_y)):
                            # 计算参数区域的位置
                            param_y_offset = 40  # 参数区域的起始Y坐标偏移
                            param_height = 25   # 每个参数的高度
                            
                            # 遍历块的参数 - 支持变量替换功能
                            for param_idx, param in enumerate(block.params):
                                param_y = block.y + param_y_offset + param_idx * param_height
                                # 参数值区域，更精确的定位
                                param_value_rect = QRect(block.x + 70, param_y - 10, 120, 20)
                                
                                # 如果鼠标在参数值区域内，将变量绑定到该参数（支持替换）
                                if param_value_rect.contains(int(mouse_x), int(mouse_y)):
                                    # 设置参数值为变量名，并标记为变量引用
                                    block.params[param_idx]['value'] = item_data['name']
                                    block.params[param_idx]['is_variable'] = True
                                    block.params[param_idx]['variable_type'] = item_data.get('type', 'unknown')
                                    self.selected_block_index = block_idx
                                    self.blockSelected.emit(block_idx)
                                    self.update()
                                    print(f"参数已替换为变量: {item_data['name']}")
                                    return
                            
                            # 检查是否拖拽到条件输入节点区域（针对逻辑块）
                            if block.type == 'logic' and mouse_x < block.x + 30 and len(block.input_nodes) > 0:
                                # 检查是否是条件输入节点
                                for node in block.input_nodes:
                                    if node.name == '条件' and node.value_type == 'boolean':
                                        # 为条件创建一个参数或更新现有参数（支持替换）
                                        condition_param_exists = False
                                        for param in block.params:
                                            if param['name'] == '条件':
                                                param['value'] = item_data['name']
                                                param['is_variable'] = True
                                                param['variable_type'] = item_data.get('type', 'unknown')
                                                condition_param_exists = True
                                                print(f"条件变量已替换为: {item_data['name']}")
                                                break
                                        
                                        if not condition_param_exists:
                                            block.params.append({
                                                'name': '条件',
                                                'type': 'boolean',
                                                'value': item_data['name'],
                                                'is_variable': True,
                                                'variable_type': item_data.get('type', 'unknown')
                                            })
                                        
                                        self.selected_block_index = block_idx
                                        self.blockSelected.emit(block_idx)
                                        self.update()
                                        return
                    
                # 处理从函数输出节点拖拽到变量上（函数输出赋值给变量）
                if from_node and from_node.node_type == NodeType.OUTPUT and from_node.value_type != 'execution' and item_type == 'variable':
                    print(f"处理函数输出赋值给变量: {from_block_index}.{from_node.name} -> {item_data['name']}")
                    # 确保不会尝试连接两个输出节点
                    if target_node and target_node.node_type == NodeType.OUTPUT:
                        print("连接失败: 不允许将输出节点连接到另一个输出节点")
                        return
                    
                    # 创建一个特殊的变量输入节点
                    to_variable_node = Node(
                        name=f'var_{item_data["name"]}',
                        node_type=NodeType.INPUT,
                        value_type=from_node.value_type,  # 使用函数输出的类型作为变量类型
                        node_id=f'var_{item_data["name"]}_input'
                    )
                    to_variable_node.variable = item_data['name']
                    
                    # 创建连接，表示将函数输出赋值给变量
                    new_connection = Connection(
                        from_block=from_block_index,
                        from_node=from_node,
                        to_block=-1,  # 特殊标记，表示指向变量
                        to_node=to_variable_node
                    )
                    new_connection.type = 'data'
                    
                    # 清除与该变量相关的旧连接
                    for conn in self.connections[:]:
                        if hasattr(conn.to_node, 'variable') and conn.to_node.variable == item_data['name']:
                            print(f"清除变量旧连接: {conn.from_node.name} -> {conn.to_node.variable}")
                            self.connections.remove(conn)
                    
                    # 添加新连接
                    self.connections.append(new_connection)
                    # 发送变量更新信号
                    self.variableUpdated.emit(item_data['name'], from_node.value_type)
                    self.update()
                    print(f"函数输出已连接到变量: {from_node.name} -> {item_data['name']}")
                    return
                
            except json.JSONDecodeError:
                pass
            
            # 清除拖拽预览
            self.drag_preview = None
            self.update()
    
    def addBlock(self, block: ProgramBlock):
        """添加程序块"""
        self.blocks.append(block)
        self.update()
    
    def removeSelectedBlock(self):
        """移除选中的程序块"""
        if self.selected_block_index >= 0:
            # 移除相关的连接
            self.connections = [conn for conn in self.connections 
                              if conn.from_block != self.selected_block_index 
                              and conn.to_block != self.selected_block_index]
            
            # 更新连接索引
            for conn in self.connections:
                if conn.from_block > self.selected_block_index:
                    conn.from_block -= 1
                if conn.to_block > self.selected_block_index:
                    conn.to_block -= 1
            
            # 移除块
            self.blocks.pop(self.selected_block_index)
            self.selected_block_index = -1
            self.blockSelected.emit(-1)
            self.update()
    
    def clear(self):
        """清空画布"""
        self.blocks = []
        self.connections = []
        self.selected_block_index = -1
        self.update()
    
    def setDragItem(self, item_type, item_data):
        """设置拖拽项"""
        self.drag_item_type = item_type
        self.drag_item = item_data