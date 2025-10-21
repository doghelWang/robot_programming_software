#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码生成器
"""

from typing import List, Dict, Any
from core.data_models import ProgramBlock, Connection, Variable


class PythonCodeGenerator:
    """Python代码生成器"""
    
    def __init__(self):
        self.indent_level = 0
        self.indent_str = "    "
    
    def generate_code(self, blocks: List[ProgramBlock], connections: List[Connection], variables: Dict[str, Variable]) -> str:
        """生成完整的Python代码"""
        code = []
        
        # 添加文件头部
        code.extend(self._generate_header())
        
        # 添加导入语句
        code.extend(self._generate_imports())
        
        # 添加变量初始化
        code.extend(self._generate_variable_initialization(variables))
        
        # 添加主函数
        code.extend(self._generate_main_function())
        
        # 生成程序逻辑
        code.extend(self._generate_program_logic(blocks, connections))
        
        # 添加主函数调用
        code.extend(self._generate_main_call())
        
        return "\n".join(code)
    
    def _generate_header(self) -> List[str]:
        """生成文件头部注释"""
        return [
            "#!/usr/bin/env python3",
            "# -*- coding: utf-8 -*-",
            "",
            "# 自动生成的机器人控制代码",
            "# 由机器人编程软件生成",
            ""
        ]
    
    def _generate_imports(self) -> List[str]:
        """生成导入语句"""
        return [
            "import time",
            "# 导入机器人控制库",
            "# from robot_lib import Robot",
            ""
        ]
    
    def _generate_variable_initialization(self, variables: Dict[str, Variable]) -> List[str]:
        """生成变量初始化代码"""
        if not variables:
            return []
        
        code = ["# 初始化变量"]
        
        for name, var in variables.items():
            # 根据变量类型生成不同的初始化代码
            if var.value_type == "string":
                code.append(f'{name} = "{var.value}"')
            else:
                code.append(f'{name} = {var.value!r}')
        
        code.append("")
        return code
    
    def _generate_main_function(self) -> List[str]:
        """生成主函数定义"""
        return [
            "def main():",
            f"{self.indent_str}\"\"\"主函数\"\"\"",
            # 添加机器人初始化代码
            f"{self.indent_str}# 初始化机器人",
            f"{self.indent_str}# robot = Robot()",
            f"{self.indent_str}print('机器人程序开始执行...')",
            ""
        ]
    
    def _generate_main_call(self) -> List[str]:
        """生成主函数调用代码"""
        return [
            "",
            "if __name__ == '__main__':",
            f"{self.indent_str}main()"
        ]
    
    def _generate_program_logic(self, blocks: List[ProgramBlock], connections: List[Connection]) -> List[str]:
        """生成程序逻辑代码"""
        code = []
        
        # 分析连接关系，构建执行流程图
        execution_graph = self._build_execution_graph(blocks, connections)
        
        # 生成代码
        self.indent_level = 1  # 主函数内的缩进级别
        
        # 按顺序生成块的代码
        # 注意：这是一个简化版本，实际应该根据执行图生成更复杂的控制流
        for block in blocks:
            code.extend(self._generate_block_code(block, execution_graph))
        
        # 添加结束消息
        code.append(f"{self.indent_str}print('机器人程序执行完成')")
        
        return code
    
    def _build_execution_graph(self, blocks: List[ProgramBlock], connections: List[Connection]) -> Dict[int, List[int]]:
        """构建执行流程图"""
        graph = {}
        
        # 初始化每个块的后继列表
        for i in range(len(blocks)):
            graph[i] = []
        
        # 根据连接构建执行流程
        for conn in connections:
            # 这里简化处理，实际应该根据节点类型和连接关系确定执行流程
            # 特别是对于逻辑块，需要处理分支逻辑
            graph[conn.from_block].append(conn.to_block)
        
        return graph
    
    def _generate_block_code(self, block: ProgramBlock, execution_graph: Dict[int, List[int]]) -> List[str]:
        """生成单个块的代码"""
        code = []
        
        # 添加块注释
        code.append(f"{self.indent_str}\n{self.indent_str}# {block.name}")
        
        # 根据块类型生成不同的代码
        if block.type == 'motor':
            code.extend(self._generate_motor_block_code(block))
        elif block.type == 'sensor':
            code.extend(self._generate_sensor_block_code(block))
        elif block.type == 'logic':
            code.extend(self._generate_logic_block_code(block, execution_graph))
        elif block.type == 'variable':
            code.extend(self._generate_variable_block_code(block))
        
        return code
    
    def _generate_motor_block_code(self, block: ProgramBlock) -> List[str]:
        """生成电机控制块代码"""
        code = []
        
        if block.name == '前进':
            speed = self._get_param_value(block, '速度')
            duration = self._get_param_value(block, '时间')
            code.append(f"{self.indent_str}# 控制机器人前进")
            code.append(f"{self.indent_str}# robot.move_forward(speed={speed})")
            code.append(f"{self.indent_str}print(f'前进: 速度={{speed}}, 时间={{duration}}秒')")
            code.append(f"{self.indent_str}time.sleep({duration})")
            code.append(f"{self.indent_str}# robot.stop()")
            code.append(f"{self.indent_str}print('停止')")
        
        elif block.name == '后退':
            speed = self._get_param_value(block, '速度')
            duration = self._get_param_value(block, '时间')
            code.append(f"{self.indent_str}# 控制机器人后退")
            code.append(f"{self.indent_str}# robot.move_backward(speed={speed})")
            code.append(f"{self.indent_str}print(f'后退: 速度={{speed}}, 时间={{duration}}秒')")
            code.append(f"{self.indent_str}time.sleep({duration})")
            code.append(f"{self.indent_str}# robot.stop()")
            code.append(f"{self.indent_str}print('停止')")
        
        elif block.name == '左转':
            speed = self._get_param_value(block, '速度')
            angle = self._get_param_value(block, '角度')
            code.append(f"{self.indent_str}# 控制机器人左转")
            code.append(f"{self.indent_str}# robot.turn_left(angle={angle}, speed={speed})")
            code.append(f"{self.indent_str}print(f'左转: 角度={{angle}}度, 速度={{speed}}')")
            code.append(f"{self.indent_str}time.sleep({angle / 90})  # 简单估算时间")
            code.append(f"{self.indent_str}# robot.stop()")
            code.append(f"{self.indent_str}print('停止')")
        
        elif block.name == '右转':
            speed = self._get_param_value(block, '速度')
            angle = self._get_param_value(block, '角度')
            code.append(f"{self.indent_str}# 控制机器人右转")
            code.append(f"{self.indent_str}# robot.turn_right(angle={angle}, speed={speed})")
            code.append(f"{self.indent_str}print(f'右转: 角度={{angle}}度, 速度={{speed}}')")
            code.append(f"{self.indent_str}time.sleep({angle / 90})  # 简单估算时间")
            code.append(f"{self.indent_str}# robot.stop()")
            code.append(f"{self.indent_str}print('停止')")
        
        elif block.name == '停止':
            code.append(f"{self.indent_str}# 停止所有电机")
            code.append(f"{self.indent_str}# robot.stop()")
            code.append(f"{self.indent_str}print('停止所有电机')")
        
        return code
    
    def _generate_sensor_block_code(self, block: ProgramBlock) -> List[str]:
        """生成传感器块代码"""
        code = []
        
        if block.name == '读取超声波':
            code.append(f"{self.indent_str}# 读取超声波传感器距离")
            code.append(f"{self.indent_str}# distance = robot.get_ultrasonic_distance()")
            code.append(f"{self.indent_str}distance = 0  # 模拟传感器值")
            code.append(f"{self.indent_str}print(f'超声波距离: {{distance}} cm')")
        
        elif block.name == '读取光线':
            code.append(f"{self.indent_str}# 读取光线传感器亮度")
            code.append(f"{self.indent_str}# brightness = robot.get_light_level()")
            code.append(f"{self.indent_str}brightness = 0  # 模拟传感器值")
            code.append(f"{self.indent_str}print(f'光线亮度: {{brightness}}')")
        
        elif block.name == '读取声音':
            code.append(f"{self.indent_str}# 读取声音传感器音量")
            code.append(f"{self.indent_str}# volume = robot.get_sound_level()")
            code.append(f"{self.indent_str}volume = 0  # 模拟传感器值")
            code.append(f"{self.indent_str}print(f'声音音量: {{volume}}')")
        
        return code
    
    def _generate_logic_block_code(self, block: ProgramBlock, execution_graph: Dict[int, List[int]]) -> List[str]:
        """生成逻辑块代码"""
        code = []
        
        if block.name == '条件判断':
            condition = self._get_param_value(block, '条件', default='True')
            code.append(f"{self.indent_str}# 条件判断")
            code.append(f"{self.indent_str}if {condition}:")
            
            # 增加缩进级别
            self.indent_level += 1
            
            # 生成真分支代码
            # 这里简化处理，实际应该根据连接关系生成真分支的执行代码
            code.append(f"{self.indent_str * self.indent_level}print('条件为真')")
            # TODO: 根据连接关系生成真分支的执行代码
            
            # 减少缩进级别
            self.indent_level -= 1
            
            code.append(f"{self.indent_str}else:")
            
            # 增加缩进级别
            self.indent_level += 1
            
            # 生成假分支代码
            code.append(f"{self.indent_str * self.indent_level}print('条件为假')")
            # TODO: 根据连接关系生成假分支的执行代码
            
            # 减少缩进级别
            self.indent_level -= 1
        
        elif block.name == '循环':
            times = self._get_param_value(block, '次数', default=1)
            code.append(f"{self.indent_str}# 循环 {times} 次")
            code.append(f"{self.indent_str}for _ in range({times}):")
            
            # 增加缩进级别
            self.indent_level += 1
            
            # 生成循环体代码
            # TODO: 根据连接关系生成循环体的执行代码
            code.append(f"{self.indent_str * self.indent_level}print('循环执行')")
            # 这里可以添加根据连接关系生成的循环体代码
            
            # 减少缩进级别
            self.indent_level -= 1
        
        return code
    
    def _generate_variable_block_code(self, block: ProgramBlock) -> List[str]:
        """生成变量操作块代码"""
        code = []
        
        if block.name == '变量赋值':
            var_name = self._get_param_value(block, '变量名', default='var')
            value = self._get_param_value(block, '值', default='0')
            code.append(f"{self.indent_str}# 变量赋值")
            code.append(f"{self.indent_str}{var_name} = {value}")
            code.append(f"{self.indent_str}print(f'赋值: {{var_name}} = {{value}}')")
        
        elif block.name == '变量增加':
            var_name = self._get_param_value(block, '变量名', default='var')
            increment = self._get_param_value(block, '增量', default='1')
            code.append(f"{self.indent_str}# 变量增加")
            code.append(f"{self.indent_str}{var_name} += {increment}")
            code.append(f"{self.indent_str}print(f'增加: {{var_name}} += {{increment}}')")
        
        return code
    
    def _get_param_value(self, block: ProgramBlock, param_name: str, default: Any = None) -> Any:
        """获取参数值"""
        for param in block.params:
            if param.get('name') == param_name:
                return param.get('value', param.get('default', default))
        return default


class ExecutionSimulator:
    """程序执行模拟器"""
    
    def __init__(self):
        self.variables = {}
        self.output = []
    
    def execute(self, blocks: List[ProgramBlock], connections: List[Connection], initial_variables: Dict[str, Variable]):
        """执行程序"""
        # 初始化变量
        for name, var in initial_variables.items():
            self.variables[name] = var.value
        
        # 构建执行流程图
        execution_graph = self._build_execution_graph(blocks, connections)
        
        # 开始执行
        self._execute_block(0, blocks, execution_graph)
        
        return self.output
    
    def _execute_block(self, block_index: int, blocks: List[ProgramBlock], execution_graph: Dict[int, List[int]]):
        """执行单个块"""
        if block_index >= len(blocks):
            return
        
        block = blocks[block_index]
        
        # 执行块
        result = self._execute_block_logic(block)
        
        # 根据块类型和结果决定下一步执行
        if block.type == 'logic' and block.name == '条件判断':
            # 条件判断块的特殊处理
            condition_result = result.get('condition', True)
            next_blocks = execution_graph.get(block_index, [])
            
            if next_blocks:
                # 简单处理：如果有连接，选择第一个作为真分支，第二个作为假分支
                if condition_result and len(next_blocks) >= 1:
                    self._execute_block(next_blocks[0], blocks, execution_graph)
                elif not condition_result and len(next_blocks) >= 2:
                    self._execute_block(next_blocks[1], blocks, execution_graph)
        else:
            # 普通块的处理
            next_blocks = execution_graph.get(block_index, [])
            for next_block in next_blocks:
                self._execute_block(next_block, blocks, execution_graph)
    
    def _execute_block_logic(self, block: ProgramBlock) -> Dict[str, Any]:
        """执行块的逻辑"""
        result = {}
        
        if block.type == 'motor':
            self.output.append(f"执行电机控制: {block.name}")
        elif block.type == 'sensor':
            self.output.append(f"执行传感器读取: {block.name}")
        elif block.type == 'logic':
            if block.name == '条件判断':
                condition = self._get_param_value(block, '条件', default='True')
                # 简单的表达式求值
                try:
                    # 使用变量字典作为局部变量进行求值
                    condition_result = eval(condition, {}, self.variables)
                    result['condition'] = condition_result
                    self.output.append(f"执行条件判断: {condition} -> {condition_result}")
                except:
                    result['condition'] = False
                    self.output.append(f"条件表达式错误: {condition}")
            elif block.name == '循环':
                times = self._get_param_value(block, '次数', default=1)
                self.output.append(f"执行循环: {times} 次")
        elif block.type == 'variable':
            if block.name == '变量赋值':
                var_name = self._get_param_value(block, '变量名', default='var')
                value_expr = self._get_param_value(block, '值', default='0')
                # 尝试求值表达式
                try:
                    value = eval(value_expr, {}, self.variables)
                    self.variables[var_name] = value
                    self.output.append(f"执行变量赋值: {var_name} = {value}")
                except:
                    # 如果求值失败，直接使用字符串值
                    self.variables[var_name] = value_expr
                    self.output.append(f"执行变量赋值: {var_name} = '{value_expr}'")
            elif block.name == '变量增加':
                var_name = self._get_param_value(block, '变量名', default='var')
                increment = self._get_param_value(block, '增量', default='1')
                # 确保变量存在
                if var_name not in self.variables:
                    self.variables[var_name] = 0
                # 尝试求值增量
                try:
                    inc_value = eval(str(increment), {}, self.variables)
                    self.variables[var_name] += inc_value
                    self.output.append(f"执行变量增加: {var_name} += {inc_value}")
                except:
                    self.output.append(f"变量增加失败: {var_name} += {increment}")
        
        return result
    
    def _build_execution_graph(self, blocks: List[ProgramBlock], connections: List[Connection]) -> Dict[int, List[int]]:
        """构建执行流程图"""
        graph = {}
        
        # 初始化每个块的后继列表
        for i in range(len(blocks)):
            graph[i] = []
        
        # 根据连接构建执行流程
        for conn in connections:
            graph[conn.from_block].append(conn.to_block)
        
        return graph
    
    def _get_param_value(self, block: ProgramBlock, param_name: str, default: Any = None) -> Any:
        """获取参数值"""
        for param in block.params:
            if param.get('name') == param_name:
                return param.get('value', param.get('default', default))
        return default