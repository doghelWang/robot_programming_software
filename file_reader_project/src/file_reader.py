# -*- coding: utf-8 -*-
"""
文件读取器核心模块
提供统一的文件读取接口，支持HTML/XML和Excel文件
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path

# 导入解析器模块
from .html_parser import HTMLParser
from .excel_reader import ExcelReader


class FileReader:
    """文件读取器主类"""
    
    def __init__(self):
        """初始化文件读取器"""
        self.html_parser = HTMLParser()
        self.excel_reader = ExcelReader()
        self.supported_formats = {
            '.html': 'html',
            '.htm': 'html',
            '.xml': 'xml',
            '.xlsx': 'excel',
            '.xls': 'excel'
        }
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        读取指定路径的文件
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            Dict[str, Any]: 包含文件信息和内容的字典
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 获取文件扩展名
            file_extension = Path(file_path).suffix.lower()
            
            # 检查是否支持该文件格式
            if file_extension not in self.supported_formats:
                raise ValueError(f"不支持的文件格式: {file_extension}")
            
            # 根据文件类型选择读取方法
            file_type = self.supported_formats[file_extension]
            
            if file_type == 'html' or file_type == 'xml':
                return self._read_html_xml(file_path, file_type)
            elif file_type == 'excel':
                return self._read_excel(file_path)
            else:
                raise ValueError(f"未知的文件类型: {file_type}")
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def _read_html_xml(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        读取HTML/XML文件
        
        Args:
            file_path (str): 文件路径
            file_type (str): 文件类型 ('html' 或 'xml')
            
        Returns:
            Dict[str, Any]: 文件读取结果
        """
        try:
            content = self.html_parser.parse_file(file_path)
            return {
                'success': True,
                'file_path': file_path,
                'file_type': file_type,
                'content': content,
                'metadata': {
                    'size': os.path.getsize(file_path),
                    'modified_time': os.path.getmtime(file_path)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def _read_excel(self, file_path: str) -> Dict[str, Any]:
        """
        读取Excel文件
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            Dict[str, Any]: 文件读取结果
        """
        try:
            content = self.excel_reader.read_excel(file_path)
            return {
                'success': True,
                'file_path': file_path,
                'file_type': 'excel',
                'content': content,
                'metadata': {
                    'size': os.path.getsize(file_path),
                    'modified_time': os.path.getmtime(file_path)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的文件格式列表
        
        Returns:
            List[str]: 支持的文件格式列表
        """
        return list(self.supported_formats.keys())
    
    def is_supported_format(self, file_extension: str) -> bool:
        """
        检查文件扩展名是否被支持
        
        Args:
            file_extension (str): 文件扩展名
            
        Returns:
            bool: 是否支持该格式
        """
        return file_extension.lower() in self.supported_formats


# 创建全局实例
file_reader = FileReader()
