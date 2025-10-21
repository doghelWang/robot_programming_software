#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机器人编程软件 - 主入口文件
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.main_window import RobotProgrammingApp


def main():
    """应用程序入口函数"""
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("机器人编程软件")
    app.setApplicationVersion("1.0.0")
    
    # 设置高DPI支持
    # 注意：在PyQt6中，高DPI支持是默认启用的，不需要手动设置
    
    # 创建主窗口
    window = RobotProgrammingApp()
    
    # 显示主窗口
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()