#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整机配置表到通用控制器格式转换程序
用于将整机配置表中的物料代码转换为通用控制器文档的标准格式
"""

import pandas as pd
import os
from typing import Dict, List, Any, Optional
import sys

class ConfigurationConverter:
    """配置转换器类"""
    
    def __init__(self):
        """初始化转换器"""
        self.generic_controller_data = {}
        self.machine_config_data = {}
        
    def load_generic_controller_data(self, file_path: str):
        """加载通用控制器数据"""
        try:
            # 读取通用控制器Excel文件
            excel_file = pd.ExcelFile(file_path)
            
            # 读取板子库数据
            if '板子库' in excel_file.sheet_names:
                board_library_df = pd.read_excel(file_path, sheet_name='板子库')
                self.generic_controller_data['board_library'] = board_library_df
                print(f"成功加载板子库数据，共 {len(board_library_df)} 条记录")
                
            # 读取板子库描述数据
            if '板子库描述' in excel_file.sheet_names:
                board_desc_df = pd.read_excel(file_path, sheet_name='板子库描述')
                self.generic_controller_data['board_desc'] = board_desc_df
                print(f"成功加载板子库描述数据，共 {len(board_desc_df)} 条记录")
                
            # 读取单板信息描述数据
            if '单板信息描述' in excel_file.sheet_names:
                board_info_df = pd.read_excel(file_path, sheet_name='单板信息描述')
                self.generic_controller_data['board_info'] = board_info_df
                print(f"成功加载单板信息描述数据，共 {len(board_info_df)} 条记录")
                
            print(f"成功加载通用控制器数据文件: {file_path}")
            return True
            
        except Exception as e:
            print(f"加载通用控制器数据失败: {e}")
            return False
    
    def load_machine_config_data(self, file_path: str):
        """加载整机配置数据"""
        try:
            # 读取整机配置表Excel文件
            excel_file = pd.ExcelFile(file_path)
            
            # 读取硬件属性表
            if '硬件属性表' in excel_file.sheet_names:
                hardware_df = pd.read_excel(file_path, sheet_name='硬件属性表')
                self.machine_config_data['hardware'] = hardware_df
                print(f"成功加载硬件属性表，共 {len(hardware_df)} 条记录")
                
            # 读取整机配置表
            if '整机配置表' in excel_file.sheet_names:
                config_df = pd.read_excel(file_path, sheet_name='整机配置表')
                self.machine_config_data['config'] = config_df
                print(f"成功加载整机配置表，共 {len(config_df)} 条记录")
                
            print(f"成功加载整机配置数据文件: {file_path}")
            return True
            
        except Exception as e:
            print(f"加载整机配置数据失败: {e}")
            return False
    
    def extract_material_codes(self) -> List[str]:
        """从整机配置表中提取物料代码"""
        material_codes = []
        
        if 'config' in self.machine_config_data and '整机配置表' in self.machine_config_data['config']:
            # 从整机配置表中提取物料代码
            # 根据Excel结构，物料代码可能在不同的列中
            config_df = self.machine_config_data['config']
            
            # 显示前几行数据以便分析结构
            print("整机配置表前5行数据:")
            print(config_df.head())
            print("\n整机配置表列名:", config_df.columns.tolist())
            
            # 分析整机配置表的结构
            # 从示例数据看，物料代码通常在"单板型号"列中，格式为"型号：202905466"
            # 或者在"组件型号"列中
            
            # 方法1: 查找包含"型号："的列
            for col in config_df.columns:
                col_name = str(col)
                if '型号' in col_name and '型号：' not in col_name:
                    print(f"检查列 {col_name}...")
                    # 提取该列的值
                    codes = config_df[col].dropna().astype(str).tolist()
                    for code in codes:
                        if isinstance(code, str) and '型号：' in code:
                            # 提取型号：后面的数字
                            import re
                            match = re.search(r'型号：(\d+)', code)
                            if match:
                                material_code = match.group(1)
                                material_codes.append(material_code)
                                print(f"从 {col_name} 提取到物料代码: {material_code}")
            
            # 方法2: 直接查找包含"型号："的列
            for col in config_df.columns:
                col_name = str(col)
                if '型号：' in col_name:
                    print(f"发现型号列: {col_name}")
                    codes = config_df[col].dropna().astype(str).tolist()
                    for code in codes:
                        if isinstance(code, str) and '型号：' in code:
                            import re
                            match = re.search(r'型号：(\d+)', code)
                            if match:
                                material_code = match.group(1)
                                material_codes.append(material_code)
                                print(f"从 {col_name} 提取到物料代码: {material_code}")
            
            # 方法3: 查找包含"组件型号"的列
            for col in config_df.columns:
                col_name = str(col)
                if '组件型号' in col_name:
                    print(f"发现组件型号列: {col_name}")
                    codes = config_df[col].dropna().astype(str).tolist()
                    for code in codes:
                        if isinstance(code, str) and '组件型号：' in code:
                            import re
                            match = re.search(r'组件型号：(\d+)', code)
                            if match:
                                material_code = match.group(1)
                                material_codes.append(material_code)
                                print(f"从 {col_name} 提取到物料代码: {material_code}")
            
            # 方法4: 从所有数据中查找可能的物料代码
            if not material_codes:
                print("尝试从整表数据中查找物料代码...")
                # 将所有数据展平为字符串列表
                all_data = config_df.astype(str).values.flatten()
                # 筛选出可能的物料代码（假设是9位数字）
                import re
                for item in all_data:
                    # 匹配9位数字的物料代码格式
                    if re.match(r'^\d{9}$', item.strip()):
                        material_codes.append(item.strip())
                        print(f"从数据中提取到物料代码: {item.strip()}")
                        
        # 去重并返回
        return list(set(material_codes))
    
    def convert_material_code(self, material_code: str) -> Optional[Dict[str, Any]]:
        """将物料代码转换为通用控制器格式"""
        if not self.generic_controller_data:
            print("未加载通用控制器数据")
            return None
            
        # 在通用控制器数据中查找对应的物料
        if 'board_library' in self.generic_controller_data:
            board_library_df = self.generic_controller_data['board_library']
            # 查找匹配的物料代码
            matching_rows = board_library_df[board_library_df['物料代码'] == material_code]
            
            if not matching_rows.empty:
                # 找到匹配的物料，返回详细信息
                result = {
                    'material_code': material_code,
                    'description': matching_rows.iloc[0]['完整物料描述'] if '完整物料描述' in matching_rows.columns else '',
                    'hardware_name': matching_rows.iloc[0]['硬件命名'] if '硬件命名' in matching_rows.columns else '',
                    'hardware_model': matching_rows.iloc[0]['硬件型号'] if '硬件型号' in matching_rows.columns else '',
                    'chip_platform': matching_rows.iloc[0]['芯片平台'] if '芯片平台' in matching_rows.columns else '',
                    'status': matching_rows.iloc[0]['是否已支持'] if '是否已支持' in matching_rows.columns else '',
                    'description_complete': matching_rows.iloc[0]['描述是否完成'] if '描述是否完成' in matching_rows.columns else ''
                }
                return result
                
        return None
    
    def process_all_materials(self) -> List[Dict[str, Any]]:
        """处理所有物料代码并转换为标准格式"""
        results = []
        
        # 提取整机配置表中的物料代码
        material_codes = self.extract_material_codes()
        print(f"提取到 {len(material_codes)} 个物料代码: {material_codes}")
        
        # 转换每个物料代码
        for code in material_codes:
            print(f"正在转换物料代码: {code}")
            converted = self.convert_material_code(code)
            if converted:
                results.append(converted)
            else:
                print(f"未找到物料代码 {code} 的详细信息")
                
        return results
    
    def generate_output(self, results: List[Dict[str, Any]]) -> str:
        """生成输出格式"""
        output = "物料代码转换结果:\n"
        output += "=" * 50 + "\n"
        
        if not results:
            output += "未找到匹配的物料代码\n"
        else:
            for result in results:
                output += f"物料代码: {result['material_code']}\n"
                output += f"完整描述: {result['description']}\n"
                output += f"硬件名称: {result['hardware_name']}\n"
                output += f"硬件型号: {result['hardware_model']}\n"
                output += f"芯片平台: {result['chip_platform']}\n"
                output += f"状态: {result['status']}\n"
                output += f"描述完成: {result['description_complete']}\n"
                output += "-" * 30 + "\n"
            
        return output

def main():
    """主函数"""
    print("整机配置表到通用控制器格式转换程序")
    print("=" * 50)
    
    # 创建转换器实例
    converter = ConfigurationConverter()
    
    # 加载数据文件
    generic_file = "c:/Users/wangfeifei/Downloads/通用控制器V1.2-RCU.xlsx"
    machine_file = "c:/Users/wangfeifei/Downloads/【323700510 MR-F0-50DCH-A7(M)】整机配置表-20240507.xlsx"
    
    # 检查文件是否存在
    if not os.path.exists(generic_file):
        print(f"错误: 通用控制器文件不存在 - {generic_file}")
        return
        
    if not os.path.exists(machine_file):
        print(f"错误: 整机配置文件不存在 - {machine_file}")
        return
    
    # 加载数据
    if not converter.load_generic_controller_data(generic_file):
        print("加载通用控制器数据失败")
        return
        
    if not converter.load_machine_config_data(machine_file):
        print("加载整机配置数据失败")
        return
    
    # 处理物料代码
    print("开始处理物料代码转换...")
    results = converter.process_all_materials()
    
    # 生成输出
    output = converter.generate_output(results)
    print(output)
    
    # 保存到文件
    try:
        with open('conversion_output.txt', 'w', encoding='utf-8') as f:
            f.write(output)
        print("转换完成，结果已保存到 conversion_output.txt")
    except Exception as e:
        print(f"保存文件时出错: {e}")

if __name__ == "__main__":
    main()
