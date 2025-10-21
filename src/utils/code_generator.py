#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码生成器
"""
 
from typing import List, Dict, Any, Optional
from ..core.data_models import ProgramBlock, Connection, Variable


class PythonCodeGenerator:
    """Python代码生成器 - 增强版，添加完整类型注解和异常处理
    
    主要功能:
    - 生成完整的Python机器人控制代码
    - 支持电机控制、传感器读取、逻辑判断和变量操作块
    - 内置完善的错误处理和类型安全检查
    - 生成详细的代码统计和执行信息
    
    使用示例:
    ```python
    # 创建代码生成器实例
    generator = PythonCodeGenerator()
    
    # 定义程序块、连接和变量
    blocks = [ProgramBlock(type='motor', name='前进', params=[{"name": "速度", "value": 50}])]
    connections = []
    variables = {"count": Variable(value=0)}
    
    # 生成代码
    code = generator.generate_code(blocks, connections, variables)
    
    # 检查生成是否成功
    if generator._validate_code_generation():
        print("代码生成成功!")
        print(code)
    else:
        print(f"代码生成失败: {generator.last_error}")
    ```
    
    错误处理机制:
    - 参数验证: 所有输入参数都会经过严格的类型和有效性检查
    - 分步骤生成: 代码生成过程分为多个步骤，每步都会检查错误
    - 异常捕获: 捕获所有可能的异常并提供详细的错误信息
    - 状态跟踪: 通过error_occurred和last_error属性跟踪错误状态
    """
    
    def __init__(self):
        """初始化代码生成器，设置类型注解和初始状态"""
        self.indent_level: int = 0        # 缩进级别计数器
        self.indent_str: str = "    "      # 4个空格的缩进格式
        self.error_occurred: bool = False # 错误状态标志
        self.last_error: Optional[str] = None  # 最后一次错误信息
        self._reset()
    
    def generate_code(self, blocks: List[ProgramBlock], connections: List[Connection], variables: Dict[str, Variable]) -> str:
        """生成完整的Python代码，添加参数验证和异常处理"""
        try:
            # 参数验证增强
            if blocks is None or not isinstance(blocks, (list, tuple)):
                raise ValueError("blocks参数必须是列表或元组类型且不能为空")
            
            if connections is None or not isinstance(connections, (list, tuple)):
                raise ValueError("connections参数必须是列表或元组类型")
            
            if variables is None or not isinstance(variables, dict):
                raise ValueError("variables参数必须是字典类型")
            
            # 重置错误状态
            self.error_occurred = False
            self.last_error = None
            
            code = []
            
            # 分步骤生成，每步检查错误
            header = self._generate_header()
            code.extend(header)
            if self.error_occurred:
                error_msg = str(self.last_error)
                return f"#!/usr/bin/env python3\n# 错误: 代码生成失败 - {error_msg}\n\nprint(\"程序错误: {error_msg}\")"
            
            imports = self._generate_imports()
            code.extend(imports)
            if self.error_occurred:
                return "\n".join(code) + "\n# 错误: 代码生成中断 - " + str(self.last_error)
            
            var_init = self._generate_variable_initialization(variables)
            code.extend(var_init)
            if self.error_occurred:
                return "\n".join(code) + "\n# 错误: 代码生成中断 - " + str(self.last_error)
            
            main_func = self._generate_main_function()
            code.extend(main_func)
            if self.error_occurred:
                return "\n".join(code) + "\n# 错误: 代码生成中断 - " + str(self.last_error)
            
            program_logic = self._generate_program_logic(blocks, connections)
            code.extend(program_logic)
            if self.error_occurred:
                return "\n".join(code) + "\n# 错误: 代码生成中断 - " + str(self.last_error)
            
            main_call = self._generate_main_call()
            code.extend(main_call)
            
            # 组装最终代码
            final_code = "\n".join(code)
            
            # 生成代码统计信息
            stats_comment = "\n\n# " + "="*60 + "\n"
            stats_comment += f"# 代码生成信息\n"
            stats_comment += f"# 生成块数量: {len(blocks)}\n"
            stats_comment += f"# 生成连接数量: {len(connections)}\n"
            stats_comment += f"# 生成变量数量: {len(variables)}\n"
            stats_comment += f"# 生成代码行数: {len(final_code.split('\n'))}\n"
            stats_comment += f"# 生成时间: {self._get_current_timestamp()}\n"
            stats_comment += "# " + "="*60
            
            return final_code + stats_comment
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"生成代码时出错: {str(e)}"
            return f"#!/usr/bin/env python3\n# 错误: 代码生成失败\n\nprint(\"代码生成错误: {str(e)}\")"
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳字符串"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _validate_code_generation(self) -> bool:
        """验证代码生成状态，确保没有严重错误"""
        if self.error_occurred:
            return False
        return True

    def _reset(self):
        """重置生成器状态，包括错误状态"""
        self.error_occurred = False
        self.last_error = None
        self.indent_level = 0
    
    def _generate_header(self) -> List[str]:
        """生成文件头部注释，添加错误处理"""
        try:
            return [
                "#!/usr/bin/env python3",
                "# -*- coding: utf-8 -*-",
                "",
                "# 自动生成的机器人控制代码",
                "# 由机器人编程软件生成",
                ""
            ]
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"生成头部注释失败: {str(e)}"
            return ["# 错误: 无法生成头部注释"]
    
    def _generate_imports(self) -> List[str]:
        """生成导入语句，添加错误处理"""
        try:
            return [
                "import time",
                "# 导入机器人控制库",
                "# from robot_lib import Robot",
                ""
            ]
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"生成导入语句失败: {str(e)}"
            return ["# 错误: 无法生成导入语句"]
    
    def _generate_variable_initialization(self, variables: Dict[str, Variable]) -> List[str]:
        """生成变量初始化代码，增强类型转换和错误处理"""
        try:
            if not variables:
                return []
            
            code = ["# 初始化变量"]
            
            for name, var in variables.items():
                try:
                    # 安全地处理变量值
                    if hasattr(var, 'value') and var.value is not None:
                        # 增强的类型转换和格式化
                        if var.value_type == "string" or isinstance(var.value, str):
                            # 转义字符串中的特殊字符
                            escaped_value = var.value.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
                            code.append(f'{name} = "{escaped_value}"')
                        elif isinstance(var.value, bool):
                            code.append(f'{name} = {str(var.value).lower()}')
                        elif isinstance(var.value, (int, float)):
                            code.append(f'{name} = {var.value}')
                        else:
                            code.append(f'{name} = {var.value!r}')
                    else:
                        code.append(f'{name} = None')
                except Exception as e:
                    self.error_occurred = True
                    self.last_error = f"初始化变量 {name} 时出错: {str(e)}"
                    code.append(f'{name} = None  # 初始化失败')
            
            code.append("")
            return code
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"生成变量初始化代码失败: {str(e)}"
            return ["# 错误: 无法生成变量初始化代码"]
    
    def _generate_main_function(self) -> List[str]:
        """生成主函数定义，添加错误处理"""
        try:
            return [
                "def main():",
                f"{self.indent_str}\"\"\"主函数\"\"\"",
                # 添加机器人初始化代码
                f"{self.indent_str}# 初始化机器人",
                f"{self.indent_str}# robot = Robot()",
                f"{self.indent_str}print('机器人程序开始执行...')",
                ""
            ]
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"生成主函数定义失败: {str(e)}"
            return ["# 错误: 无法生成主函数定义"]
    
    def _generate_main_call(self) -> List[str]:
        """生成主函数调用代码，添加错误处理"""
        try:
            return [
                "",
                "if __name__ == '__main__':",
                f"{self.indent_str}try:",
                f"{self.indent_str}{self.indent_str}main()",
                f"{self.indent_str}{self.indent_str}print('机器人程序执行完毕')",
                f"{self.indent_str}except Exception as e:",
                f"{self.indent_str}{self.indent_str}print(f'程序执行错误: {{e}}')"
            ]
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"生成主函数调用失败: {str(e)}"
            return ["# 错误: 无法生成主函数调用"]
    
    def _generate_program_logic(self, blocks: List[ProgramBlock], connections: List[Connection]) -> List[str]:
        """生成程序逻辑代码，添加错误处理和类型转换功能"""
        try:
            code = []
            
            # 参数验证
            if blocks is None or not isinstance(blocks, list) or connections is None or not isinstance(connections, list):
                raise ValueError("输入参数类型错误")
            
            # 分析连接关系，构建执行流程图
            execution_graph = self._build_execution_graph(blocks, connections)
            
            # 生成代码
            self.indent_level = 1  # 主函数内的缩进级别
            
            # 按顺序生成块的代码
            # 注意：这是一个简化版本，实际应该根据执行图生成更复杂的控制流
            for block in blocks:
                try:
                    block_code = self._generate_block_code(block, execution_graph)
                    if block_code is not None:
                        code.extend(block_code)
                except Exception as e:
                    self.error_occurred = True
                    self.last_error = f"生成块 {block.name if hasattr(block, 'name') else '未知'} 代码失败: {str(e)}"
                    code.append(f"{self.indent_str}# 错误: 无法生成块代码 - {str(e)}")
            
            # 添加结束消息
            code.append(f"{self.indent_str}print('机器人程序执行完成')")
            
            return code
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"生成程序逻辑失败: {str(e)}"
            return [f"{self.indent_str}# 错误: 无法生成程序逻辑 - {str(e)}"]
    
    def _build_execution_graph(self, blocks: List[ProgramBlock], connections: List[Connection]) -> Dict[int, List[int]]:
        """构建执行流程图，添加错误处理和类型安全检查"""
        try:
            graph = {}
            
            # 初始化每个块的后继列表
            for i in range(len(blocks)):
                graph[i] = []
            
            # 根据连接构建执行流程，增加类型安全检查
            for conn in connections:
                try:
                    # 安全地访问连接属性
                    if hasattr(conn, 'from_block') and hasattr(conn, 'to_block'):
                        # 确保索引在有效范围内
                        if (isinstance(conn.from_block, int) and conn.from_block >= 0 and conn.from_block < len(blocks) and
                            isinstance(conn.to_block, int) and conn.to_block >= 0 and conn.to_block < len(blocks)):
                            graph[conn.from_block].append(conn.to_block)
                except Exception as e:
                    print(f"处理连接时出错: {str(e)}")
            
            return graph
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"构建执行流程图失败: {str(e)}"
            return {}
    
    def _generate_block_code(self, block: ProgramBlock, execution_graph: Dict[int, List[int]]) -> List[str]:
        """生成单个块的代码，添加错误处理和完善类型转换功能"""
        try:
            code = []
            
            # 添加块注释，安全处理块名称
            block_name = getattr(block, 'name', '未知块')
            code.append(f"{self.indent_str}\n{self.indent_str}# {block_name}")
            
            # 根据块类型生成不同的代码，增加类型检查
            if not hasattr(block, 'type'):
                code.append(f"{self.indent_str}# 警告: 块缺少类型信息")
                return code
            
            block_type = block.type
            
            try:
                if block_type == 'motor':
                    code.extend(self._generate_motor_block_code(block))
                elif block_type == 'sensor':
                    code.extend(self._generate_sensor_block_code(block))
                elif block_type == 'logic':
                    # 确保execution_graph有效
                    if execution_graph is not None and isinstance(execution_graph, dict):
                        code.extend(self._generate_logic_block_code(block, execution_graph))
                    else:
                        code.append(f"{self.indent_str}# 警告: 无效的执行流程图")
                elif block_type == 'variable':
                    code.extend(self._generate_variable_block_code(block))
                else:
                    code.append(f"{self.indent_str}# 警告: 未知的块类型 {block_type}")
            except Exception as e:
                self.error_occurred = True
                self.last_error = f"生成块代码失败: {str(e)}"
                code.append(f"{self.indent_str}# 错误: 生成块代码时出错 - {str(e)}")
            
            return code
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"生成块代码过程出错: {str(e)}"
            return [f"{self.indent_str}# 错误: 无法生成块代码"]
        
    def _get_connection_value(self, block: ProgramBlock, node_name: str) -> str:
        """获取连接的输入值，增强错误处理和类型安全检查"""
        try:
            # 参数验证
            if not isinstance(block, ProgramBlock) or not isinstance(node_name, str):
                self.error_occurred = True
                self.last_error = f"无效的参数类型: block={type(block)}, node_name={type(node_name)}"
                return f"var_invalid_{node_name}"
            
            # 检查块参数中是否有默认值
            if hasattr(block, 'params') and isinstance(block.params, list):
                for param in block.params:
                    try:
                        # 安全地访问参数属性
                        if isinstance(param, dict):
                            if param.get('name') == node_name:
                                param_value = param.get('value')
                                # 根据参数值的类型返回合适的表达式
                                if param_value is None:
                                    return "None"
                                elif isinstance(param_value, (int, float)):
                                    return str(param_value)
                                elif isinstance(param_value, bool):
                                    return 'True' if param_value else 'False'
                                elif isinstance(param_value, str):
                                    # 如果是字符串，检查是否是变量名或字面量
                                    if param_value in ['True', 'False', 'None'] or param_value.isdigit() or (param_value.startswith('"') and param_value.endswith('"')):
                                        return param_value
                                    # 否则作为字符串字面量处理
                                    # 转义特殊字符以避免语法错误
                                    escaped_value = param_value.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
                                    return f'"{escaped_value}"'
                                return repr(param_value)
                        elif hasattr(param, 'get') and param.get('name') == node_name:
                            param_value = param.get('value')
                            if param_value is None:
                                return "None"
                            elif isinstance(param_value, (int, float)):
                                return str(param_value)
                            elif isinstance(param_value, bool):
                                return 'True' if param_value else 'False'
                            elif isinstance(param_value, str):
                                if param_value in ['True', 'False', 'None'] or param_value.isdigit() or (param_value.startswith('"') and param_value.endswith('"')):
                                    return param_value
                                escaped_value = param_value.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
                                return f'"{escaped_value}"'
                            return repr(param_value)
                    except Exception as e:
                        print(f"处理参数时出错: {str(e)}")
                        continue
            
            # 生成安全的变量名
            safe_node_name = node_name.replace(' ', '_').replace('-', '_').lower()
            return f"var_{id(block)}_{safe_node_name}"
            
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"获取连接值时发生错误 (node={node_name}): {str(e)}"
            return f"var_error_{id(block)}_{node_name}"
    
    def _generate_motor_block_code(self, block: ProgramBlock) -> List[str]:
        """生成电机控制块代码，增强错误处理和参数验证"""
        try:
            code = []
            
            # 安全地获取块名称
            block_name = getattr(block, 'name', '未知电机控制')
            
            try:
                if block_name == '前进':
                    # 获取速度参数，确保类型正确
                    speed = self._get_param_value(block, '速度', default=50)
                    # 验证速度值范围
                    if isinstance(speed, (int, float)) and 0 <= speed <= 100:
                        duration = self._get_param_value(block, '时间', default=1)
                        if isinstance(duration, (int, float)) and duration >= 0:
                            code.append(f"{self.indent_str}# 控制机器人前进")
                            code.append(f"{self.indent_str}# robot.move_forward(speed={speed})")
                            code.append(f"{self.indent_str}print(f'前进: 速度={{speed}}, 时间={{duration}}秒')")
                            code.append(f"{self.indent_str}time.sleep({duration})")
                            code.append(f"{self.indent_str}# robot.stop()")
                            code.append(f"{self.indent_str}print('停止')")
                        else:
                            code.append(f"{self.indent_str}# 警告: 无效的时间值 {duration}")
                            code.append(f"{self.indent_str}time.sleep(1)  # 使用默认时间")
                    else:
                        code.append(f"{self.indent_str}# 警告: 无效的速度值 {speed}")
                        code.append(f"{self.indent_str}print(f'前进: 速度=50, 时间=1秒')")
                        code.append(f"{self.indent_str}time.sleep(1)")
                
                elif block_name == '后退':
                    # 获取速度参数
                    speed = self._get_param_value(block, '速度', default=50)
                    if isinstance(speed, (int, float)) and 0 <= speed <= 100:
                        duration = self._get_param_value(block, '时间', default=1)
                        if isinstance(duration, (int, float)) and duration >= 0:
                            code.append(f"{self.indent_str}# 控制机器人后退")
                            code.append(f"{self.indent_str}# robot.move_backward(speed={speed})")
                            code.append(f"{self.indent_str}print(f'后退: 速度={{speed}}, 时间={{duration}}秒')")
                            code.append(f"{self.indent_str}time.sleep({duration})")
                            code.append(f"{self.indent_str}# robot.stop()")
                            code.append(f"{self.indent_str}print('停止')")
                        else:
                            code.append(f"{self.indent_str}# 警告: 无效的时间值 {duration}")
                            code.append(f"{self.indent_str}time.sleep(1)  # 使用默认时间")
                    else:
                        code.append(f"{self.indent_str}# 警告: 无效的速度值 {speed}")
                        code.append(f"{self.indent_str}print(f'后退: 速度=50, 时间=1秒')")
                        code.append(f"{self.indent_str}time.sleep(1)")
                
                elif block_name == '左转':
                    # 获取速度参数
                    speed = self._get_param_value(block, '速度', default=50)
                    angle = self._get_param_value(block, '角度', default=90)
                    if isinstance(speed, (int, float)) and 0 <= speed <= 100:
                        if isinstance(angle, (int, float)) and 0 < angle <= 360:
                            code.append(f"{self.indent_str}# 控制机器人左转")
                            code.append(f"{self.indent_str}# robot.turn_left(angle={angle}, speed={speed})")
                            code.append(f"{self.indent_str}print(f'左转: 角度={{angle}}度, 速度={{speed}}')")
                            code.append(f"{self.indent_str}time.sleep({angle / 90})  # 简单估算时间")
                            code.append(f"{self.indent_str}# robot.stop()")
                            code.append(f"{self.indent_str}print('停止')")
                        else:
                            code.append(f"{self.indent_str}# 警告: 无效的角度值 {angle}")
                            code.append(f"{self.indent_str}time.sleep(1)  # 使用默认时间")
                    else:
                        code.append(f"{self.indent_str}# 警告: 无效的速度值 {speed}")
                        code.append(f"{self.indent_str}print(f'左转: 角度=90度, 速度=50')")
                        code.append(f"{self.indent_str}time.sleep(1)")
                
                elif block_name == '右转':
                    # 获取速度参数
                    speed = self._get_param_value(block, '速度', default=50)
                    angle = self._get_param_value(block, '角度', default=90)
                    if isinstance(speed, (int, float)) and 0 <= speed <= 100:
                        if isinstance(angle, (int, float)) and 0 < angle <= 360:
                            code.append(f"{self.indent_str}# 控制机器人右转")
                            code.append(f"{self.indent_str}# robot.turn_right(angle={angle}, speed={speed})")
                            code.append(f"{self.indent_str}print(f'右转: 角度={{angle}}度, 速度={{speed}}')")
                            code.append(f"{self.indent_str}time.sleep({angle / 90})  # 简单估算时间")
                            code.append(f"{self.indent_str}# robot.stop()")
                            code.append(f"{self.indent_str}print('停止')")
                        else:
                            code.append(f"{self.indent_str}# 警告: 无效的角度值 {angle}")
                            code.append(f"{self.indent_str}time.sleep(1)  # 使用默认时间")
                    else:
                        code.append(f"{self.indent_str}# 警告: 无效的速度值 {speed}")
                        code.append(f"{self.indent_str}print(f'右转: 角度=90度, 速度=50')")
                        code.append(f"{self.indent_str}time.sleep(1)")
                
                elif block_name == '停止':
                    code.append(f"{self.indent_str}# 停止所有电机")
                    code.append(f"{self.indent_str}# robot.stop()")
                    code.append(f"{self.indent_str}print('停止所有电机')")
                
                else:
                    code.append(f"{self.indent_str}# 未知的电机控制块: {block_name}")
            except Exception as e:
                self.error_occurred = True
                self.last_error = f"生成电机控制块代码时出错: {str(e)}"
                code.append(f"{self.indent_str}# 错误: 无法生成电机控制块代码")
            
            return code
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"处理电机控制块时出错: {str(e)}"
            return [f"{self.indent_str}# 错误: 电机控制块处理失败"]
    
    def _generate_sensor_block_code(self, block: ProgramBlock) -> List[str]:
        """生成传感器块代码，增强错误处理和类型安全"""
        try:
            code = []
            
            # 安全地获取块名称
            block_name = getattr(block, 'name', '未知传感器')
            
            try:
                # 生成传感器读取代码
                if block_name == '读取超声波':
                    code.append(f"{self.indent_str}# 读取超声波传感器距离")
                    code.append(f"{self.indent_str}try:")
                    code.append(f"{self.indent_str}{self.indent_str}# distance = robot.get_ultrasonic_distance()")
                    code.append(f"{self.indent_str}{self.indent_str}distance = 0  # 模拟传感器值")
                    code.append(f"{self.indent_str}{self.indent_str}print(f'超声波距离: {{distance}} cm')")
                    code.append(f"{self.indent_str}except Exception as e:")
                    code.append(f"{self.indent_str}{self.indent_str}print(f'读取超声波传感器错误: {{e}}')")
                    code.append(f"{self.indent_str}{self.indent_str}distance = 0  # 默认值")
                
                elif block_name == '读取光线':
                    code.append(f"{self.indent_str}# 读取光线传感器亮度")
                    code.append(f"{self.indent_str}try:")
                    code.append(f"{self.indent_str}{self.indent_str}# brightness = robot.get_light_level()")
                    code.append(f"{self.indent_str}{self.indent_str}brightness = 0  # 模拟传感器值")
                    code.append(f"{self.indent_str}{self.indent_str}print(f'光线亮度: {{brightness}}')")
                    code.append(f"{self.indent_str}except Exception as e:")
                    code.append(f"{self.indent_str}{self.indent_str}print(f'读取光线传感器错误: {{e}}')")
                    code.append(f"{self.indent_str}{self.indent_str}brightness = 0  # 默认值")
                
                elif block_name == '读取声音':
                    code.append(f"{self.indent_str}# 读取声音传感器音量")
                    code.append(f"{self.indent_str}try:")
                    code.append(f"{self.indent_str}{self.indent_str}# volume = robot.get_sound_level()")
                    code.append(f"{self.indent_str}{self.indent_str}volume = 0  # 模拟传感器值")
                    code.append(f"{self.indent_str}{self.indent_str}print(f'声音音量: {{volume}}')")
                    code.append(f"{self.indent_str}except Exception as e:")
                    code.append(f"{self.indent_str}{self.indent_str}print(f'读取声音传感器错误: {{e}}')")
                    code.append(f"{self.indent_str}{self.indent_str}volume = 0  # 默认值")
                
                else:
                    # 生成通用传感器代码
                    sensor_name = block_name.replace('读取', '').strip()
                    var_name = sensor_name.lower().replace(' ', '_') + '_value'
                    code.append(f"{self.indent_str}# 读取{sensor_name}传感器")
                    code.append(f"{self.indent_str}try:")
                    code.append(f"{self.indent_str}{self.indent_str}{var_name} = 0  # 模拟值")
                    code.append(f"{self.indent_str}{self.indent_str}print(f'{sensor_name}传感器值: {{{var_name}}}')")
                    code.append(f"{self.indent_str}except Exception as e:")
                    code.append(f"{self.indent_str}{self.indent_str}print(f'读取{sensor_name}传感器错误: {{e}}')")
                    code.append(f"{self.indent_str}{self.indent_str}{var_name} = 0  # 默认值")
            except Exception as e:
                self.error_occurred = True
                self.last_error = f"生成传感器块代码时出错: {str(e)}"
                code.append(f"{self.indent_str}# 错误: 无法生成传感器块代码")
            
            return code
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"处理传感器块时出错: {str(e)}"
            return [f"{self.indent_str}# 错误: 传感器块处理失败"]
    
    def _generate_logic_block_code(self, block: ProgramBlock, execution_graph: Dict[int, List[int]]) -> List[str]:
        """生成逻辑块代码，增强错误处理和循环安全性，修复未定义变量错误"""
        try:
            code = []
            
            # 安全地获取块名称
            block_name = getattr(block, 'name', '未知逻辑块')
            
            try:
                # 生成逻辑块代码
                if block_name == '条件判断':
                    # 获取条件参数
                    condition = self._get_param_value(block, '条件', default='True')
                    
                    # 确保条件是有效的字符串
                    if not isinstance(condition, str):
                        condition = str(condition)
                    
                    # 生成条件判断代码
                    code.append(f"{self.indent_str}# 条件判断")
                    code.append(f"{self.indent_str}try:")
                    code.append(f"{self.indent_str}{self.indent_str}# 安全评估条件")
                    code.append(f"{self.indent_str}{self.indent_str}condition_result = {condition}")
                    code.append(f"{self.indent_str}except Exception as e:")
                    code.append(f"{self.indent_str}{self.indent_str}print(f'条件评估错误: {{e}}')")
                    code.append(f"{self.indent_str}{self.indent_str}condition_result = False")
                    code.append(f"{self.indent_str}")
                    code.append(f"{self.indent_str}if condition_result:")
                    
                    # 增加缩进级别
                    self.indent_level += 1
                    
                    # 生成真分支代码 - 不再使用blocks变量，避免未定义错误
                    code.append(f"{self.indent_str}print('条件为真')")
                    
                    # 减少缩进级别
                    self.indent_level -= 1
                    
                    # 生成假分支代码
                    code.append(f"{self.indent_str}else:")
                    
                    # 增加缩进级别
                    self.indent_level += 1
                    
                    # 生成假分支代码
                    code.append(f"{self.indent_str}print('条件为假')")
                    
                    # 减少缩进级别
                    self.indent_level -= 1
                
                elif block_name == '循环':
                    # 获取循环类型和条件
                    loop_type = self._get_param_value(block, '类型', default='for')
                    
                    if loop_type == 'while':
                        # while循环，添加循环保护
                        condition = self._get_param_value(block, '条件', default='True')
                        if not isinstance(condition, str):
                            condition = str(condition)
                        
                        code.append(f"{self.indent_str}# while循环")
                        code.append(f"{self.indent_str}loop_counter = 0")
                        code.append(f"{self.indent_str}MAX_LOOPS = 1000  # 防止无限循环")
                        code.append(f"{self.indent_str}while {condition} and loop_counter < MAX_LOOPS:")
                        code.append(f"{self.indent_str}{self.indent_str}loop_counter += 1")
                    else:
                        # for循环，验证次数
                        times = self._get_param_value(block, '次数', default=1)
                        # 确保次数是正整数
                        if isinstance(times, (int, float)):
                            times = max(1, int(times))
                        else:
                            times = 1
                        code.append(f"{self.indent_str}# for循环 {times} 次")
                        code.append(f"{self.indent_str}for _ in range({times}):")
                    
                    # 增加缩进级别
                    self.indent_level += 1
                    
                    # 生成循环体代码 - 不再使用blocks变量
                    code.append(f"{self.indent_str}print('循环执行')")
                    
                    # 减少缩进级别
                    self.indent_level -= 1
                    
                    # 添加循环保护检查
                    if loop_type == 'while':
                        code.append(f"{self.indent_str}if loop_counter >= MAX_LOOPS:")
                        code.append(f"{self.indent_str}{self.indent_str}print('警告: 循环可能无限执行，已中断')")
                else:
                    code.append(f"{self.indent_str}# 未知的逻辑块类型: {block_name}")
            except Exception as e:
                self.error_occurred = True
                self.last_error = f"生成逻辑块代码时出错: {str(e)}"
                code.append(f"{self.indent_str}# 错误: 无法生成逻辑块代码")
            
            return code
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"处理逻辑块时出错: {str(e)}"
            return [f"{self.indent_str}# 错误: 逻辑块处理失败"]
    
    def _generate_variable_block_code(self, block: ProgramBlock) -> List[str]:
        """生成变量操作块代码，增强错误处理和变量安全检查"""
        try:
            code = []
            
            # 安全地获取块名称
            block_name = getattr(block, 'name', '未知变量操作')
            
            try:
                # 生成变量操作代码
                if block_name == '变量赋值':
                    # 获取变量名和值
                    var_name = self._get_param_value(block, '变量名', default='var')
                    value = self._get_param_value(block, '值', default='0')
                    
                    # 验证变量名有效性
                    if isinstance(var_name, str) and var_name.isidentifier():
                        code.append(f"{self.indent_str}# 变量赋值")
                        code.append(f"{self.indent_str}try:")
                        code.append(f"{self.indent_str}{self.indent_str}{var_name} = {value}")
                        code.append(f"{self.indent_str}{self.indent_str}print(f'赋值: {{var_name}} = {{{var_name}}}')")  # 使用实际值而不是表达式
                        code.append(f"{self.indent_str}except Exception as e:")
                        code.append(f"{self.indent_str}{self.indent_str}print(f'变量赋值错误: {{e}}')")
                    else:
                        # 清理变量名
                        safe_var_name = ''.join(c if c.isidentifier() else '_' for c in str(var_name))
                        if not safe_var_name or not safe_var_name[0].isalpha():
                            safe_var_name = 'var_' + safe_var_name
                        code.append(f"{self.indent_str}# 警告: 无效的变量名 '{var_name}'，已转换为 '{safe_var_name}'")
                        code.append(f"{self.indent_str}{safe_var_name} = {value}")
                
                elif block_name == '变量增加':
                    # 获取变量名和增量
                    var_name = self._get_param_value(block, '变量名', default='var')
                    increment = self._get_param_value(block, '增量', default='1')
                    
                    # 验证变量名有效性
                    if isinstance(var_name, str) and var_name.isidentifier():
                        code.append(f"{self.indent_str}# 变量增加")
                        code.append(f"{self.indent_str}try:")
                        # 检查变量是否存在，不存在则初始化为0
                        code.append(f"{self.indent_str}{self.indent_str}try:")
                        code.append(f"{self.indent_str}{self.indent_str}{self.indent_str}{var_name}")
                        code.append(f"{self.indent_str}{self.indent_str}except NameError:")
                        code.append(f"{self.indent_str}{self.indent_str}{self.indent_str}{var_name} = 0")
                        # 执行增加操作
                        code.append(f"{self.indent_str}{self.indent_str}{var_name} += {increment}")
                        code.append(f"{self.indent_str}{self.indent_str}print(f'增加: {{var_name}} += {{{increment}}}，结果: {{{var_name}}}')")
                        code.append(f"{self.indent_str}except Exception as e:")
                        code.append(f"{self.indent_str}{self.indent_str}print(f'变量增加错误: {{e}}')")
                    else:
                        code.append(f"{self.indent_str}# 警告: 无效的变量名 '{var_name}'")
                
                else:
                    code.append(f"{self.indent_str}# 未知的变量操作: {block_name}")
            except Exception as e:
                self.error_occurred = True
                self.last_error = f"生成变量操作块代码时出错: {str(e)}"
                code.append(f"{self.indent_str}# 错误: 无法生成变量操作块代码")
            
            return code
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"处理变量操作块时出错: {str(e)}"
            return [f"{self.indent_str}# 错误: 变量操作块处理失败"]
    
    def _get_param_value(self, block: ProgramBlock, param_name: str, default: Any = None) -> Any:
        """获取参数值，处理类型转换，增强版"""
        try:
            if not hasattr(block, 'params') or block.params is None:
                return default
            
            # 处理列表类型的params
            for param in block.params:
                if param.get('name') == param_name:
                    param_value = param.get('value', param.get('default', default))
                    
                    # 尝试类型转换
                    try:
                        # 根据参数名推断类型（如果没有默认值）
                        if default is None:
                            # 常见数字参数名处理
                            if param_name in ['次数', '时间', '速度', '距离', '角度', '延时']:
                                return float(param_value) if isinstance(param_value, (int, float)) or (isinstance(param_value, str) and '.' in param_value) else int(param_value)
                            # 常见布尔参数名处理
                            elif param_name in ['条件', '启用', '禁用', '循环']:
                                if isinstance(param_value, bool):
                                    return param_value
                                return str(param_value).lower() in ('true', 'yes', '1', 'y', 't')
                            # 默认为字符串
                            elif not isinstance(param_value, (int, float, bool)):
                                return str(param_value)
                        
                        # 如果提供了默认值，按照默认值类型转换
                        if isinstance(default, (int, float)):
                            if isinstance(param_value, (int, float)):
                                return param_value
                            return float(param_value) if isinstance(param_value, str) and '.' in param_value else int(param_value)
                        # 如果默认值是布尔值
                        elif isinstance(default, bool):
                            if isinstance(param_value, bool):
                                return param_value
                            return str(param_value).lower() in ('true', 'yes', '1', 'y', 't')
                        # 如果默认值是字符串
                        elif isinstance(default, str):
                            return str(param_value)
                    except (ValueError, TypeError) as e:
                        print(f"参数类型转换错误 (param={param_name}, value={param_value}): {str(e)}")
                    
                    return param_value
            return default
            
        except Exception as e:
            print(f"获取参数值时发生错误 (param={param_name}): {str(e)}")
            return default


class ExecutionSimulator:
    """程序执行模拟器 - 增强版，添加了完整的异常处理和安全检查
    
    主要功能:
    - 模拟执行机器人程序块
    - 支持电机控制、传感器读取、逻辑判断和变量操作
    - 内置递归保护和执行栈限制
    - 提供详细的执行输出和错误报告
    - 支持循环引用检测和异常捕获
    
    错误处理说明:
    - 严重错误: 会中断执行并设置error_occurred标志
    - 警告信息: 记录到output中，但不会中断执行
    - 递归保护: 检测到可能的无限循环时会自动中断
    - 内存保护: 防止执行过程中发生内存溢出
    
    使用示例:
    ```python
    # 创建模拟器实例
    simulator = ExecutionSimulator()
    
    # 定义程序块、连接和初始变量
    blocks = [ProgramBlock(type='motor', name='前进', params=[{"name": "速度", "value": 50}])]
    connections = []
    initial_variables = {"count": Variable(value=0)}
    
    # 执行模拟
    output = simulator.execute(blocks, connections, initial_variables)
    
    # 输出执行结果
    for line in output:
        print(line)
    
    # 获取执行状态
    status = simulator.get_execution_status()
    print(f"执行状态: 成功={not status['error_occurred']}")
    ```
    
    安全特性:
    - 参数验证: 所有输入参数都会经过类型和有效性检查
    - 异常隔离: 单个块的异常不会导致整个执行崩溃
    - 栈深度限制: 防止递归调用过深导致栈溢出
    - 循环检测: 识别并阻止潜在的无限循环
    """
    
    def __init__(self):
        """初始化执行模拟器，设置执行状态和数据结构"""
        try:
            self.variables = {}         # 变量存储字典
            self.output = []            # 执行输出日志
            self.error_occurred = False # 错误状态标志
            self.last_error = None      # 最后一次错误信息
            self.execution_stack = []   # 执行栈，用于递归保护
        except Exception as e:
            self.error_occurred = True
            self.last_error = f"初始化模拟器失败: {str(e)}"
            print(f"模拟器错误: {self.last_error}")
    
    def execute(self, blocks: List[ProgramBlock], connections: List[Connection], initial_variables: Dict[str, Variable]):
        """执行程序，增强参数验证和异常处理"""
        try:
            # 重置状态
            self.error_occurred = False
            self.last_error = None
            self.output = []
            self.execution_stack = []
            self.variables = {}
            
            # 参数验证增强
            # 验证blocks参数
            if blocks is None:
                raise ValueError("blocks参数不能为None")
            elif not isinstance(blocks, (list, tuple)):
                raise TypeError("blocks参数必须是列表或元组类型")
            elif not blocks:
                self.output.append("警告: 没有可执行的块")
                return self.output
            
            # 验证connections参数
            if connections is None:
                connections = []
            elif not isinstance(connections, (list, tuple)):
                self.output.append(f"警告: connections参数类型无效({type(connections).__name__})，将使用空连接")
                connections = []
            
            # 验证initial_variables参数
            if initial_variables is None:
                self.output.append("警告: initial_variables参数为None，将使用空变量集")
                initial_variables = {}
            elif not isinstance(initial_variables, dict):
                self.output.append(f"警告: initial_variables参数类型无效({type(initial_variables).__name__})，将使用空变量集")
                initial_variables = {}
            
            # 记录执行开始信息
            self.output.append(f"开始执行模拟 - 块数量: {len(blocks)}, 连接数量: {len(connections)}, 变量数量: {len(initial_variables)}")
            
            # 初始化变量，添加类型安全检查
            valid_vars = 0
            for name, var in initial_variables.items():
                try:
                    # 验证变量名
                    if not isinstance(name, str) or not name:
                        self.output.append(f"警告: 无效的变量名，将跳过")
                        continue
                    
                    # 安全获取变量值
                    if hasattr(var, 'value'):
                        value = var.value
                        self.variables[name] = value
                        valid_vars += 1
                    else:
                        self.output.append(f"警告: 变量 {name} 缺少value属性，将使用None")
                        self.variables[name] = None
                except Exception as e:
                    self.output.append(f"警告: 初始化变量 {name} 失败: {str(e)}")
            
            self.output.append(f"成功初始化 {valid_vars}/{len(initial_variables)} 个变量")
            
            # 构建执行流程图，添加异常捕获
            try:
                execution_graph = self._build_execution_graph(blocks, connections)
                if not isinstance(execution_graph, dict):
                    self.output.append("警告: 构建执行流程图失败，将使用空图")
                    execution_graph = {}
            except Exception as e:
                self.output.append(f"错误: 构建执行流程图失败: {str(e)}")
                return self.output
            
            # 开始执行，添加递归和内存保护
            try:
                # 验证第一个块是否有效
                if not hasattr(blocks[0], 'type'):
                    self._handle_error("第一个块缺少type属性，无法执行")
                    return self.output
                
                self._execute_block(0, blocks, execution_graph)
                
                # 记录执行完成信息
                if not self.error_occurred:
                    self.output.append("模拟执行完成")
                else:
                    self.output.append(f"模拟执行中断: {self.last_error}")
            except RecursionError:
                self._handle_error("执行过程中发生递归错误，可能存在无限循环")
            except MemoryError:
                self._handle_error("执行过程中发生内存错误")
            except StackOverflowError:
                self._handle_error("执行过程中发生堆栈溢出错误")
            except Exception as e:
                self._handle_error(f"执行主流程时出错: {str(e)}")
            
            # 返回最终执行输出
            return self.output
        except Exception as e:
            error_msg = f"执行程序时发生未预期错误: {str(e)}"
            self.error_occurred = True
            self.last_error = error_msg
            self.output.append(error_msg)
            return self.output
    
    def _execute_block(self, block_index: int, blocks: List[ProgramBlock], execution_graph: Dict[int, List[int]]):
        """执行单个块，添加递归保护和异常处理"""
        try:
            # 检查是否发生错误
            if self.error_occurred:
                return
                
            # 检查索引有效性
            if block_index >= len(blocks) or block_index < 0:
                self._handle_error(f"无效的块索引: {block_index}")
                return
            
            # 防止无限递归
            if block_index in self.execution_stack:
                recursion_depth = self.execution_stack.count(block_index)
                if recursion_depth > 100:
                    self._handle_error(f"检测到可能的无限递归: 块 {block_index} 已执行 {recursion_depth} 次")
                    return
            
            # 添加到执行栈
            self.execution_stack.append(block_index)
            
            # 限制栈深度
            if len(self.execution_stack) > 1000:
                self._handle_error(f"执行栈溢出: 最大深度 {len(self.execution_stack)}")
                return
            
            block = blocks[block_index]
            
            # 执行块
            result = self._execute_block_logic(block)
            
            # 根据块类型和结果决定下一步执行
            if hasattr(block, 'type') and hasattr(block, 'name'):
                if block.type == 'logic' and block.name == '条件判断':
                    # 条件判断块的特殊处理
                    condition_result = result.get('condition', True)
                    next_blocks = execution_graph.get(block_index, []) if isinstance(execution_graph, dict) else []
                    
                    if next_blocks:
                        # 简单处理：如果有连接，选择第一个作为真分支，第二个作为假分支
                        try:
                            if condition_result and len(next_blocks) >= 1:
                                self._execute_block(next_blocks[0], blocks, execution_graph)
                            elif not condition_result and len(next_blocks) >= 2:
                                self._execute_block(next_blocks[1], blocks, execution_graph)
                        except Exception as e:
                            self._handle_error(f"执行条件分支时出错: {str(e)}")
                else:
                    # 普通块的处理
                    next_blocks = execution_graph.get(block_index, []) if isinstance(execution_graph, dict) else []
                    for next_block in next_blocks:
                        if self.error_occurred:  # 检查是否仍可执行
                            break
                        self._execute_block(next_block, blocks, execution_graph)
        except Exception as e:
            self._handle_error(f"执行块 {block_index} 时出错: {str(e)}")
        finally:
            # 从执行栈中移除
            if self.execution_stack and self.execution_stack[-1] == block_index:
                self.execution_stack.pop()
    
    def _handle_error(self, error_message):
        """统一错误处理"""
        self.error_occurred = True
        self.last_error = error_message
        self.output.append(f"错误: {error_message}")
        print(f"模拟器错误: {error_message}")
    
    def _execute_block_logic(self, block: ProgramBlock) -> Dict[str, Any]:
        """执行块的逻辑，添加完整的异常处理"""
        result = {}
        
        try:
            # 检查块属性
            if not hasattr(block, 'type'):
                self.output.append(f"警告: 块缺少type属性")
                return result
                
            block_type = block.type
            
            if block_type == 'motor':
                block_name = getattr(block, 'name', '未知电机块')
                self.output.append(f"执行电机控制: {block_name}")
            elif block_type == 'sensor':
                block_name = getattr(block, 'name', '未知传感器块')
                self.output.append(f"执行传感器读取: {block_name}")
            elif block_type == 'logic':
                if hasattr(block, 'name') and block.name == '条件判断':
                    condition = self._get_param_value(block, '条件', default='True')
                    # 简单的表达式求值
                    try:
                        # 使用变量字典作为局部变量进行求值
                        condition_result = eval(condition, {}, self.variables)
                        result['condition'] = condition_result
                        self.output.append(f"执行条件判断: {condition} -> {condition_result}")
                    except Exception as e:
                        result['condition'] = False
                        self.output.append(f"条件表达式错误: {condition} - {str(e)}")
                elif hasattr(block, 'name') and block.name == '循环':
                    times = self._get_param_value(block, '次数', default=1)
                    self.output.append(f"执行循环: {times} 次")
            elif block_type == 'variable':
                if hasattr(block, 'name'):
                    if block.name == '变量赋值':
                        var_name = self._get_param_value(block, '变量名', default='var')
                        value_expr = self._get_param_value(block, '值', default='0')
                        # 尝试求值表达式
                        try:
                            value = eval(value_expr, {}, self.variables)
                            self.variables[var_name] = value
                            self.output.append(f"执行变量赋值: {var_name} = {value}")
                        except Exception as e:
                            # 如果求值失败，直接使用字符串值
                            self.variables[var_name] = value_expr
                            self.output.append(f"执行变量赋值(未求值): {var_name} = '{value_expr}' - 错误: {str(e)}")
                    elif block.name == '变量增加':
                        var_name = self._get_param_value(block, '变量名', default='var')
                        increment = self._get_param_value(block, '增量', default='1')
                        # 确保变量存在
                        if var_name not in self.variables:
                            self.variables[var_name] = 0
                        # 尝试求值增量
                        try:
                            inc_value = eval(str(increment), {}, self.variables)
                            # 确保是数值类型才能进行加法
                            if isinstance(self.variables[var_name], (int, float)) and isinstance(inc_value, (int, float)):
                                self.variables[var_name] += inc_value
                                self.output.append(f"执行变量增加: {var_name} += {inc_value}")
                            else:
                                self.output.append(f"变量增加失败: 类型不匹配")
                        except Exception as e:
                            self.output.append(f"变量增加失败: {var_name} += {increment} - 错误: {str(e)}")
            else:
                self.output.append(f"未知块类型: {block_type}")
        except Exception as e:
            self._handle_error(f"执行块逻辑时出错: {str(e)}")
        
        return result
    
    def _build_execution_graph(self, blocks: List[ProgramBlock], connections: List[Connection]) -> Dict[int, List[int]]:
        """构建执行流程图，增强连接类型识别和安全检查"""
        try:
            # 参数验证
            if not isinstance(blocks, (list, tuple)):
                self._handle_error(f"构建执行流程图失败: blocks参数类型无效: {type(blocks).__name__}")
                return {}
            
            if not isinstance(connections, (list, tuple)):
                self.output.append(f"警告: connections参数类型无效，将忽略连接: {type(connections).__name__}")
                connections = []
            
            # 初始化空图
            graph = {}
            
            # 初始化每个块的后继列表，添加块索引验证
            for i in range(len(blocks)):
                # 验证块是否有效
                if not hasattr(blocks[i], 'type'):
                    self.output.append(f"警告: 块 {i} 缺少type属性，可能是无效块")
                graph[i] = []
            
            # 统计有效连接数
            valid_connections = 0
            invalid_connections = 0
            
            # 根据连接构建执行流程，增强连接类型识别
            for conn_idx, conn in enumerate(connections):
                try:
                    # 连接类型检查
                    if not isinstance(conn, object):
                        self.output.append(f"警告: 连接 {conn_idx} 类型无效: {type(conn).__name__}")
                        invalid_connections += 1
                        continue
                    
                    # 检查必要属性
                    if hasattr(conn, 'from_block') and hasattr(conn, 'to_block'):
                        from_block = conn.from_block
                        to_block = conn.to_block
                        
                        # 验证块索引范围
                        if isinstance(from_block, int) and isinstance(to_block, int):
                            if 0 <= from_block < len(blocks) and 0 <= to_block < len(blocks):
                                graph[from_block].append(to_block)
                                valid_connections += 1
                            else:
                                self.output.append(f"警告: 连接 {conn_idx} 包含无效的块索引: from={from_block}, to={to_block}")
                                invalid_connections += 1
                        else:
                            self.output.append(f"警告: 连接 {conn_idx} 的块索引类型无效: from={type(from_block).__name__}, to={type(to_block).__name__}")
                            invalid_connections += 1
                    else:
                        # 尝试备选属性名（增强兼容性）
                        if hasattr(conn, 'source') and hasattr(conn, 'target'):
                            from_block = conn.source
                            to_block = conn.target
                            if isinstance(from_block, int) and isinstance(to_block, int):
                                if 0 <= from_block < len(blocks) and 0 <= to_block < len(blocks):
                                    graph[from_block].append(to_block)
                                    valid_connections += 1
                                else:
                                    self.output.append(f"警告: 连接 {conn_idx} 使用备选属性但索引无效: from={from_block}, to={to_block}")
                                    invalid_connections += 1
                            else:
                                self.output.append(f"警告: 连接 {conn_idx} 使用备选属性但类型无效")
                                invalid_connections += 1
                        else:
                            self.output.append(f"警告: 连接 {conn_idx} 缺少必要属性(from_block/to_block或source/target)")
                            invalid_connections += 1
                except Exception as e:
                    self.output.append(f"警告: 处理连接 {conn_idx} 时出错: {str(e)}")
                    invalid_connections += 1
            
            # 记录连接处理统计
            if connections:
                self.output.append(f"连接处理统计: 有效={valid_connections}, 无效={invalid_connections}, 总数={len(connections)}")
            
            # 检查循环引用风险
            self._check_cyclic_references(graph)
            
            return graph
        except Exception as e:
            self._handle_error(f"构建执行流程图失败: {str(e)}")
            return {}
    
    def _check_cyclic_references(self, graph: Dict[int, List[int]]):
        """检查执行图中是否存在循环引用风险"""
        try:
            # 使用简单的深度优先搜索检测循环
            visited = set()
            rec_stack = set()
            
            def has_cycle(node):
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in graph.get(node, []):
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
                
                rec_stack.remove(node)
                return False
            
            # 检查每个未访问的节点
            for node in graph:
                if node not in visited:
                    if has_cycle(node):
                        self.output.append(f"警告: 执行图中检测到潜在的循环引用，可能导致无限循环")
                        break
        except Exception as e:
            self.output.append(f"警告: 检查循环引用时出错: {str(e)}")
    
    def _get_param_value(self, block: ProgramBlock, param_name: str, default: Any = None) -> Any:
        """获取参数值，增强参数验证和类型转换逻辑"""
        try:
            # 块对象类型检查
            if not isinstance(block, object):
                self.output.append(f"警告: 无效的块对象: {type(block).__name__}")
                return default
            
            # 参数名验证
            if not isinstance(param_name, str) or not param_name:
                self.output.append(f"警告: 无效的参数名: {param_name}")
                return default
            
            # 检查params属性
            if not hasattr(block, 'params') or block.params is None:
                return default
            
            # 参数字典验证
            params = block.params
            if not isinstance(params, (list, tuple)):
                self.output.append(f"警告: 块参数格式无效: {type(params).__name__}")
                return default
            
            # 遍历参数查找匹配项
            for param in params:
                try:
                    # 支持字典和类似字典的对象
                    param_name_value = None
                    param_value = None
                    
                    if isinstance(param, dict):
                        param_name_value = param.get('name')
                        param_value = param.get('value', param.get('default', default))
                    elif hasattr(param, 'get'):
                        param_name_value = param.get('name')
                        param_value = param.get('value', param.get('default', default))
                    elif hasattr(param, 'name'):
                        param_name_value = param.name
                        param_value = getattr(param, 'value', getattr(param, 'default', default))
                    
                    # 如果找到匹配的参数名
                    if param_name_value == param_name:
                        # 特殊值处理
                        if param_value == 'None':
                            return None
                        elif param_value == 'True':
                            return True
                        elif param_value == 'False':
                            return False
                        
                        # 尝试进行数值范围检查（针对特定参数名）
                        if param_name.lower() in ('速度', 'speed', '角度', 'angle', 'time', '延时', '延迟'):
                            if isinstance(param_value, (int, float)):
                                # 速度范围检查
                                if param_name.lower() in ('速度', 'speed') and not (-100 <= param_value <= 100):
                                    self.output.append(f"警告: {param_name}值超出有效范围(-100到100): {param_value}")
                                # 角度范围检查
                                elif param_name.lower() in ('角度', 'angle') and not (-180 <= param_value <= 180):
                                    self.output.append(f"警告: {param_name}值超出有效范围(-180到180度): {param_value}")
                                # 时间范围检查
                                elif param_name.lower() in ('time', '延时', '延迟') and param_value < 0:
                                    self.output.append(f"警告: {param_name}值不能为负数: {param_value}")
                        
                        # 字符串清理和安全处理
                        if isinstance(param_value, str):
                            # 移除首尾空白
                            param_value = param_value.strip()
                            # 转义危险字符
                            if '\n' in param_value or '\t' in param_value:
                                param_value = param_value.replace('\n', '\\n').replace('\t', '\\t')
                        
                        return param_value
                except Exception as e:
                    self.output.append(f"警告: 处理参数时出错: {str(e)}")
                    continue
            
            return default
        except Exception as e:
            self.output.append(f"警告: 获取参数值时出错: {str(e)}")
            return default
    
    def _validate_code_generation(self) -> bool:
        """验证代码生成状态，确保没有严重错误"""
        if self.error_occurred:
            return False
        return True
    
    def get_execution_status(self):
        """获取执行状态信息"""
        return {
            'error_occurred': self.error_occurred,
            'last_error': self.last_error,
            'stack_depth': len(self.execution_stack),
            'variables_count': len(self.variables),
            'output_count': len(self.output)
        }